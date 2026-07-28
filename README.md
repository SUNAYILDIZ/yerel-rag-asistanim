# 🤖 Yerel RAG Asistanı (Local RAG Assistant)

Microsoft AI Innovators Summer Internship programı kapsamında tamamen yerel donanım üzerinde çalışan, harici API bağımlılığı olmayan ve gizlilik odaklı geliştirilmiş uçtan uca bir **Retrieval-Augmented Generation (RAG)** asistanıdır. Microsoft Foundry Local SDK altyapısı, `qwen3-embedding-0.6b` embedding modeli, `qwen2.5-7b` üretken dil modeli, SQLite veritabanı ve **Streamlit** arayüzü ile güçlendirilmiştir.

---

## ✨ Öne Çıkan Özellikler

* **🔒 %100 Çevrimdışı ve Güvenli:** Verileriniz dış sunuculara gitmez; tüm süreçler tamamen yerel donanım üzerinde yürütülür.
* **⚡ Anlamsal Arama (Semantic Search):** Metinler `qwen3-embedding-0.6b` modeliyle vektörlere dönüştürülür ve yerel SQLite veritabanında (`chunks.db`) saklanır.
* **🧠 Yerel LLM Çıkarımı:** Doğal dil yanıtları ve bağlamsal sorgulamalar `qwen2.5-7b` modeliyle sağlanır.
* **📑 Şeffaf Kaynak Gösterimi:** Her yanıtın hangi kaynak belgeden üretildiği, benzerlik skorları ve filtrelenmiş eşik değerleriyle arayüzde şeffaf bir şekilde listelenir.
* **🌐 Otomatik Dil Tespiti:** `langdetect` ile soru dili tespit edilir, cevap ve iç temizlik mantığı (parantez temizleme vb.) buna göre uyarlanır.
* **🎨 Modern ve İnteraktif Arayüz:** Streamlit tabanlı, form tabanlı (her tuş vuruşunda değil, yalnızca gönderimde çalışan) hızlı ve kullanıcı dostu web arayüzü sunar.

---

## 🏗️ Mimari ve RAG Akışı

```text
[Kullanıcı Sorgusu] 
     │
     ▼
[Embedding Modeli: qwen3-embedding-0.6b] ────► [Vektör Veritabanı: SQLite / chunks.db]
                                                              │
                                                              ▼ (Eşik: skor ≥ 0.5 olan chunk'lar)
                                                              │
[Yerel LLM: qwen2.5-7b] ◄─────────────────────────────────────┘
     │
     ▼
[Grounded Yanıt + Kaynak Gösterimi]
```

* **Ingestion (Veri Alımı):** Yerel `.txt` belgeleri okunur, paragraflara (chunk) bölünür, dosya adı chunk içine gömülür (retrieval kalitesini artırmak için) ve embedding'leri çıkarılarak `chunks.db` veritabanına kaydedilir.
* **Retrieval (Erişim):** Kullanıcı bir soru sorduğunda, sistem vektör benzerliği (Cosine Similarity) hesaplayarak en ilgili belge parçalarını getirir. Yalnızca **0.5 ve üzeri skora sahip** chunk'lar bir sonraki adıma taşınır; düşük skorlu chunk'lar context'e hiç girmez.
* **Generation (Üretim):** Getirilen parçalar bağlam (context) olarak `qwen2.5-7b` modeline dil-bazlı katı sistem promptu ile beslenir; model yalnızca bağlamdaki bilgiyle yanıt üretir, aksi halde "Bilmiyorum" der.

---

## 🛠️ Kullanılan Teknolojiler

* **Arayüz:** Streamlit (`week4_app.py`, `@st.cache_resource` optimizasyonu, form tabanlı input)
* **Yerel AI Altyapısı:** `foundry_local_sdk` (`FoundryLocalManager`, `Configuration`)
* **Yapay Zeka Modelleri:**
  * **Chat / Üretim:** `qwen2.5-7b` (`temperature=0.2`, `max_tokens=300`)
  * **Embedding:** `qwen3-embedding-0.6b`
