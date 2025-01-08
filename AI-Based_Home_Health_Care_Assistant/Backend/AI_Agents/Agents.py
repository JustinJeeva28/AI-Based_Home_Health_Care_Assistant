import ollama
import ast
from config.settings import DB_PARAMS
from database.database import connect_db

def classify_msg(prompt):
    """Classify the type of message received from the user."""
    classify_msg = (
        'You are a classification AI agent. Your input will be a prompt. '
        'You will classify the prompt into one of the following categories: "emergency", "general query", or "reminder query". '
        'If the input is related to a critical situation requiring immediate attention, classify it as "emergency". '
        'If the input is a general question or inquiry, classify it as "general query". '
        'If the input is related to setting or managing reminders, classify it as "reminder query". '
        'Respond only with the category name: "emergency", "general query", or "reminder query". '
        'If the input does not clearly fit into any of these categories, respond with "general query".'
    )

    classify_convo = [
        {'role': 'system', 'content': classify_msg},
        {'role': 'user', 'content': prompt}
    ]

    response = ollama.chat(model='llama3', messages=classify_convo)
    return response['message']['content']

def classify_embedding(query, context):
    """Classify the relevance of a given context to a search query."""
    classify_msg = (
        'You are an embedding classification AI agent. Your input will be a prompt and one embedded chunk of text.'
        'You will not respond as an AI assistant. You only respond "yes" or "no".'
        'Determine whether the context contains data that directly is related to the search query. '
        'If the context is seemingly exactly what the search query needs, respond "yes" if it is anything but directly '
        'related respond "no". Do not respond "yes" unless the content is highly relevant to the search query.'
    )

    classify_convo = [
        {'role': 'system', 'content': classify_msg},
        {'role': 'user', 'content': f'SEARCH QUERY: {query} \n\nEMBEDDED CONTEXT: {context}'}
    ]
    
    response = ollama.chat(model='llama3', messages=classify_convo)
    return response["message"]["content"].strip().lower()

def create_queries(prompt):
    """Create a list of search queries based on the user's prompt."""
    query_msg = (
        'You are a first principle reasoning search query AI agent.'
        'Your list of search queries will be ran on an embedding database of all your conversations '
        'you have ever had with the user. With first principles create a Python list of queries to '
        'search the embeddings database for any data that would be necessary to have access to in '
        'order to correctly respond to the prompt. Your response must be a Python list with no syntax errors.'
        'Do not explain anything and do not ever generate anything but a perfect syntax Python list'
    )

    query_convo = [
        {'role': 'system', 'content': query_msg},
        {'role': 'user', 'content': prompt}
    ]

    response = ollama.chat(model='llama3', messages=query_convo)

    try:
        return ast.literal_eval(response["message"]["content"])
    except:
        return [prompt]

def health_history(prompt):
    """Classify the type of message received from the user and extract medical data."""
    classify_msg = (
        'You are a MEDICAL HISTORY EXTRACTING  AI agent. Your input will be a prompt. '
        'You will EXTRACT the prompt into one of the following categories: "THE HEALTH DATA IN THE PROMPT", or "null". '
        'If the input contains information about past medical conditions, treatments, or medications, U GIVE THE  it as "THE HEALTH DATA IN THE PROMPT". '
        'If the input contains specific health-related data such as symptoms, vital signs, or health metrics, classify it as "health data". '
        'If the input does not contain any relevant medical information, respond with "null".'
    )

    classify_convo = [
        {'role': 'system', 'content': classify_msg},
        {'role': 'user', 'content': 'I have a history of hypertension and take medication for it.'},
        {'role': 'assistant', 'content': 'the user has hypertension and he is taking medication for it.'},
        {'role': 'user', 'content': 'My blood pressure reading was 120 over 80.'},
        {'role': 'assistant', 'content': 'User blood presseue was 120/80.'},
        {'role': 'user', 'content': 'I feel fine, nothing to report.'},
        {'role': 'assistant', 'content': 'null'},
        {'role': 'user', 'content': prompt}
    ]

    response = ollama.chat(model='llama3', messages=classify_convo)

    try:
        message_content = response['message']['content']  # Adjust this based on the actual structure
        # print(response)
        if message_content != 'null':
            conn = connect_db(DB_PARAMS)
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO health_history(timestamp, history) VALUES (CURRENT_TIMESTAMP, %s)',
                    (message_content,)
                )
                conn.commit()
            conn.close()
    except KeyError as e:
        print(f"KeyError: {e}. The response structure may not match your expectation.")
    except Exception as e:
        print(f"An error occurred: {e}")