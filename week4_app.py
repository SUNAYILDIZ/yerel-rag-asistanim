import streamlit as st
import sqlite3
import re
from langdetect import detect, DetectorFactory
from foundry_local_sdk import Configuration, FoundryLocalManager

# week4.py dosyasından sadece gereken ana parçayı (get_top_chunks) alıyoruz
from week4 import get_top_chunks

# Dil tespitinin her çalışmada tutarlı (deterministic) olması için seed sabitliyoruz
DetectorFactory.seed = 0

def detect_language(text):
    """
    Kullanıcının girdiği sorunun dilini tespit eder.
    """
    try:
        lang = detect(text)
        return "tr" if lang == "tr" else "en"
    except:
        return "tr"

def format_output(text):
    """
    LLM çıktısındaki olası tırnakları temizler ve yapışık kelimeleri ayırır.
    """
    cleaned = text.strip()
    
    if cleaned.startswith('"') and cleaned.endswith('"'):
        cleaned = cleaned[1:-1]
        
    cleaned = re.sub(r'([a-zğüşöçı])([A-ZĞÜŞİÖÇ])', r'\1 \2', cleaned)
    return cleaned

def answer_query_ui(conn, embedding_client, chat_client, question):
    """
    Streamlit arayüzüne özel cevap üretici. Kaynakları ekrana basabilmek için
    top_chunks verisini de döndürür.
    """
    # 1. Adım: Sorunun dilini önceden tespit et
    user_lang = detect_language(question)
    
    top_chunks = get_top_chunks(conn, embedding_client, question, top_k=6)
    context = "\n\n".join([chunk[1] for chunk in top_chunks])
    
    # 2. Adım: Dile özel katı yönlendirme ekle
    if user_lang == "en":
        lang_instruction = (
            "CRITICAL: The user asked in ENGLISH. Even if the Context is in Turkish, "
            "you MUST translate the extracted information and answer strictly in ENGLISH."
        )
    else:
        lang_instruction = (
            "ÖNEMLİ: Kullanıcı soruyu TÜRKÇE sordu. Yanıtı kesinlikle TÜRKÇE veriniz."
        )

    system_prompt = (
        f"You are a strict QA assistant. Answer the question using ONLY the provided context.\n"
        f"{lang_instruction}\n"
        "1. Extract the facts from the context to answer the question. Do NOT hallucinate.\n"
        "2. Answer directly and naturally without using internal terms like 'chunk', 'context', or 'document'.\n"
        "3. If the context does not contain enough information, respond ONLY with 'Bilmiyorum' (for Turkish) or 'I don't know' (for English)."
    )
    
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    
    response = chat_client.complete_chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])
    
    content = format_output(response.choices[0].message.content)
    is_not_found = ("bilmiyorum" in content.lower() or "i don't know" in content.lower()) and top_chunks[0][2] < 0.5
    
    if is_not_found:
        if user_lang == "tr":
            content = "Aradığınız bilgi belgelerimde bulunamadı. Lütfen farklı bir soru sormayı deneyin."
        else:
            content = "The requested information was not found in the documents. Please try asking a different question."
    
    return content, top_chunks, is_not_found

@st.cache_resource
def load_models():
    """
    Uygulama her yenilendiğinde modelleri baştan yüklememek için önbelleğe alır.
    """
    try:
        FoundryLocalManager.initialize(Configuration(app_name="MyLocalRAGAssistant"))
    except:
        pass
    manager = FoundryLocalManager.instance
    manager.download_and_register_eps()
    
    # Embedding Modeli
    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embedding_model.download()
    embedding_model.load()
    embedding_client = embedding_model.get_embedding_client()

    # Chat Modeli 
    chat_model = manager.catalog.get_model("qwen2.5-7b")
    chat_model.download()
    chat_model.load()
    chat_client = chat_model.get_chat_client()
    chat_client.settings.max_tokens = 300
    chat_client.settings.temperature = 0.1 
    
    return embedding_client, chat_client

# Modelleri ve veritabanı bağlantısını başlatıyoruz
embedding_client, chat_client = load_models()
conn = sqlite3.connect("chunks.db", check_same_thread=False)

# --- Streamlit Arayüzü ---
st.title("Yerel RAG Asistanım")  
question = st.text_input("Soru:", key="question")

cleaned_question = question.strip()

if cleaned_question:
    content, top_chunks, is_not_found = answer_query_ui(conn, embedding_client, chat_client, cleaned_question)
    st.write(f"Cevap: {content}")
    
    # Bilgi bulunduysa kaynakları listele
    if not is_not_found:
        valid_sources = [c for c in top_chunks if c[2] > 0.5]
        if valid_sources:
            st.write("**Kaynaklar:**")
            seen_sources = set()
            for chunk_id, chunk_content, score in valid_sources:
                source_name = chunk_content.split(":")[0].strip()
                if source_name not in seen_sources:
                    st.write(f"- {source_name} (skor: {score:.3f})")
                    seen_sources.add(source_name)