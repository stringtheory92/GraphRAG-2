import os
import numpy as np
import requests
from neo4j import GraphDatabase
from dotenv import load_dotenv
from google_drive_auth import authenticate_google_drive
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from langchain_huggingface import HuggingFaceEmbeddings
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neo4j Configuration
neo4j_password = os.getenv("NEO4JAURA_INSTANCE_PASSWORD")
neo4j_username = os.getenv("NEO4JAURA_INSTANCE_USERNAME")
neo4j_uri = os.getenv("NEO4JAURA_INSTANCE_URI")
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))

# Google Drive Authentication
service = authenticate_google_drive()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Initialize the Supabase client with the `vector` schema
client_options = ClientOptions(schema="vector")
client = create_client(SUPABASE_URL, SUPABASE_KEY, options=client_options)
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=client_options)

# Initialize HuggingFace Embeddings model
huggingface_embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# Function to generate query embedding using HuggingFace model
def generate_query_embedding(query):
    logger.info(f"Generating embedding for query: {query}")
    return huggingface_embed_model.embed_documents([query])[0]  # Extract the embedding for the query


# # Search Supabase for similar questions based on embedding
# def search_supabase_for_similar_questions(query_embedding, top_k=3):
#     """Searches Supabase for questions with embeddings most similar to the query embedding."""
#     try:
#         response = client.rpc("cosine_similarity_search", {"query_embedding": query_embedding, "top_k": top_k}).execute()
#         # response = supabase.rpc("cosine_similarity_search", {"query_embedding": query_embedding, "top_k": top_k}).execute()

#         if response.data:
#             logger.info(f"Found {len(response.data)} similar questions.")
#             return response.data
#         else:
#             logger.info("No similar questions found in Supabase.")
#             return []

#     except Exception as e:
#         logger.error(f"Error querying Supabase embeddings: {e}")
#         raise

def search_supabase_for_similar_questions(query_embedding, top_k=3):
    """Searches Supabase for questions with embeddings most similar to the query embedding."""
    try:
        # Call Supabase using an RPC to retrieve the similar embeddings using cosine_distance
        response = client.table("embeddings").select("*").order(f"cosine_distance(embedding, array{query_embedding})").limit(top_k).execute()
        
        logging.info(f"Retrieved {len(response.data)} similar questions from Supabase.")
        return response.data  # Return the response data (most similar questions)

    except Exception as e:
        logging.error(f"Error querying Supabase embeddings: {e}")
        raise



# Fetch metadata (topic, tags, body link) from Neo4j for a given question ID
def fetch_metadata_from_neo4j(question_id):
    """Fetches metadata (topic, tags, body link) for a given question ID from Neo4j."""
    try:
        with driver.session() as session:
            query = """
            MATCH (q:Question {id: $question_id})-[:HAS_BODY]->(b:Body)
            OPTIONAL MATCH (q)-[:HAS_TOPIC]->(t:Topic)
            OPTIONAL MATCH (b)-[:HAS_TAG]->(tag:Tag)
            RETURN q.text AS question, b.text_link AS body_link, collect(tag.word) AS tags, t.name AS topic
            """
            result = session.run(query, question_id=question_id)
            record = result.single()

            if record:
                logger.info(f"Metadata fetched for question_id: {question_id}")
                return {
                    "question": record["question"],
                    "body_link": record["body_link"],
                    "tags": record["tags"],
                    "topic": record["topic"]
                }
            else:
                logger.info(f"No metadata found for question_id: {question_id}")
                return {}

    except Exception as e:
        logger.error(f"Error fetching metadata from Neo4j: {e}")
        raise


# Fetch full body text from Google Drive using the link
def fetch_body_from_google_drive(body_link):
    """Fetches the full body text from Google Drive using the link."""
    try:
        file_id = body_link.split("id=")[-1]  # Extract the file ID from the link
        file = service.files().get(fileId=file_id, fields="id, name, mimeType").execute()

        if file and file["mimeType"] == "text/plain":
            request = service.files().get_media(fileId=file_id)
            body_text = request.execute().decode("utf-8")
            logger.info(f"Fetched body text from Google Drive for file_id: {file_id}")
            return body_text
        else:
            logger.error(f"File with ID {file_id} is not a valid text file.")
            return None

    except Exception as e:
        logger.error(f"Error fetching body text from Google Drive: {e}")
        raise


# Main retrieval function
def retrieve_similar_questions(query):
    """Main function that retrieves similar questions based on the input query."""
    try:
        # Generate embedding for the input query
        query_embedding = generate_query_embedding(query)

        # Search Supabase for similar questions
        similar_questions = search_supabase_for_similar_questions(query_embedding)

        # For each similar question, fetch metadata and full body text
        for question in similar_questions:
            question_id = question['question_id']

            # Fetch metadata from Neo4j
            metadata = fetch_metadata_from_neo4j(question_id)

            if metadata:
                logger.info(f"Question: {metadata['question']}")
                logger.info(f"Topic: {metadata['topic']}")
                logger.info(f"Tags: {', '.join(metadata['tags']) if metadata['tags'] else 'None'}")

                # Fetch body text from Google Drive
                body_text = fetch_body_from_google_drive(metadata['body_link'])

                if body_text:
                    logger.info(f"Body Text: {body_text[:200]}...")  # Log a snippet of the body text

    except Exception as e:
        logger.error(f"Error during retrieval: {e}")


if __name__ == "__main__":
    # Example query to retrieve similar questions
    retrieve_similar_questions("What is Dr. Chaffee's opinion on fruits?")





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

# # Connection to your Neo4j instance
# uri = neo4j_uri
# username = neo4j_username
# password = neo4j_password

# driver = GraphDatabase.driver(uri, auth=(username, password))

# # Initialize Neo4jGenAI
# genai = Neo4jGenAI(driver)

# # Sample query to retrieve data
# query = """
# MATCH (r:Response)-[:RELATED_TO]->(t:Topic)
# WHERE t.name = $topic
# RETURN r.text AS response
# """

# topic_name = "carnivore diet"  # Example topic
# results = genai.query(query, {"topic": topic_name})

# for record in results:
#     print(record["response"])



#     # Chain: Neo4j data -> LLM
# def get_neo4j_responses_and_generate(query):
#     # Query Neo4j for relevant responses
#     results = genai.query(query, {"topic": topic_name})

#     # Extract responses
#     context = "\n".join([record["response"] for record in results])

#     # Prepare a prompt for the LLM based on retrieved context
#     prompt = f"""
#     You are an expert in {topic_name}.
#     Here are some relevant responses:
#     {context}

#     Based on this information, provide a detailed answer to the following question:
#     """

#     # Generate final answer using LLM
#     final_response = llm(prompt)
#     return final_response

# # Example usage
# response = get_neo4j_responses_and_generate(query)
# print(response)
