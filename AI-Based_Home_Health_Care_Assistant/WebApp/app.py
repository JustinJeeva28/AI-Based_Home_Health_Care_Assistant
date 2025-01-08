from flask import Flask, render_template, request, jsonify
import ollama
import chromadb
import psycopg
from psycopg.rows import dict_row
import ast
import os
import asyncio

# Set the event loop policy for Windows
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask(__name__)


# Database connection parameters for health monitoring
DB_PARAMS_HEALTH_MONITORING = {
    'dbname': 'xxxxxx', 
    'user': 'xxxxxx',
    'password': 'xxxxxx',
    'host': 'xxxxxx',
    'port': 'xxxx'  
}

client = chromadb.Client()

system_prompt = (
    'You are an AI healthcare assistant that has memory of every conversation you have ever had with this user. '
    'On every prompt from the user, the system has checked for any relevant messages you have had with the user.'
    'If any embedded previous conversations are attached, use them for context to responding to the user, '
    'if the context is relevant and useful to responding. If the recalled conversations are irrelevant, '
    'disregard speaking about them and respond normally as an AI assistant. Do not talk about recalling conversations.'
    'Just use any useful data from the previous conversations and respond normally as an intelligent AI HEALTHCARE assistant.'
)
convo = [{'role': 'system', 'content': system_prompt}]


async def get_db_connection(db_params):
    return await psycopg.AsyncConnection.connect(**db_params)


def fetch_conversations():
    conn = psycopg.connect(**DB_PARAMS_HEALTH_MONITORING)
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute('SELECT * FROM conversations')
        conversations = cursor.fetchall()
    conn.close()
    return conversations


def store_conversations(prompt, response):
    conn = psycopg.connect(**DB_PARAMS_HEALTH_MONITORING)
    with conn.cursor() as cursor:
        cursor.execute(
            'INSERT INTO conversations(timestamp, prompt, response) VALUES (CURRENT_TIMESTAMP, %s, %s)',
            (prompt, response)
        )
        conn.commit()
    conn.close()


def stream_response(prompt):
    response = ''
    stream = ollama.chat(model='llama3', messages=convo, stream=True)
    for chunk in stream:
        content = chunk['message']['content']
        response += content

    store_conversations(prompt=prompt, response=response)
    convo.append({'role': 'assistant', 'content': response})
    return response


def create_vector_db(conversations):
    vector_db_name = 'conversations'
    try:
        client.delete_collection(name=vector_db_name)
    except ValueError:
        pass

    vector_db = client.create_collection(name=vector_db_name)

    for c in conversations:
        serialized_convo = f'prompt:{c["prompt"]} response:{c["response"]}'
        response = ollama.embeddings(model='nomic-embed-text', prompt=serialized_convo)
        embedding = response['embedding']

        vector_db.add(
            ids=[str(c['id'])],
            embeddings=[embedding],
            documents=[serialized_convo]
        )


def retrieve_embeddings(queries, results_per_query=1):
    embeddings = set()

    for query in queries:
        response = ollama.embeddings(model='nomic-embed-text', prompt=query)
        query_embedding = response['embedding']

        vector_db = client.get_collection(name='conversations')
        results = vector_db.query(query_embeddings=[query_embedding], n_results=results_per_query)
        best_embedding = results['documents'][0]

        for best in best_embedding:
            if best not in embeddings:
                if 'yes' in classify_embedding(query=query, context=best):
                    embeddings.add(best)

    return embeddings


def create_queries(prompt):
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


def classify_embedding(query, context):
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


def recall(prompt):
    queries = create_queries(prompt=prompt)
    embeddings = retrieve_embeddings(queries=queries)
    convo.append({'role': 'user', 'content': f'MEMORIES: {embeddings} \n\n USER PROMPT: {prompt}'})
    return len(embeddings)


conversations = fetch_conversations()
create_vector_db(conversations=conversations)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    num_embeddings = recall(prompt=user_message)
    assistant_response = stream_response(prompt=user_message)
    return jsonify({'assistant': assistant_response, 'num_embeddings': num_embeddings})


@app.route('/api/vitals', methods=['GET'])
async def get_vitals():
    async with await get_db_connection(DB_PARAMS_HEALTH_MONITORING) as conn:
        async with conn.cursor() as cur:
            await cur.execute('SELECT id, timestamp, heart_rate, blood_oxygen_level, temperature FROM vitals')
            vitals = await cur.fetchall()
            # print(vitals)
            vitals_data = [
                {
                    'id': row[0],
                    'timestamp': row[1],
                    'heart_rate': row[2],
                    'blood_oxygen_level': row[3],
                    'temperature': row[4]
                }
                # [ row[0], row[1], row[2], row[3], row[4]]
                for row in vitals
            ]
    return jsonify(vitals_data)


@app.route('/api/reports', methods=['GET'])
async def get_reports():
    async with await get_db_connection(DB_PARAMS_HEALTH_MONITORING) as conn:
        async with conn.cursor() as cur:
            await cur.execute('SELECT id, timestamp, report FROM health_reports')
            reports = await cur.fetchall()
            reports_data = [
                {
                    'id': row[0],
                    'timestamp': row[1],
                    'report': row[2]
                    # [row[0], row[1], row[2]]
                }
                for row in reports
            ]
    return jsonify(reports_data)


# @app.route('/api/health_history', methods=['GET'])
# async def get_health_history():
#     async with await get_db_connection(DB_PARAMS_HEALTH_MONITORING) as conn:
#         async with conn.cursor() as cur:
#             await cur.execute('SELECT id, date, condition, notes FROM health_history')
#             history = await cur.fetchall()
#             history_data = [
#                 {
#                     'id': row[0],
#                     'date': row[1],
#                     'condition': row[2],
#                     'notes': row[3]
#                 }
#                 for row in history
#             ]
#     return jsonify(history_data)


if __name__ == '__main__':
    app.run(debug=True)