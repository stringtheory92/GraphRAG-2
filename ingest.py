# import os
# from neo4j import GraphDatabase
# from neo4j_genai import Neo4jGenAI
# from dotenv import load_dotenv
# import ollama  

# from langchain import OpenAI, LLMChain

# load_dotenv()

# neo4j_password = os.getenv("NEO4JAURA_INSTANCE_PASSWORD")
# neo4j_username = os.getenv("NEO4JAURA_INSTANCE_URI")
# neo4j_uri = os.getenv("NEO4JAURA_INSTANCE_USERNAME")

# # Connect to the Neo4j database
# uri = neo4j_uri
# username = neo4j_username
# password = neo4j_password

# driver = GraphDatabase.driver(uri, auth=(username, password))

# def add_data_to_neo4j(data):
#     with driver.session() as session:
#         # Add Question Node and let Neo4j assign the ID
#         result = session.run(
#             "CREATE (q:Question {question: $question, date: $date}) RETURN ID(q) as qid",
#             question=data['question'], date=data['date']
#         )
#         question_id = result.single()['qid']  # Retrieve the auto-generated question ID
        
#         # Add Topic Node and associate it with the Question
#         session.run(
#             """
#             MERGE (t:Topic {name: $name})
#             WITH t
#             MATCH (q:Question) WHERE ID(q) = $qid
#             MERGE (q)-[:HAS_TOPIC]->(t)
#             """,
#             name=data['topic'], qid=question_id
#         )
        
#         # Add Body Node and let Neo4j assign the ID
#         body = data['body']
#         result = session.run(
#             "CREATE (b:Body {text: $text, date: $date}) RETURN ID(b) as bid",
#             text=body['text'], date=body['date']
#         )
#         body_id = result.single()['bid']  # Retrieve the auto-generated body ID
        
#         # Add Keywords as separate nodes and relationships to Body
#         for keyword in body['keywords']:
#             session.run(
#                 """
#                 MERGE (k:Keyword {word: $word})
#                 WITH k
#                 MATCH (b:Body) WHERE ID(b) = $bid
#                 MERGE (b)-[:HAS_KEYWORD]->(k)
#                 """,
#                 word=keyword, bid=body_id
#             )
        
#         # Create the HAS_BODY relationship between Question and Body using Neo4j-generated IDs
#         session.run(
#             """
#             MATCH (q:Question), (b:Body)
#             WHERE ID(q) = $qid AND ID(b) = $bid
#             CREATE (q)-[:HAS_BODY]->(b)
#             """,
#             qid=question_id, bid=body_id
#         )

# if __name__ == '__main__':


#     # Example Data (your settled structure)
#     # data = {
#     #     "question": "What are the benefits of a carnivore diet?",
#     #     "topic": "benefits of the carnivore diet",
#     #     "date": "2023-09-12",
#     #     "body": {
#     #         "text": "A carnivore diet focuses primarily on meat consumption...",
#     #         "date": "2023-09-12",
#     #         "keywords": ["carnivore diet", "meat", "health", "nutrition"]
#     #     }
#     # }

#     # Add the data to Neo4j
#     add_data_to_neo4j(data)


import os
from neo4j import GraphDatabase
# from neo4j_genai import Neo4jGenAI
from dotenv import load_dotenv
import ollama  
import json

# from langchain import OpenAI, LLMChain

load_dotenv()

neo4j_password = os.getenv("NEO4JAURA_INSTANCE_PASSWORD")
neo4j_username = os.getenv("NEO4JAURA_INSTANCE_USERNAME")
neo4j_uri = os.getenv("NEO4JAURA_INSTANCE_URI")

# Connect to the Neo4j database
uri = neo4j_uri
username = neo4j_username
password = neo4j_password

driver = GraphDatabase.driver(uri, auth=(username, password))

def load_json(file_path):
    """Loads the JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def add_data_to_neo4j(question_data):
    with driver.session() as session:
        for question in question_data:
            # Add Question Node
            session.run(
                "CREATE (q:Question {id: randomUUID(), text: $text, date: $date, topic: $topic})",
                text=question['question'], date=question['date'], topic=question['topic']
            )
            
            # Add Body Node
            body = question['body']
            session.run(
                "CREATE (b:Body {id: randomUUID(), text: $text, date: $date})",
                text=body['text'], date=body['date']
            )
            
            # Create the HAS_BODY relationship
            session.run(
                """
                MATCH (q:Question {text: $qtext}), (b:Body {text: $btext})
                CREATE (q)-[:HAS_BODY]->(b)
                """,
                qtext=question['question'], btext=body['text']
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
                        MATCH (b:Body {text: $btext})
                        MERGE (b)-[:HAS_TAG]->(t)
                        """,
                        word=tag, btext=body['text']
                    )

def main():
    # Load data from the manually_cleaned_data/test_ingest_data/ingest_data.json file
    file_path = "manually_cleaned_data/test_ingest_data/ingest_data.json"
    data = load_json(file_path)

    # Ingest data into Neo4j
    add_data_to_neo4j(data)

if __name__ == "__main__":
    main()
