#main.py
# Ayşenur Arslan - 16.04.2025

import argparse
import os
import sys
from PIL import Image
import logging
from modules.translator import Translator  
# Modülleri içeri aktar
from modules.image_processor import get_image_from_source, preprocess_image
from modules.object_detector import ObjectDetector
from modules.keyword_extractor import KeywordExtractor
from modules.web_searcher import WebSearcher
from modules.data_storage import DataStorage

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    # Argüman ayrıştırıcıyı ayarla
    parser = argparse.ArgumentParser(description="Görüntü Analizi ve Sohbet Uygulaması")
    parser.add_argument("--source", "-s", help="Görüntü URL'si veya dosya yolu (isteğe bağlı)")
    args = parser.parse_args()
    
    # Özel eğitilmiş modeli kullan
    model_path = "D:\Masaüstü\goruntu_analizi_sohbet_uygulamasi\models\best.pt"  # Modelinizin tam yolu
    
    # Nesneleri başlat - özel model kullanımı için parametreleri geçir
    object_detector = ObjectDetector(
    model_path=model_path, 
    custom_model=True, 
    confidence_threshold=0.3,
    ensemble=True,  # Ensemble (birleştirme) modelini etkinleştir
    optimize=True   # Model optimizasyonunu etkinleşti
    
    )
    keyword_extractor = KeywordExtractor()
    translator = Translator()  # Çeviri nesnesi
    web_searcher = WebSearcher()
    data_storage = DataStorage()
    
    print("=" * 50)
    print("Görüntü Analizi ve Sohbet Uygulaması")
    print("=" * 50)
    
    # Komut satırı argümanı yoksa kullanıcıdan al
    source = args.source
    if not source:
        source = input("Görüntü URL'si veya dosya yolu girin: ")
    
    # Ana uygulama döngüsü
    while True:
        try:
            # Görüntüyü al
            print(f"\nGörüntü yükleniyor: {source}")
            image = get_image_from_source(source)
            processed_image = preprocess_image(image)
            
            # Nesne tespiti
            print("Görüntü analiz ediliyor...")
            object_name, marked_image = object_detector.detect_objects(processed_image)
            
            if not object_name:
                print("Görüntüde tanımlanabilir bir nesne bulunamadı! Lütfen başka bir görüntü deneyin.")
                source = input("\nYeni bir görüntü URL'si veya dosya yolu girin: ")
                continue
            
            # İngilizce nesne adını Türkçe'ye çevir
            tr_object_name = translator.translate(object_name)
            print(f"\n✓ Tespit edilen nesne: {object_name} (Türkçesi: {tr_object_name})")
            
            # İsteğe bağlı: işaretlenmiş görüntüyü kaydet
            marked_image.save("detected_object.jpg")
            print("(İşaretlenmiş görüntü 'detected_object.jpg' olarak kaydedildi)")
            
            # Anahtar kelime üretme
            keywords = keyword_extractor.generate_keywords(tr_object_name, is_turkish=True)
            print(f"✓ Anahtar kelimeler: {', '.join(keywords)}")
            
            # Web'de arama
            print("\nWeb'de bilgi aranıyor...")
            search_results = web_searcher.search_web(tr_object_name, keywords, lang="tr")

            if not search_results:
               print("Web'de arama sonucu bulunamadı!")
               source = input("\nYeni bir görüntü URL'si veya dosya yolu girin (çıkmak için 'q'): ")
               if source.lower() == 'q':
                  break
               continue
               
            # İçerik çıkarma - object_name ve keywords parametrelerini geçirerek zenginleştir
            content = web_searcher.extract_content(search_results, tr_object_name)
           
            # Sonuçları göster
            print("\n" + "=" * 50)
            print(f" '{object_name}' HAKKINDA BİLGİLER ")
            print("=" * 50)
            print(content)
            print("=" * 50)
            
            # Veri saklama
            data_storage.save_data(object_name, keywords, content)
            print("✓ Sonuçlar başarıyla kaydedildi!")
            
            # Yeni görüntü için sorgu
            source = input("\nYeni bir görüntü URL'si veya dosya yolu girin (çıkmak için 'q'): ")
            if source.lower() == 'q':
                break
                
        except Exception as e:
            logger.error(f"Program hatası: {e}")
            print(f"\nBir hata oluştu: {e}")
            retry = input("Tekrar denemek için 'r', yeni bir görüntü için URL/dosya yolu girin, çıkmak için 'q': ")
            if retry.lower() == 'q':
                break
            elif retry.lower() == 'r':
                # Aynı kaynakla tekrar dene
                continue
            else:
                # Yeni kaynak
                source = retry

if __name__ == "__main__":
    main()