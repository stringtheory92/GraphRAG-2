import os
import json
import ollama  

def load_json(file_path):
    """Loads the JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    """Saves the processed JSON data back to a file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# def extract_question_and_tags(text, model_name="llama2:latest"):
#     """
#     Uses Ollama's local model to extract the question from a given text
#     and generate a list of tags/keywords.
#     """
#     # Define the prompt for the model
#     prompt = f"""
#     You are given a section of a transcript. Your task is:
#     1. Extract the main question from the text.
#     2. Generate a list of tags or keywords that can help someone search for this information.

#     Section: {text}

#     Please respond with the question followed by a list of keywords.
#     """

#     # Run the prompt through the model using Ollama's API (assuming you have Ollama setup)
#     response = ollama.chat(model=model_name, messages=[
#     {
#         'role': 'user',
#         'content': prompt
#     }
# ])

#     # Parse the response, assuming the model provides a structured output
#     question, *tags = response.strip().split("\n")

#     # Clean the tags into a list of keywords
#     tags = [tag.strip() for tag in tags if tag]

#     return question, tags

def extract_question_and_tags(text, model_name="llama2:latest"):
    """
    Uses Ollama's local model to extract the question from a given text
    and generate a list of tags/keywords.
    """
    # Define the prompt for the model
    prompt = f"""
    You are given a transcript of a conversation. The transcript contains both the question
    and the response, but the questio, while usually located toward the beginning of the body of text, is not explicitly marked. It may be fragmented or unclear
    and must be inferred from the response. Your tasks fall into two categories:

    Questions:
    1. Infer the most relevant question being answered in the transcript. Use the context of the response to help determine the question. 
    2. Only return the question portion of your response. DO NOT ADD ANY ADDITIONAL TEXT BEFORE OR AFTER THE QUESTION. 

    Keywords:
    1. Only return the list of keywords as strings.
    2. Do not include any numbers, symbols, or extra words like "Sure!", "Here are", "Keywords:", or other similar phrases.
    3. Each keyword should be a single word or short phrase without additional formatting.
    4. Return the list as plain strings, one keyword per line.
    5. DO NOT INCLUDE ANY NUMERATION, ADDITIONAL COMMENTS, OR ANY OTHER TEXT AT ALL. ONLY 1 KEYWORD PER INDEX AND NOTHING MORE

    The inferred question should be a complete sentence, as if someone had asked it directly.
    The tags should be one-word or simple keyword phrases, uniquely representative of the body of text. The tags should each point to a main topic of that section

    Transcript: {text}

    Please respond with the inferred question first, followed by a list of keywords.

    """
    # prompt = f"""
    # You are given a section of a transcript. Your task is to generate a list of keywords that can help someone search for this information. 
    # Please follow these rules:
    # 1. Only return the list of keywords as strings.
    # 2. Do not include any numbers, symbols, or extra words like "Sure!", "Here are", "Keywords:", or other similar phrases.
    # 3. Each keyword should be a single word or short phrase without additional formatting.
    # 4. Return the list as plain strings, one keyword per line.
    # 5. DO NOT INCLUDE ANY NUMERATION, ADDITIONAL COMMENTS, OR ANY OTHER TEXT AT ALL. ONLY 1 KEYWORD PER INDEX AND NOTHING MORE


    # Section: {text}

    # Please respond with the clean list of keywords.

    # example:
    # Section: "Dr chafee what is your opinion on fruits for someone like myself who's extremely active and trains a lot you always mention that plants are bitter and don't want us to eat them but fruits are sweet so fruits are delicious yeah but but Sugar's a drug and that and that's the main thing so this is why yes you know if something tastes bad that's your brain and your tongue giving you a clear signal inside that there's something bad in there and it says don't eat this spit this out right ..."
    # Expected Output:   fruits
    #     sugar
    #     active lifestyle
    #     training
    #     plants
    #     sweetness
    #     metabolism
    #     energy
    #     fat storage
    #     fructose

    # """

    # Run the prompt through the model using Ollama's API
    response = ollama.chat(model=model_name, messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ])

    # Extract the message content from the response dictionary
    message_content = response['message']['content']

    # Split the response content into the inferred question and tags
    inferred_question, *tags = message_content.strip().split("\n")

    # Clean the tags into a list of keywords (using the previous cleaning function)
    clean_tags = clean_keywords(tags)

    return inferred_question, clean_tags

def clean_keywords(raw_keywords):
    """
    Cleans the raw keywords by removing numbers, 'Keywords:' and other irrelevant data,
    returning a list of clean keyword strings.
    """
    clean_list = []
    for keyword in raw_keywords:
        # Remove any numerical indicators or unnecessary parts
        keyword = keyword.strip()
        keyword = keyword.lstrip("0123456789.- ")  # Remove numbers, dots, dashes, and spaces at the start
        keyword = keyword.replace("Keywords:", "")  # Remove 'Keywords:' text if present
        keyword = keyword.strip()  # Strip extra spaces again
        if keyword:  # Only append non-empty strings
            clean_list.append(keyword)
    return clean_list



def process_batch_files(input_dir, model_name="llama2:latest"):
    """Processes all JSON files in the batch_processed_files directory."""
    for file_name in os.listdir(input_dir):
        if file_name.endswith("_processed.json"):
            file_path = os.path.join(input_dir, file_name)
            print(f"Processing file: {file_path}")

            # Load the JSON file
            data = load_json(file_path)

            # Process each section in the JSON data
            for section in data:
                text = section["transcript"]

                # Use the LLM to extract the question and tags
                question, tags = extract_question_and_tags(text, model_name=model_name)

                # Add the extracted question and tags as metadata
                section["tags"] = tags
                section["question"] = question

            # Save the updated JSON file
            save_json(data, file_path)
            print(f"Processed file saved: {file_path}")

# Example usage:
input_directory = "data_processing/batched_processed_files"

# Process all files in the batch_processed_files directory
process_batch_files(input_directory, model_name="llama2:latest")