* **Dil Tespiti & Metin İşleme:** `langdetect` (Türkçe/İngilizce otomatik yönlendirme), `re` (normalizasyon, döngü kırma, yapışık kelime ayırma)
* **Veritabanı:** SQLite (`chunks.db`)

## 🚀 Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları takip edebilirsiniz:

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/SUNAYILDIZ/yerel-rag-asistanim.git
   cd yerel-rag-asistanim
   ```
2. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Uygulamayı başlatın:**
   ```bash
   python -m streamlit run week4_app.py
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

Sistem, farklı soru kategorileriyle kapsamlı şekilde test edilmiştir. Özellikle son testlerde, retrieval (bilgiyi bulma) ve generation (bilgiyi kullanarak çıkarım yapma) katmanlarındaki hataların **birbirinden ayrıştırılması** hedeflenmiştir.

| # | Soru | Kategori | Beklenen | Sonuç | Not |
|---|------|----------|----------|-------|-----|
| 1 | n8n nedir ve ne işe yarar? | Cevaplanabilir | Doğru cevap | ✅ | — |
| 2 | What is n8n? | Cevaplanabilir (İngilizce) | İngilizce cevap | ✅ | `langdetect` ile dil tespiti |
| 3 | Gizlilik için neden n8n tercih edilmeli? | Çıkarım gerektiren | Doğru cevap | ✅ | Skor eşiğe yakın (0.513), sınırda ama başarılı |
| 4 | Is n8n a paid platform? | Cevaplanamaz | I don't know | ✅ | — |
| 5 | n8n hangi programlama dillerini destekler? | Cevaplanamaz | Bilmiyorum | ✅ | Chunk context'e girdi, model doğru şekilde bilgi eksikliğini fark etti |
| 6 | Warka Water nedir ve günde kaç litre üretir? | Cevaplanabilir | Doğru cevap | ✅ | — |
| 7 | Warka Water yapımında hangi malzemeler kullanılır? | Cevaplanabilir | Doğru cevap | ✅ | — |
| 8 | Warka Water ile n8n birlikte kullanılır mı? | Çapraz belge | Bilmiyorum | ✅ | Konular arası ilişkilendirme uydurulmadı |
| 9 | Ambalajları paraya dönüştürmek için ne yapmalıyım? | Dolaylı ifade | Doğru cevap | ❌ | **Retrieval hatası**: doğru chunk (%1 TL teşvik bedeli) veri tabanında var ama skor 0.3996, eşiğin (0.5) altında kaldı — embedding modeli dolaylı ifadeyi yakalayamadı |
| 10 | Kazanılan para nakit çekilebilir mi? | Dolaylı ifade | Doğru cevap | ❌ | Aynı retrieval sınırlaması; "kazanılan para" ifadesi belge terminolojisinden uzak |
| 11 | 5 litrelik damacana DOA'ya kabul edilir mi? | Negatif/karşılaştırmalı çıkarım | Hayır | ❌ | **Generation hatası**: doğru chunk (0.10–3 litre aralığı) skor 0.5828 ile context'e girdi, ama model "aralık dışı → hayır" çıkarımını yapamayıp "bilmiyorum" dedi |
| 12 | n8n ile DOA arasındaki farklar nelerdir? | Çapraz belge | "Belgede kıyaslama yok" | ✅ | Belgede doğrudan kıyaslama olmadığı için uydurma yanıt engellendi |
| 13 | Doğayı koruyan sistemler nelerdir? | Belirsiz/şemsiye kavram | Warka Water + DOA | ❌ | **Retrieval hatası**: sinyal birden fazla belgeye dağıldı (en yüksek skor 0.4570), hiçbir chunk eşiği geçemedi; Warka Water ilk 4'e bile girmedi |

### Tespit Edilen Sorunlar ve Çözümler

