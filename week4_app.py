from foundry_local_sdk import Configuration, FoundryLocalManager
import sqlite3
import math
import json
import streamlit as st
def ep_progress_callback(ep_name, percent):
    print(f"\r📥 [{ep_name}]: {round(percent)}%", end="\r")
def cosine_similarity(vec_a, vec_b):
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot_product / (norm_a * norm_b)
def get_top_chunks(conn,embedding_client,query,top_k=2):
      query_embedding=embedding_client.generate_embeddings([query]).data[0].embedding
      rows = conn.execute("SELECT id, content, embedding FROM chunks").fetchall()
      similarities = []
      for row in rows:
          chunk_id, content, embedding_json = row
          chunk_embedding = json.loads(embedding_json)
          similarity_score = cosine_similarity(query_embedding, chunk_embedding)
          similarities.append((chunk_id, content, similarity_score))
         
      similarities.sort(key=lambda x: x[2], reverse=True)
      return similarities[:top_k]   
def answer_query(conn, embedding_client, chat_client, question):
    top_chunks = get_top_chunks(conn, embedding_client, question, top_k=2)
    context = "\n".join([f"Chunk {i+1}: {chunk[1]}" for i, chunk in enumerate(top_chunks)])
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    response = chat_client.complete_chat([
        {"role": "system", "content": "You must answer the question using only the context given to you. If the answer is not in the context, say 'I don't know.' Answer in the same language as the question."},
        {"role": "user", "content": prompt}
])
    
    return response.choices[0].message.content
@st.cache_resource
def load_models():
    FoundryLocalManager.initialize(Configuration(app_name="MyLocalRAGAssistant"))
    manager = FoundryLocalManager.instance
    manager.download_and_register_eps()
    
    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embedding_model.download()
    embedding_model.load()
    embedding_client = embedding_model.get_embedding_client()

    chat_model = manager.catalog.get_model("phi-3.5-mini")
    chat_model.download()
    chat_model.load()
    chat_client = chat_model.get_chat_client()
    chat_client.settings.max_tokens = 300
    
   
    return embedding_client, chat_client
embedding_client, chat_client = load_models()
conn = sqlite3.connect("chunks.db", check_same_thread=False)
 # kullanıcı bunu görür
st.title("Yerel RAG Asistanım")  
question = st.text_input("Soru:", key="question")
if question:
    answer = answer_query(conn, embedding_client, chat_client, question)
    st.write(f"Cevap: {answer}")

