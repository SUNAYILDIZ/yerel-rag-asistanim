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
```

* Ingestion (Veri Alımı): Yerel .txt belgeleri okunur, paragraflara (chunk) bölünür ve embedding'leri çıkarılarak chunks.db veritabanına kaydedilir.

* Retrieval (Erişim): Kullanıcı bir soru sorduğunda, sistem vektör benzerliği (Cosine Similarity) hesaplayarak en ilgili belge parçalarını getirir.

* Generation (Üretim): Getirilen parçalar bağlam (context) olarak qwen2.5-7b modeline katı sistem promptu ile beslenir, böylece halüsinasyon (uydurma) olmaksızın güvenli ve doğru yanıtlar üretilir.
---

* **Arayüz:** Streamlit (week4_app.py, @st.cache_resource optimizasyonu)
* **Yerel AI Altyapısı:** `foundry_local_sdk` (`FoundryLocalManager`, `Configuration`)
* **Yapay Zeka Modelleri:**
  * **Chat / Üretim:** `qwen2.5-7b` (`temperature=0.1`)
  * **Embedding:** `qwen3-embedding-0.6b`
## 🚀 Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları takip edebilirsiniz:

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/SUNAYILDIZ/yerel-rag-asistanim.git
   cd yerel-rag-asistanim
   ```
2.**Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
  ```
3.**Uygulamayı başlatın:**
  ```bash
  streamlit run week4_app.py
   ```

## 📁 Proje Yapısı
```text
Yerel_RAG_Asistanim/

├── Belgeler/            # RAG sisteminin taranacağı kaynak metinler (.txt)
├── week2.py             # Temel veri işleme modülü
├── week3.py             # Gelişmiş veri operasyonları ve chunking modülü
├── week4.py             # Veri işleme, chunking, embedding ve benzerlik hesaplama modülü
├── week4_app.py         # Streamlit tabanlı ana arayüz, dil tespiti ve UI mantığı
├── main.py              # Uygulama akışını başlatan ana Python betiği
├── .gitignore           # Git tarafından takip edilmeyecek dosya ve klasörler
├── requirements.txt     # Proje bağımlılıkları ve Python kütüphaneleri
└── README.md            # Proje dokümantasyonu
```
> Not: week2-4 dosyaları staj sürecindeki aşamalı geliştirme adımlarını temsil eder. Ana uygulama `week4_app.py`'dir.
---
## 🧪 Test Sonuçları

Sistem, farklı soru kategorileriyle kapsamlı şekilde test edilmiştir.

| # | Soru | Kategori | Beklenen | Sonuç | Not |
|---|------|----------|----------|-------|-----|
| 1 | n8n nedir ve ne işe yarar? | Cevaplanabilir | Doğru cevap | ✅ | — |
| 2 | What is n8n? | Cevaplanabilir (İngilizce) | İngilizce cevap | ✅ | langdetect ile dil tespiti eklendi |
| 3 | Gizlilik için neden n8n tercih edilmeli? | Çıkarım gerektiren | Doğru cevap | ✅ | — |
| 4 | Is n8n a paid platform? | Cevaplanamaz | I don't know | ✅ | Kaynak gösterimi düzeltildi |
| 5 | n8n hangi programlama dillerini destekler? | Cevaplanamaz | Bilmiyorum | ✅ | — |
| 6 | Warka Water nedir ve günde kaç litre üretir? | Cevaplanabilir | Doğru cevap | ✅ | — |
| 7 | Warka Water yapımında hangi malzemeler kullanılır? | Cevaplanabilir | Doğru cevap | ✅ | Prompt leakage düzeltildi |
| 8 | Warka Water ile n8n birlikte kullanılır mı? | Çapraz belge | Bilmiyorum | ✅ | — |
| 9 | Ambalajları paraya dönüştürmek için ne yapmalıyım? | Cevaplanabilir | Adım adım cevap | ⚠️ | Halüsinasyon tespit edildi, temperature=0.1 ile azaltıldı |
| 10 | Kazanılan para nakit çekilebilir mi? | Cevaplanabilir | Doğru cevap | ⚠️ | Belge yetersiz — chunk'ta bilgi eksik |
| 11 | 5 litrelik damacana DOA'ya kabul edilir mi? | Cevaplanabilir | Hayır | ✅ | Sistem doğru reddetti |
| 12 | n8n ile DOA arasındaki farklar nelerdir? | Çapraz Belge | *"Belgede Kıyaslama Yok"* | ✅ | Belgede doğrudan kıyaslama olmadığı için uydurma yanıt engellendi. |
| 13 | Doğayı koruyan sistemler nelerdir? | Semantik çıkarım | Warka Water + DOA | ⚠️ | Retrieval skoru 0.5 altında kaldı |

### Tespit Edilen Sorunlar ve Çözümler

| Sorun | Çözüm |
|-------|-------|
| Model Çince cevap verdi | `langdetect` kütüphanesi ile dil tespiti eklendi |
| "Context'te belirtilmiştir" iç bilgisi sızdı | Sistem promptu sıkılaştırıldı (prompt leakage engellendi) |
| Aynı kaynak iki kez listelendi | `seen_sources` yapısı ile tekrarlayan kaynaklar temizlendi |
| Model kelime uydurdu (halüsinasyon) | `temperature=0.1` ile yaratıcılık kısıtlandı |
| "IsePET" gibi yapışık kelimeler oluştu | `format_output` regex fonksiyonu eklendi |
| Düşük skorlu kaynak gösterildi | Similarity threshold 0.5 uygulandı |

### ⚠️ Bilinen Limitler

- `qwen2.5-7b` modeli bazı sorularda Türkçe gramer hatası yapabilir
- Belge sayısı arttıkça retrieval kalitesi artacaktır
- Semantik olarak yakın ama alakasız chunk'lar bazen 0.5 eşiğini geçebilir
- Az sayıda belgeyle çapraz belge karşılaştırma soruları retrieval kalitesini düşürebilir. 
  Bilgi tabanı genişledikçe bu sorun azalır.
---

## 📜 Lisans
Bu proje kişisel ve kurumsal yerel RAG denemeleri için özgürce kullanılabilir.

* Dil Tespiti & Metin İşleme: langdetect (Otomatik Türkçe/İngilizce yönlendirme), re (Normalizasyon)

* Veritabanı: SQLite (chunks.db)

* Dil ve Paket Yönetimi: Python, Pip
