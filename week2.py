from foundry_local_sdk import Configuration, FoundryLocalManager 
import math
import sqlite3
import json
import streamlit as st

def ep_progress_callback(ep_name, percent):
    print(f"\r📥 [{ep_name}]: {round(percent)}%", end="\r")

@st.cache_resource
def load_embedding_client():
    config = Configuration(app_name="MyLocalRAGAssistant")
    try:
        FoundryLocalManager.initialize(config)   
    except Exception:
        pass
        
    manager = FoundryLocalManager.instance
    #Embedding modelini indir ve yükle
    # Niye phi-3.5-mini yerine qwen3-embedding-0.6b kullanıyoruz? Çünkü embedding modeli, metinleri vektörlere dönüştürmek için özel olarak tasarlanmıştır ve RAG (Retrieval-Augmented Generation) uygulamaları için daha uygundur. 
    # phi-3.5-mini ise bir dil modelidir ve metin üretimi için kullanılır, embedding oluşturmak için optimize edilmemiştir. Bu nedenle, embedding işlemleri için qwen3-embedding-0.6b modelini tercih ediyoruz.
    manager.download_and_register_eps(progress_callback=ep_progress_callback)
    model = manager.catalog.get_model("qwen3-embedding-0.6b")
    model.download()
    model.load()
    
    return model.get_embedding_client()

def cosine_similarity(vec_a, vec_b):
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    #Norm a yada norm b sıfır olursa, yani vektörlerden biri sıfır vektör ise, bu durumda kosinüs benzerliği tanımsız olur ve bir hata oluşur. Bu nedenle, norm_a veya norm_b sıfır olduğunda, fonksiyon 0 döndürür. Bu, iki vektörün birbirine hiç benzemediğini ifade eder.
    if norm_a == 0 or norm_b == 0:
        return 0

    return dot_product / (norm_a * norm_b)

def init_db(db_name="belgeler.db"):
    conn = sqlite3.connect(db_name)
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        embedding TEXT NOT NULL
                 )
    """)
    conn.commit()
    return conn

def ingest_data(phrases, embedding_client, db_name="belgeler.db"):
    conn = init_db(db_name)
    count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    
    if count > 0:
        print("There is data .You don't use insert method")
        data = conn.execute("SELECT id, content FROM documents").fetchall()
        for i in data:
            print(i)
    else:
        response = embedding_client.generate_embeddings(phrases)
        
        #3 metnin hepsinin ilk 3 sayısını görmek için döngü ile yazdırıyoruz.
        for i, item in enumerate(response.data):
            print(f"\nPhrase {i+1}: {phrases[i]}")
            print(f"Embedding (ilk 3 sayı): {item.embedding[:3]}")
            
        for phrase, item in zip(phrases, response.data):
            embedding_json = json.dumps(item.embedding)
            conn.execute("INSERT INTO documents (content, embedding) VALUES (?, ?)", (phrase, embedding_json))
            #Değişiklikleri kaydetmek için commit() metodunu çağırıyoruz.Bu veritabanında yaptığımız değişiklikleri kaydeder.
            conn.commit()
            
        #execute() metodunu kullanarak veritabanındaki belgelerin sayısını sorguluyoruz ve fetchone() metodunu kullanarak sonucu alıyoruz. Bu, veritabanında kaç belge olduğunu gösterir.
        count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()        
        data = conn.execute("SELECT id, content FROM documents").fetchall()
        for i in data:
            print(i)
            
    conn.close()

# Bu dosya test edilmek istenirse aşağıdaki kodlar çalışır
if __name__ == "__main__":
    client = load_embedding_client()
    phrases = ["What is RAG?", "What is SQLite?", "What is embedding ?"]
    
    # Verileri içeri alma fonksiyonunu çağırıyoruz
    ingest_data(phrases, client)
    
    # Cosine Similarity Testini Fonksiyonlarla Yapıyoruz
    response = client.generate_embeddings(phrases)
    vec1 = response.data[0].embedding
    vec2 = response.data[2].embedding
    similarity_score = cosine_similarity(vec1, vec2)
    
    print(f"\nPhrase 1: {phrases[0]}")
    print(f"Phrase 2: {phrases[2]}")
    print(f"Cosine Similarity: {similarity_score:.4f}")