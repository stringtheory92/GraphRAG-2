# import os
# from neo4j import GraphDatabase
# from dotenv import load_dotenv
# import json

# load_dotenv()

# neo4j_password = os.getenv("NEO4JAURA_INSTANCE_PASSWORD")
# neo4j_username = os.getenv("NEO4JAURA_INSTANCE_USERNAME")
# neo4j_uri = os.getenv("NEO4JAURA_INSTANCE_URI")

# # Connect to the Neo4j database
# uri = neo4j_uri
# username = neo4j_username
# password = neo4j_password

# driver = GraphDatabase.driver(uri, auth=(username, password))

# def load_json(file_path):
#     """Loads the JSON file."""
#     with open(file_path, 'r') as f:
#         return json.load(f)

# def add_data_to_neo4j(question_data):
#     with driver.session() as session:
#         for question in question_data:
#             # Add Question Node
#             session.run(
#                 "CREATE (q:Question {id: randomUUID(), text: $text, date: $date, topic: $topic})",
#                 text=question['question'], date=question['date'], topic=question['topic']
#             )
            
#             # Add Body Node
#             body = question['body']
#             session.run(
#                 "CREATE (b:Body {id: randomUUID(), text: $text, date: $date})",
#                 text=body['text'], date=body['date']
#             )
            
#             # Create the HAS_BODY relationship
#             session.run(
#                 """
#                 MATCH (q:Question {text: $qtext}), (b:Body {text: $btext})
#                 CREATE (q)-[:HAS_BODY]->(b)
#                 """,
#                 qtext=question['question'], btext=body['text']
#             )

#             # Add Topic Node and Relationship (if a topic exists)
#             if 'topic' in question:
#                 session.run(
#                     """
#                     MERGE (t:Topic {name: $topic})
#                     WITH t
#                     MATCH (q:Question {text: $qtext})
#                     MERGE (q)-[:HAS_TOPIC]->(t)
#                     """,
#                     topic=question['topic'], qtext=question['question']
#                 )
            
#             # Check if 'tags' exists in the body before trying to add them
#             if 'tags' in body:
#                 for tag in body['tags']:
#                     session.run(
#                         """
#                         MERGE (t:Tag {word: $word})
#                         WITH t
#                         MATCH (b:Body {text: $btext})
#                         MERGE (b)-[:HAS_TAG]->(t)
#                         """,
#                         word=tag, btext=body['text']
#                     )

# def main():
#     # Load data
#     file_path = "manually_cleaned_data/test_ingest_data/ingest_data.json"
#     data = load_json(file_path)

#     # Ingest data into Neo4j
#     add_data_to_neo4j(data)

# if __name__ == "__main__":
#     main()



import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import json
from google_drive_auth import authenticate_google_drive
from googleapiclient.http import MediaFileUpload

load_dotenv()

# Google Drive Authentication
service = authenticate_google_drive()

# Neo4j Configuration
neo4j_password = os.getenv("NEO4JAURA_INSTANCE_PASSWORD")
neo4j_username = os.getenv("NEO4JAURA_INSTANCE_USERNAME")
neo4j_uri = os.getenv("NEO4JAURA_INSTANCE_URI")

# Connect to the Neo4j database
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))

def load_json(file_path):
    """Loads the JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def get_or_create_carnivore_folder(service):
    """Get the 'carnivore' folder ID, or create it if it doesn't exist."""
    # Search for the 'carnivore' folder in Google Drive
    query = "name = 'carnivore' and mimeType = 'application/vnd.google-apps.folder'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])
    
    if folders:
        # Folder exists, return its ID
        return folders[0]['id']
    else:
        # Create the 'carnivore' folder
        file_metadata = {
            'name': 'carnivore',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def upload_to_drive(service, file_name, text_content):
    """Uploads the given text to Google Drive inside the 'carnivore' folder and tags it as 'api-generated'."""
    # Get or create the 'carnivore' folder
    folder_id = get_or_create_carnivore_folder(service)
    
    # Save the content to a temporary file
    temp_file_path = f'/tmp/{file_name}.txt'
    with open(temp_file_path, 'w') as f:
        f.write(text_content)
    
    # Define metadata for the file, including the 'api-generated' tag in the description
    file_metadata = {
        'name': file_name,
        'parents': [folder_id],  # Upload to the 'carnivore' folder
        'mimeType': 'text/plain',
        'description': 'api-generated'  # Add 'api-generated' tag to the file
    }
    
    # Upload the file to Google Drive
    media = MediaFileUpload(temp_file_path, mimetype='text/plain')
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    # Get the file ID and create a sharable link
    file_id = uploaded_file.get('id')
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}  # Make the file publicly accessible
    ).execute()
    
    # Return the sharable Google Drive link
    return f"https://drive.google.com/uc?id={file_id}"



def add_data_to_neo4j(question_data, service):
    with driver.session() as session:
        for question in question_data:
            # Add Question Node
            session.run(
                "CREATE (q:Question {id: randomUUID(), text: $text, date: $date, topic: $topic})",
                text=question['question'], date=question['date'], topic=question['topic']
            )
            
            # Upload body text to Google Drive and get the link
            body = question['body']
            file_name = f"body_text_{question['date']}"
            drive_link = upload_to_drive(service, file_name, body['text'])

            # Add Body Node with reference to Google Drive text
            session.run(
                "CREATE (b:Body {id: randomUUID(), text_link: $text_link, date: $date})",
                text_link=drive_link, date=body['date']
            )
            
            # Create the HAS_BODY relationship
            session.run(
                """
                MATCH (q:Question {text: $qtext}), (b:Body {text_link: $btext_link})
                CREATE (q)-[:HAS_BODY]->(b)
                """,
                qtext=question['question'], btext_link=drive_link
            )

            # Add Topic Node and Relationship (if a topic exists)
            if 'topic' in question:
                session.run(
                    """
                    MERGE (t:Topic {name: $topic})
                    WITH t
                    MATCH (q:Question {text: $qtext})
                    MERGE (q)-[:HAS_TOPIC]->(t)
                    """,
                    topic=question['topic'], qtext=question['question']
                )
            
            # Check if 'tags' exists in the body before trying to add them
            if 'tags' in body:
                for tag in body['tags']:
                    session.run(
                        """
                        MERGE (t:Tag {word: $word})
                        WITH t
                        MATCH (b:Body {text_link: $btext_link})
                        MERGE (b)-[:HAS_TAG]->(t)
                        """,
                        word=tag, btext_link=drive_link
                    )

def main():
    # Load data
    file_path = "manually_cleaned_data/test_ingest_data/ingest_data.json"
    data = load_json(file_path)

    # Ingest data into Neo4j
    add_data_to_neo4j(data, service)

if __name__ == "__main__":
    main()
