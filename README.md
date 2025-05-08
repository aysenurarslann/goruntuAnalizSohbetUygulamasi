# 🤖 Görüntü Analizi ve Sohbet Uygulaması

**Geliştirici:** Ayşenur Arslan  
**Tarih:** 16.04.2025

## 📌 1. Proje Özeti

Bu proje, kullanıcının sağladığı görüntülerdeki nesneleri tanımlayarak, bu nesnelerle ilgili bilgilerin web üzerinden araştırılıp sunulduğu bir yapay zeka uygulamasıdır. Uygulama, CLI (komut satırı arayüzü) üzerinden çalışır ve kullanıcı dostu bir deneyim sunar.

---

## 🎯 1.1 Amaç ve Kapsam

Projenin temel amacı, kullanıcıların görüntülerdeki nesneler hakkında hızlı ve kapsamlı bilgiye erişmesini sağlamaktır.

### Uygulamanın Temel İşlevleri:

- URL veya yerel dosyadan görüntü alma
- Nesne tespiti ve önceliklendirme
- Anahtar kelime çıkarımı
- Web araması ve içerik sunumu
- Sohbet geçmişi ile bağlamsal süreklilik

---

## 🔁 1.2 Kullanıcı Etkileşimi ve Akış Şeması

1. Kullanıcı görüntü URL’si veya dosya yolu girer  
2. Görüntü alınır ve ön işleme yapılır  
3. Nesneler tespit edilir, en belirgin nesne belirlenir  
4. Nesne adı Türkçe’ye çevrilir  
5. Anahtar kelimeler oluşturulur  
6. Web araması gerçekleştirilir  
7. İçerik çıkarılır ve sunulur  
8. Sonuçlar kaydedilir  
9. Yeni görüntü veya çıkış seçeneği sunulur

---

## 🛠️ 2. Teknik Altyapı

### 2.1 Programlama Dili ve Kütüphaneler

**Dil:** Python  
**Kütüphaneler:**

- `PIL` – Görüntü işleme
- `nltk`, `spaCy` – Doğal dil işleme
- `transformers` – Büyük dil modelleri
- `requests` – HTTP istekleri
- `ultralytics` – YOLOv8 nesne tanıma
- `fiftyone` – Görselleştirme ve veri yönetimi

### 2.2 Mimari Yapı

Modüler ve nesne yönelimli mimari:

- `main.py` – Uygulama giriş noktası
- `image_processor.py` – Görüntü alma ve ön işleme
- `object_detector.py` – Nesne tespiti
- `keyword_extractor.py` – Anahtar kelime çıkarımı
- `translator.py` – Çeviri işlemleri
- `web_searcher.py` – Web araması
- `data_storage.py` – Geçmiş veri yönetimi

---

## 🖼️ 3. Görüntü İşleme ve Nesne Tanıma

### 3.1 Görüntü İşleme

- URL ve dosya girişi desteği
- RGB dönüşümü, kontrast artırma (1.5x)
- Yeniden boyutlandırma: 640x640
- LANCZOS örnekleme

### 3.2 Nesne Tanıma (YOLOv8)

- **Model:** YOLOv8x ve özel eğitimli YOLOv8l
- **Veri seti:** Open Images (2000 örnek, 80/20 split)
- **Eğitim:** 100 epoch, Adam optimizer, LR: 0.001 → 0.01, çeşitli augmentasyonlar
- **Ensemble:** YOLOv8x (1.4 ağırlık), özel model (1.2 ağırlık)

#### Akıllı Önem Skoru

- Güven skoru (%25)
- Nesne boyutu (%25)
- Merkeze yakınlık (%15)
- Önemli nesne (%40 bonus)

#### Görsel İşaretleme

- Bounding box
- Ana nesne vurgusu
- Tespit edilen model ve skor gösterimi

---

## 🗝️ 4. Anahtar Kelime Çıkarımı

### 4.1 Yöntemler

- LLM (BERTurk, Transformers, cosine similarity)
- Kural tabanlı sistem (kategori & nitelik sözlükleri)
- NLP araçları: SpaCy, WordNet

### 4.2 Bağlamsal Zenginleştirme

- Önceki sorgu geçmişi tutulur (son 10)
- Kategorik benzerlik analizleri yapılır

### 4.3 Çoklu Dil Desteği

- `spaCy` modelleri: `en_core_web_md`, `tr_core_news_md`
- `sentence-transformers` çok dilli model yedeği

### 4.4 Hata Toleransı

- Alternatif yöntemlerle çalışabilirlik
- Varsayılan anahtar kelimelerle devam edebilme

---

## 🌐 5. Web Arama ve İçerik Çıkarımı

### 5.1 Web Arama Süreci

- Arama motorları: `Serper.dev`, `DuckDuckGo`
- Dil tercihi: Türkçe öncelikli
- Kategoriye göre özelleştirilmiş sorgular
- Arama geçmişi optimizasyonu

### 5.2 İçerik Çıkarımı

- Sayfa içeriğinden bilgi çıkarımı
- Otomatik özetleme (max 4000 karakter)
- HTML temizleme
- Wikipedia entegrasyonu
- NLP tabanlı özetleme

---

## 💾 6. Veri Yönetimi

### 6.1 Veri Yapısı

- JSON formatında veri
- Zaman damgası, nesne, anahtar kelime, içerik
- UTF-8 desteği

### 6.2 Özellikler

- Varsayılan dosya: `data/history.json`
- Otomatik dosya oluşturma
- Geçmiş veriye erişim

### 6.3 Hata Yönetimi

- Dosya hataları için try-except
- Log kayıtları

---

## 🌍 7. Çeviri İşlemleri

- İngilizce nesneler Türkçe’ye çevrilir
- Yerel sözlük: 300+ nesne adı
- Google Translate ve LibreTranslate API entegrasyonu
- Kategori tabanlı çeviri doğruluğu

---

## 🧑‍💻 8. Kullanıcı Arayüzü

- CLI tabanlı etkileşim
- `argparse` ile komut satırı parametreleri
- Emoji ve görsel bildirim desteği
- Kullanıcı yönlendirmesi ve hata mesajları

---

## 🧩 9. Hata Yönetimi ve Loglama

- Tüm modüllerde `try-except`
- Konsol ve dosya loglama
- Hatalarda kullanıcıya yönlendirme (yeniden dene/görüntü gir/çıkış)

---

## 📦 Ekler

### 📁 Ek 1: Kurulum

```bash
pip install pillow nltk spacy transformers requests ultralytics
python -m spacy download en_core_web_md
python -m spacy download tr_core_news_md



python main.py --source https://example.com/image.jpg
python main.py --source images/sample.jpg



goruntu_analizi_sohbet_uygulamasi/
├── main.py
├── modules/
│   ├── image_processor.py
│   ├── object_detector.py
│   ├── keyword_extractor.py
│   ├── translator.py
│   ├── web_searcher.py
│   └── data_storage.py
├── data/
│   └── history.json
├── models/
│   └── best.pt
├── app.log
└── egitilmis_yolo.ipynb