| Sorun | Çözüm |
|-------|-------|
| Model Çince cevap verdi | `langdetect` kütüphanesi ile dil tespiti eklendi |
| "Context'te belirtilmiştir" iç bilgisi sızdı | Sistem promptu dil-bazlı ve sıkı kurallarla ayrıştırıldı |
| Aynı kaynak iki kez listelendi | `seen_sources` yapısı ile tekrarlayan kaynaklar temizlendi |
| "IsePET" gibi yapışık kelimeler oluştu | `format_output` regex fonksiyonu eklendi |
| Parantez temizleme Türkçe cevaplarda da çalışıp geçerli içeriği siliyordu | `quick_clean` fonksiyonuna `user_lang` parametresi eklendi; parantez temizliği yalnızca İngilizce modda çalışıyor |
| Düşük skorlu chunk'lar context'e gürültü olarak gidiyordu | Yalnızca en iyi chunk değil, **her chunk tek tek** 0.5 eşiğine göre filtrelendi (`valid_chunks`) |
| "Bilmiyorum" tespiti cevabın herhangi bir yerinde geçen kelimeyle yanlış tetikleniyordu | Ayrı `is_no_answer()` fonksiyonu ile yalnızca cevabın başında/tamamında arama yapılıyor |
| Kaynak adı çıkarma (`split(":")[0]`) `:` içermeyen içerikte kırılgandı | `partition(":")` ile güvenli hale getirildi, `:` yoksa fallback |
| Her tuş vuruşunda script yeniden çalışıyordu | `st.text_input`, `st.form` içine alındı; sorgu yalnızca gönderim anında çalışıyor |

### ⚠️ Bilinen Limitler

Debug testleri sonucunda, sistemin hataları **iki farklı katmanda** ortaya çıktığı netleşmiştir:

1. **Retrieval (Erişim) Sınırlamaları** — embedding modeli, sorudaki dolaylı/günlük dil ifadelerini (örn. "ambalajları paraya dönüştürmek") belgedeki resmi terminolojiyle ("teşvik bedeli kazanırsın") yeterince güçlü eşleştiremiyor; skor 0.5 eşiğinin altında kalıyor. Belirsiz/şemsiye kavramlı sorularda (örn. "doğayı koruyan sistemler") sinyal birden fazla belgeye dağılıp hiçbiri eşiği geçemeyebiliyor.
2. **Generation (Üretim) Sınırlamaları** — doğru chunk context'e başarıyla girse bile, küçük yerel model (`qwen2.5-7b`) negatif veya karşılaştırmalı çıkarım gerektiren sorularda (örn. "5 litre, 0.10–3 litre aralığının dışında, o hâlde hayır") bu mantığı kurmakta zorlanıp güvenli tarafta kalarak "bilmiyorum" diyebiliyor.
3. Belge sayısı arttıkça retrieval kalitesinin artması beklenmektedir; az sayıda belgeyle çapraz belge karşılaştırma soruları retrieval kalitesini düşürebilir.
4. `qwen2.5-7b` modeli bazı sorularda Türkçe gramer hatası yapabilir.

**Olası iyileştirme yönleri (henüz uygulanmadı):**
- Retrieval sınırlaması için: query expansion / eş anlamlı zenginleştirme, ya da eşik değerinin (0.5) düşürülmesi (yanlış pozitif riskiyle birlikte).
- Generation sınırlaması için: sistem promptuna sayısal aralık/karşılaştırma çıkarımını teşvik eden açık bir talimat eklenmesi.

---

## 📜 Lisans
Bu proje kişisel ve kurumsal yerel RAG denemeleri için özgürce kullanılabilir.

* Dil Tespiti & Metin İşleme: langdetect (Otomatik Türkçe/İngilizce yönlendirme), re (Normalizasyon)

* Veritabanı: SQLite (chunks.db)

* Dil ve Paket Yönetimi: Python, Pip
