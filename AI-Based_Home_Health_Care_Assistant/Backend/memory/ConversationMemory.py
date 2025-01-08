import ollama
import chromadb
from database.database  import connect_db
from AI_Agents.Agents import create_queries, classify_embedding
from psycopg.rows import dict_row

client = chromadb.Client()
convo = []

def fetch_conversations():
    """Fetch all stored conversations from the memory database."""
    conn = connect_db()
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute('SELECT * FROM conversations')
        conversations = cursor.fetchall()
    conn.close()
    return conversations

def store_conversations(prompt, response):
    """Store the current conversation (prompt and response) in the memory database."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(
            'INSERT INTO conversations(timestamp, prompt, response) VALUES (CURRENT_TIMESTAMP, %s, %s)',
            (prompt, response)
        )
        conn.commit()
    conn.close()

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

def recall(prompt):
    """Recall relevant past conversations based on the user's prompt."""
    queries = create_queries(prompt=prompt)
    embeddings = retrieve_embeddings(queries=queries)
    convo.append({'role': 'user', 'content': f'MEMORIES:{embeddings} \n\n USER PROMPT: {prompt}'})

def stream_response(prompt):
    """Stream and print the AI assistant's response."""
    response = ''
    stream = ollama.chat(model='llama3', messages=convo, stream=True)
    print('\nASSISTANT:')

    for chunk in stream:
        content = chunk['message']['content']
        response += content
        print(content, end='', flush=True)

    print('\n')
    store_conversations(prompt=prompt, response=response)
    convo.append({'role': 'assistant', 'content': response})
    return response