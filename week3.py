import os
from foundry_local_sdk import Configuration,FoundryLocalManager 
import sqlite3
import json
import math
def ep_progress_callback(ep_name, percent):
    print(f"\r📥 [{ep_name}]: {round(percent)}%", end="\r")
def load_documents(file_path, file_names=None):
    documents =[]
    for file_name in os.listdir(file_path):
        exact_path = os.path.join(file_path, file_name)
        if os.path.isfile(exact_path):
            if exact_path.endswith(".txt"):
                with open(exact_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    documents.append({"file_name": file_name, "content": content})
    return documents
def cosine_similarity(vec_a, vec_b):
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot_product / (norm_a * norm_b)
docs = load_documents("Belgeler")
print(f"Downloaded documents: {len(docs)}")
#Metni paragraflara bölmek için bir fonksiyon tanımlıyoruz. Bu fonksiyon, metni iki yeni satır karakteri ile ayırarak paragraflara böler ve boş paragrafları filtreler.
#Her metni boş satırdan ikiye böler listeye atar listedeki her paragrafı sırayla alır başındaki ve sonundaki boşlukları temizler atar.
def chunk_document(content,file_name):
    paragraphs = [f"{file_name}: {p.strip()}" for p in content.split("\n\n") if p.strip()]
    return paragraphs
#Paragrafın her bir parçasına chunk adı verilir ve chunk sayısı yazdırılır. Ayrıca, chunk'lar da yazdırılır.
chunks = chunk_document(docs[0]["content"], docs[0]["file_name"])
print(f"Chunk's number: {len(chunks)}")
print(chunks)
all_chunks = []
for doc in docs:
    chunks = chunk_document(doc["content"], doc["file_name"]) 
    all_chunks.extend(chunks)
print(f"Total chunks: {len(all_chunks)}")
config =Configuration(app_name = "MyLocalRagAssistant")
FoundryLocalManager.initialize(config)
manager = FoundryLocalManager.instance
manager.download_and_register_eps(progress_callback=ep_progress_callback)
model = manager.catalog.get_model("qwen3-embedding-0.6b")
model.download()
model.load()
embedding_client = model.get_embedding_client()
response = embedding_client.generate_embeddings(all_chunks)
conn = sqlite3.connect("chunks.db")
conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        embedding TEXT NOT NULL
             )
    """)
conn.commit()
count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
if count > 0:
    print("There is data. You don't use insert method")
    data = conn.execute("SELECT id, content FROM chunks").fetchall()
    for i in data:
        print(i)
else:
    for chunk, embedding in zip(all_chunks, response.data):
        embedding_json = json.dumps(embedding.embedding)
        conn.execute("INSERT INTO chunks (content, embedding) VALUES (?, ?)", (chunk, embedding_json))
        conn.commit()
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
query = "Warka water nedir?"
results = get_top_chunks(conn, embedding_client, query, top_k=2)
for chunk_id, content, score in results:
    print(f"Skor: {score:.3f} | {content[:80]}...")  