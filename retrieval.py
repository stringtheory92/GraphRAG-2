import os
from neo4j import GraphDatabase
from neo4j_genai import Neo4jGenAI
from dotenv import load_dotenv
import ollama  

from langchain import OpenAI, LLMChain

load_dotenv()

neo4j_password = os.getenv("NEO4JAURA_INSTANCE_PASSWORD")
neo4j_username = os.getenv("NEO4JAURA_INSTANCE_URI")
neo4j_uri = os.getenv("NEO4JAURA_INSTANCE_USERNAME")

# Connection to your Neo4j instance
uri = neo4j_uri
username = neo4j_username
password = neo4j_password

driver = GraphDatabase.driver(uri, auth=(username, password))

# Initialize Neo4jGenAI
genai = Neo4jGenAI(driver)

# Sample query to retrieve data
query = """
MATCH (r:Response)-[:RELATED_TO]->(t:Topic)
WHERE t.name = $topic
RETURN r.text AS response
"""

topic_name = "carnivore diet"  # Example topic
results = genai.query(query, {"topic": topic_name})

for record in results:
    print(record["response"])



    # Chain: Neo4j data -> LLM
def get_neo4j_responses_and_generate(query):
    # Query Neo4j for relevant responses
    results = genai.query(query, {"topic": topic_name})

    # Extract responses
    context = "\n".join([record["response"] for record in results])

    # Prepare a prompt for the LLM based on retrieved context
    prompt = f"""
    You are an expert in {topic_name}.
    Here are some relevant responses:
    {context}

    Based on this information, provide a detailed answer to the following question:
    """

    # Generate final answer using LLM
    final_response = llm(prompt)
    return final_response

# Example usage
response = get_neo4j_responses_and_generate(query)
print(response)
