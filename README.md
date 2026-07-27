# 🤖 Yerel RAG Asistanı (Local RAG Assistant)

Microsoft AI Innovators Summer Internship programı kapsamında tamamen yerel donanım üzerinde çalışan, harici API bağımlılığı olmayan ve gizlilik odaklı geliştirilmiş uçtan uca bir **Retrieval-Augmented Generation (RAG)** asistanıdır. Microsoft Foundry Local SDK altyapısı, `qwen3-embedding-0.6b` embedding modeli, `qwen2.5-7b` üretken dil modeli, SQLite veritabanı ve **Streamlit** arayüzü ile güçlendirilmiştir.

---

## ✨ Öne Çıkan Özellikler

* **🔒 %100 Çevrimdışı ve Güvenli:** Verileriniz dış sunuculara gitmez; tüm süreçler tamamen yerel donanım üzerinde yürütülür.
* **⚡ Anlamsal Arama (Semantic Search):** Metinler `qwen3-embedding-0.6b` modeliyle vektörlere dönüştürülür ve yerel SQLite veritabanında (`chunks.db`) saklanır.
* **🧠 Yerel LLM Çıkarımı:** Doğal dil yanıtları ve bağlamsal sorgulamalar `qwen2.5-7b` modeliyle sağlanır.
* **📑 Şeffaf Kaynak Gösterimi:** Her yanıtın hangi kaynak belgeden üretildiği, benzerlik skorları ve filtrelenmiş eşik değerleriyle arayüzde şeffaf bir şekilde listelenir.
* **🎨 Modern ve İnteraktif Arayüz:** Streamlit tabanlı, hızlı ve kullanıcı dostu web arayüzü sunar.

---

## 🏗️ Mimari ve RAG Akışı

```text
[Kullanıcı Sorgusu] 
     │
     ▼
[Embedding Modeli: qwen3-embedding-0.6b] ────► [Vektör Veritabanı: SQLite / chunks.db]
                                                              │
                                                              ▼ (En İlgili Chunk'lar)
                                                              │
[Yerel LLM: qwen2.5-7b] ◄─────────────────────────────────────┘
     │
     ▼
[Grounded Yanıt + Kaynak Gösterimi]

* Ingestion (Veri Alımı): Yerel .txt belgeleri okunur, paragraflara (chunk) bölünür ve embedding'leri çıkarılarak chunks.db veritabanına kaydedilir.

* Retrieval (Erişim): Kullanıcı bir soru sorduğunda, sistem vektör benzerliği (Cosine Similarity) hesaplayarak en ilgili belge parçalarını getirir.

* Generation (Üretim): Getirilen parçalar bağlam (context) olarak qwen2.5-7b modeline katı sistem promptu ile beslenir, böylece halüsinasyon (uydurma) olmaksızın güvenli ve doğru yanıtlar üretilir.

🛠️ Kullanılan Teknolojiler
* Arayüz: Streamlit (week4_app.py, @st.cache_resource optimizasyonu)

* Yerel AI Altyapısı: foundry_local_sdk (FoundryLocalManager, Configuration)

* Yapay Zeka Modelleri:

* Chat / Üretim: qwen2.5-7b (temperature=0.1)

* Embedding: qwen3-embedding-0.6b

🚀 Kurulum ve Çalıştırma
Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları takip edebilirsiniz:

Depoyu klonlayın:

Bash
git clone [https://github.com/SUNAYILDIZ/yerel-rag-asistanim.git](https://github.com/SUNAYILDIZ/yerel-rag-asistanim.git)
cd yerel-rag-asistanim
Gerekli kütüphaneleri yükleyin:

Bash
pip install -r requirements.txt
Uygulamayı başlatın:

Bash
streamlit run week4_app.py
📁 Proje Yapısı
Plaintext
Yerel_RAG_Asistanim/
├── Belgeler/            # RAG sisteminin taranacağı kaynak metinler (.txt)
├── chunks.db            # SQLite vektör veritabanı (Parçalanmış metinler ve embedding'ler)
├── week4.py             # Veri işleme, chunking, embedding ve benzerlik hesaplama modülü
├── week4_app.py         # Streamlit tabanlı ana arayüz, dil tespiti ve UI mantığı
├── requirements.txt     # Proje bağımlılıkları ve Python kütüphaneleri
└── README.md            # Proje dokümantasyonu
📜 Lisans
Bu proje kişisel ve kurumsal yerel RAG denemeleri için özgürce kullanılabilir.

* Dil Tespiti & Metin İşleme: langdetect (Otomatik Türkçe/İngilizce yönlendirme), re (Normalizasyon)

* Veritabanı: SQLite (chunks.db)

* Dil ve Paket Yönetimi: Python, Pip
