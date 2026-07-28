import streamlit as st
import sqlite3
import re
from langdetect import detect, DetectorFactory
from foundry_local_sdk import Configuration, FoundryLocalManager

from week4 import get_top_chunks

DetectorFactory.seed = 0

SCORE_THRESHOLD = 0.5


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
    'IsePET' gibi yapışık kelimeleri ayırır (küçük->büyük harf geçişinde boşluk ekler).
    """
    return re.sub(r'([a-zçğıöşü])([A-ZÇİÖŞ])', r'\1 \2', text)


def quick_clean(text, user_lang="tr"):
    """
    Sistemi yavaşlatmayan, sadece kritik CJK karakterlerini,
    parantezli Türkçe açılımları (yalnızca İngilizce modda),
    yapışık kelimeleri ve uzun döngü hatalarını temizleyen hızlı fonksiyon.
    """
    cleaned = text.strip().strip('"')

    # CJK (Çince/Japonca/Korece) harf VE noktalama işaretlerini temizle.
    cjk_pattern = r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\u3000-\u303f\uff00-\uffef]+'
    cleaned = re.sub(cjk_pattern, '', cleaned)

    # İNGİLİZCE MODUNDA PARANTEZ TEMİZLİĞİ: Parantez içindeki Türkçe ifadeleri
    # (ve parantezi) tamamen sil. Sadece user_lang == "en" iken çalışır;
    # aksi halde Türkçe modda geçerli parantezli açıklamalar da silinirdi.
    if user_lang == "en":
        cleaned = re.sub(r'\s*\([^)]*[çğıöşüÇİÖŞ][^)]*\)', '', cleaned)

    # DÖNGÜ KIRICI: En az 20 karakterlik bir cümle/öbek peş peşe tekrarlanıyorsa teke indir
    cleaned = re.sub(r'(.{20,}?)\1+', r'\1', cleaned)

    # Yapışık kelimeleri ayır (örn. "IsePET" -> "Ise PET")
    cleaned = format_output(cleaned)

    # Fazla boşlukları temizle
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Noktalamadan önceki boşlukları temizle
    cleaned = re.sub(r'\s+([,.;:!?])', r'\1', cleaned)

    # CJK/Temizlik sonrası cümle yarım kalıp virgülle bitmiş olabilir
    cleaned = re.sub(r',\s*$', '.', cleaned)

    return cleaned.strip()


def is_no_answer(content, user_lang):
    """
    Modelin 'bilmiyorum' dediğini, metnin İÇİNDE herhangi bir yerde değil,
    cevabın BAŞINDA / tek başına bir ifade olarak arar. Böylece cevabın
    ortasında geçen bir 'bilmiyorum' kelimesi yanlışlıkla tetiklenmez.
    """
    normalized = content.strip().lower().rstrip('.!')
    no_answer_phrases_tr = ["bilmiyorum"]
    no_answer_phrases_en = ["i don't know", "i do not know"]

    phrases = no_answer_phrases_tr if user_lang == "tr" else no_answer_phrases_en
    # Tam eşleşme ya da cevabın en başında geçme kontrolü
    return any(normalized == p or normalized.startswith(p) for p in phrases)


def answer_query_ui(conn, embedding_client, chat_client, question):
    """
    Ayrıştırılmış sistem promptları ile cevap üreten ana fonksiyon.
    """
    user_lang = detect_language(question)

    top_chunks = get_top_chunks(conn, embedding_client, question, top_k=4)

    
    # Sadece eşik değerinin üzerindeki chunk'ları geçerli kabul et;
    # düşük skorlu, alakasız chunk'ları modele göndermeyerek gürültüyü azalt.
    valid_chunks = [c for c in top_chunks if c[2] >= SCORE_THRESHOLD]

    if not valid_chunks:
        msg = "Aradığınız bilgi belgelerimde bulunamadı. Lütfen farklı bir soru sormayı deneyin." \
            if user_lang == "tr" else \
            "The requested information was not found in the documents. Please try asking a different question."
        return msg, [], True

    context = "\n\n".join([chunk[1] for chunk in valid_chunks])

    if user_lang == "en":
        system_prompt = (
            "You are a helpful QA assistant.\n"
            "Answer using ONLY the provided Context.\n"
            "CRITICAL RULES:\n"
            "1. Write ENTIRELY in English. \n"
            "2. Keep it short (1-3 sentences).\n"
            "3. If the context is insufficient, reply strictly with 'I don't know'."
        )
        target_lang_str = "ENGLISH"

    else:
        system_prompt = (
            "Sen yardımcı bir soru-cevap asistanısın.\n"
            "Soruyu YALNIZCA sağlanan Bağlamı kullanarak yanıtla.\n"
            "Talimatlar:\n"
            "- Sadece Türkçe yanıt ver.\n"
            "- Kısa ve net ol (1-3 cümle).\n"
            "- Bağlam yetersizse YALNIZCA 'Bilmiyorum' de."
        )
        target_lang_str = "TURKISH"

    prompt = f"Context:\n{context}\n\nQuestion: {question}\nTarget Response Language: {target_lang_str}\nAnswer:"

    response = chat_client.complete_chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])

    raw_content = response.choices[0].message.content
    content = quick_clean(raw_content, user_lang)

    is_not_found = is_no_answer(content, user_lang)

    if is_not_found:
        if user_lang == "tr":
            content = "Aradığınız bilgi belgelerimde bulunamadı. Lütfen farklı bir soru sormayı deneyin."
        else:
            content = "The requested information was not found in the documents. Please try asking a different question."

    return content, valid_chunks, is_not_found


@st.cache_resource
def load_models():
    """
    Microsoft Foundry Local SDK üzerinden modelleri önbelleğe alarak yükler.
    """
    try:
        FoundryLocalManager.initialize(Configuration(app_name="MyLocalRAGAssistant"))
    except:
        pass
    manager = FoundryLocalManager.instance
    manager.download_and_register_eps()

    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embedding_model.download()
    embedding_model.load()
    embedding_client = embedding_model.get_embedding_client()

    chat_model = manager.catalog.get_model("qwen2.5-7b")
    chat_model.download()
    chat_model.load()
    chat_client = chat_model.get_chat_client()

    chat_client.settings.max_tokens = 300
    chat_client.settings.temperature = 0.2

    return embedding_client, chat_client


embedding_client, chat_client = load_models()
conn = sqlite3.connect("chunks.db", check_same_thread=False)

st.title("Yerel RAG Asistanım")

# Form kullanımı: Her tuş vuruşunda değil, yalnızca "Sor" butonuna
# basıldığında (veya Enter'a basıldığında) script'in çalışmasını sağlar.
with st.form(key="question_form"):
    question = st.text_input("Soru:", key="question")
    submitted = st.form_submit_button("🔍")       

if submitted:
    cleaned_question = question.strip()

    if cleaned_question:
        content, valid_chunks, is_not_found = answer_query_ui(
            conn, embedding_client, chat_client, cleaned_question
        )

        st.write(f"**Cevap:** {content}")

        if not is_not_found and valid_chunks:
            st.write("**Kaynaklar:**")
            seen_sources = set()
            for chunk_id, chunk_content, score in valid_chunks:
                # Chunk içeriğinde ":" yoksa tamamını kaynak adı say (IndexError'dan korunma)
                source_name = chunk_content.partition(":")[0].strip() if ":" in chunk_content else chunk_content[:40].strip()
                if source_name not in seen_sources:
                    st.write(f"- {source_name} (skor: {score:.3f})")
                    seen_sources.add(source_name)