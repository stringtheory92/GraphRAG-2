import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from google_drive_auth import authenticate_google_drive

load_dotenv()

# Neo4j Configuration
neo4j_password = os.getenv("NEO4JAURA_INSTANCE_PASSWORD")
neo4j_username = os.getenv("NEO4JAURA_INSTANCE_USERNAME")
neo4j_uri = os.getenv("NEO4JAURA_INSTANCE_URI")
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))

# Google Drive Authentication
service = authenticate_google_drive()

# Neo4j Cleanup
def cleanup_neo4j():
    """Deletes all nodes and relationships related to Question, Body, Tag, and Topic."""
    with driver.session() as session:
        session.run("MATCH (n) WHERE n:Question OR n:Body OR n:Tag OR n:Topic DETACH DELETE n")

# Get or create 'carnivore' folder in Google Drive
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

# Google Drive Cleanup
def cleanup_google_drive(service):
    """Deletes files from Google Drive inside the 'carnivore' folder that are tagged as 'api-generated'."""
    # Get the 'carnivore' folder ID
    folder_id = get_or_create_carnivore_folder(service)

    # Search for files in the 'carnivore' folder and that contain 'api-generated' in their full text
    query = f"'{folder_id}' in parents and fullText contains 'api-generated'"
    results = service.files().list(q=query, fields="files(id, name)").execute()

    files_to_delete = results.get('files', [])
    
    if not files_to_delete:
        print("No 'api-generated' files found in the 'carnivore' folder to delete.")
        return

    for file in files_to_delete:
        print(f"Deleting file: {file['name']} (ID: {file['id']})")
        service.files().delete(fileId=file['id']).execute()

# Main cleanup function
def main():
    # Clean up Neo4j database
    cleanup_neo4j()

    # Clean up Google Drive API-generated files in the 'carnivore' folder
    cleanup_google_drive(service)

if __name__ == "__main__":
    main()
