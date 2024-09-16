import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

neo4j_password = os.getenv("NEO4JAURA_INSTANCE_PASSWORD")
neo4j_username = os.getenv("NEO4JAURA_INSTANCE_USERNAME")
neo4j_uri = os.getenv("NEO4JAURA_INSTANCE_URI")

# Connect to the Neo4j database
uri = neo4j_uri
username = neo4j_username
password = neo4j_password

driver = GraphDatabase.driver(uri, auth=(username, password))

def cleanup_neo4j():
    with driver.session() as session:
        session.run("MATCH (n) WHERE n:Question OR n:Body OR n:Tag OR n:Topic DETACH DELETE n")

if __name__ == "__main__":
    cleanup_neo4j()