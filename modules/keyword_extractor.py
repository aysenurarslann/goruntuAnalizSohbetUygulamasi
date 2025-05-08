# modules/keyword_extractor.py
# Ayşenur Arslan - 16.04.2025
# Türkçe destek eklenmiş versiyon

import nltk
import spacy
from nltk.corpus import wordnet as wn
import logging

# Gerekli NLTK verilerini indir
try:
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
except Exception as e:
    pass  # İndirme hatası durumunda sessizce devam et

# SpaCy modellerini yükle
try:
    # İngilizce model
    nlp_en = spacy.load("en_core_web_md")
    
    # Türkçe model (varsa)
    try:
        nlp_tr = spacy.load("tr_core_news_md")
    except OSError:
        # Model yoksa indir (eğer varsa)
        import os
        try:
            os.system("python -m spacy download tr_core_news_md")
            nlp_tr = spacy.load("tr_core_news_md")
        except:
            logging.warning("Türkçe SpaCy modeli bulunamadı, alternatif yöntemler kullanılacak")
            nlp_tr = None
except OSError:
    # Model yoksa indir
    import os
    os.system("python -m spacy download en_core_web_md")
    nlp_en = spacy.load("en_core_web_md")
    nlp_tr = None

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeywordExtractor:
    def __init__(self, keyword_count=5):
        """Anahtar kelime çıkarıcı sınıfı."""
        self.keyword_count = keyword_count
        self.history = []  # Önceki anahtar kelimeler için geçmiş
        
        # Türkçe yaygın bağlantılı kelimeler sözlüğü
        self.tr_related_words = {
            "araba": ["otomobil", "taşıt", "araç", "vasıta", "sürüş"],
            "telefon": ["cep telefonu", "akıllı telefon", "iletişim", "arama", "mobil"],
            "bilgisayar": ["laptop", "masaüstü", "pc", "teknoloji", "yazılım"],
            "masa": ["mobilya", "çalışma", "yemek", "ofis", "ahşap"],
            "sandalye": ["oturma", "koltuk", "mobilya", "iskemle", "dinlenme"],
            "köpek": ["evcil hayvan", "dostluk", "sadakat", "havlama", "yavru"],
            "kedi": ["evcil hayvan", "miyav", "tüylü", "yumuşak", "sevimli"],
            "uçak": ["havacılık", "seyahat", "uçuş", "havayolu", "yolculuk"],
            "bisiklet": ["pedal", "spor", "ulaşım", "tekerlekli", "sürmek"],
            "insan": ["kişi", "birey", "toplum", "yaşam", "insan hakları"],
            # Daha fazla nesne ve ilişkili kelimeler eklenebilir
        }
        
    def generate_keywords(self, object_name, is_turkish=False):
        """Nesne adından anahtar kelimeler üretir."""
        try:
            keywords = set()

            # Nesne adı için kategori ve nitelik tanımlamaları
            object_categories = {
               # Giyim/Aksesuar
               "çanta": ["aksesuar", "moda", "taşıma"],
               "sırt çantası": ["aksesuar", "seyahat", "okul", "ergonomi"],
               "el çantası": ["moda", "aksesuar", "kadın"],
               "cüzdan": ["deri", "para", "kart", "taşıma"],
               "ayakkabı": ["giyim", "konfor", "moda"],
               "gözlük": ["aksesuar", "güneş", "optik"],
               "saat": ["aksesuar", "zaman", "bileklik"],
            
               # Yiyecek
               "sandviç": ["ekmek", "aperatif yemek", "lezzetli atıştırmalık"],
               "sosisli": ["sos", "sosis", "ketçap", "fast food"],
               "hamburger": ["köfte", "ekmek", "hızlı yemek"],
               "pizza": ["hamur işi", "İtalyan", "dilim"],
               "salata": ["sebze", "sağlıklı", "yeşillik"],
               "kahve": ["içecek", "kafein", "sıcak"],
            
               # Elektronik
               "telefon": ["akıllı telefon", "iletişim", "elektronik"],
               "bilgisayar": ["teknoloji", "yazılım", "donanım"],
               "tablet": ["taşınabilir", "ekran", "uygulama"],
               "televizyon": ["ekran", "yayın", "eğlence"],
               "kulaklık": ["ses", "müzik", "kablosuz"],
            
               # Mobilya
               "koltuk": ["oturma", "rahatlık", "salon"],
               "masa": ["çalışma", "yemek", "ahşap"],
               "sandalye": ["oturma", "destek", "ergonomik"],
            
               # Araçlar
               "araba": ["taşıt", "ulaşım", "motor", "yakıt"],
               "bisiklet": ["spor", "ulaşım", "pedal"],
               "motosiklet": ["hız", "motor", "iki teker"],
            
               # Hayvanlar
               "kedi": ["evcil hayvan", "miyav", "tüylü"],
               "köpek": ["evcil hayvan", "sadakat", "havlama"],
               "kuş": ["kanat", "uçmak", "tüy"],
               "balık": ["su", "yüz me", "akvaryum"],
               "at": ["binek", "sırt", "koşu"] 
               }
        
            # Sürüm kontrolü ve bağlam duyarlı eşleştirme
            object_lower = object_name.lower().strip()
            matched_object = None
        
            # Tam eşleşme veya kısmi eşleşme kontrol et
            if object_lower in object_categories:
               matched_object = object_lower
            else:
                # Kısmi eşleşme dene
                for obj in object_categories:
                    if obj in object_lower or object_lower in obj:
                        matched_object = obj
                        break
        
            # Eşleşme bulunduysa kategorilerini ekle
            if matched_object:
                keywords.update(object_categories[matched_object])
        
            # Eğer nesne adı Türkçe ise ve Türkçe özel işlem yap
            if is_turkish:
                # 1. Türkçe önceden tanımlanmış ilişkili kelimeler
                if object_lower in self.tr_related_words:
                    for related_word in self.tr_related_words[object_lower]:
                        keywords.add(related_word)
            
                # Bağlamsal zenginleştirme - Özel durumlar için
                if "çanta" in object_lower:
                   if "sırt" in object_lower:
                       keywords.update(["okul", "seyahat", "ergonomi", "dağcılık"])
                   elif "el" in object_lower:
                       keywords.update(["moda", "kadın", "aksesuar", "şık"])
                   elif "laptop" in object_lower or "bilgisayar" in object_lower:
                        keywords.update(["teknoloji", "taşıma", "koruma", "laptop"])
                    
                elif "sandviç" in object_lower:
                   keywords.update(["ekmek", "aperatif", "atıştırmalık", "lezzetli"])
                   if "sosisli" in object_lower:
                      keywords.update(["sos", "sosis", "ketçap", "fast food"])
                   elif "ton" in object_lower:
                       keywords.update(["balık", "ton balığı", "deniz ürünü"])
                   elif "peynir" in object_lower:
                       keywords.update(["kaşar", "çedar", "kahvaltılık"])
            
                # 2. Türkçe SpaCy modeli varsa kullan
                # (mevcut kodunuzu koruyun)
            
                 # 3. Türkçe anahtar kelimeler ekle - bunu zenginleştirelim
                if "çanta" in object_lower:
                    keywords.add("en iyi " + object_name + " modelleri")
                    keywords.add(object_name + " fiyatları")
                    keywords.add("kaliteli " + object_name)
                    keywords.add(object_name + " markaları")
                elif any(food in object_lower for food in ["yemek", "yiyecek", "sandviç", "pizza", "hamburger"]):
                    keywords.add(object_name + " tarifi")
                    keywords.add("kolay " + object_name + " yapımı")
                    keywords.add("pratik " + object_name)
                    keywords.add(object_name + " malzemeleri")
                else:
                    keywords.add(object_name + " nedir")
                    keywords.add(object_name + " özellikleri")
                    keywords.add(object_name + " türleri")
                    keywords.add(object_name + " kullanımı")
                    keywords.add(object_name + " hakkında")
            
                # Geçmiş sorguları dikkate alan gelişmiş bağlam oluşturma
                # Bir önceki sorgu ile bağlantı kurmaya çalış
                if self.history:
                    last_object_keywords = self.history[-1]
                    # Önceki nesne ile benzer kategoride mi kontrol et
                    for keyword in last_object_keywords:
                        if any(category in keyword for category in ["çanta", "giyim", "aksesuar"]) and "çanta" in object_lower:
                            keywords.add("modern " + object_name)
                            keywords.add(object_name + " kombinleri")
                        elif any(food in keyword for food in ["yemek", "sandviç", "tarif"]) and any(food in object_lower for food in ["sandviç", "yemek"]):
                              keywords.add("ev yapımı " + object_name)
                              keywords.add("hızlı " + object_name + " yapımı")
                
            else:
               # İngilizce için orijinal kod
               # (Mevcut kodunuz burada kalabilir)
               pass

            # Sonuçları filtrele ve sınırla
            filtered_keywords = [k for k in keywords if k != object_name and len(k) > 2]
            result = filtered_keywords[:self.keyword_count]

            # Eğer sonuç listesi boşsa veya çok az ise, varsayılan anahtar kelimeler ekle
            if len(result) < 3:
                if is_turkish:
                     result.extend([
                          object_name + " nedir", 
                          object_name + " özellikleri", 
                          object_name + " kullanımı",
                          object_name + " hakkında bilgi",
                          object_name + " türleri"
                     ])
                else:
                    result.extend([
                        object_name + " types", 
                        object_name + " uses", 
                        object_name + " features",
                        object_name + " about",
                        object_name + " information"
                    ])
                # Tekrar eden öğeleri kaldır ve limitle
                result = list(set(result))[:self.keyword_count]
   
            # Geçmişe ekle
            self.history.append(set(result))
            if len(self.history) > 10:  # Maksimum 10 geçmiş öğesi tut
                self.history.pop(0)

            logger.info(f"Üretilen anahtar kelimeler ({('Türkçe' if is_turkish else 'İngilizce')}): {result}")
            return result

        except Exception as e:
            logger.error(f"Anahtar kelime üretilirken hata: {e}")
            # Hata durumunda basit bir yöntemle devam et
            if is_turkish:
                return [object_name + " nedir", object_name + " özellikleri", object_name + " kullanımı", 
                       object_name + " bilgi", object_name + " türleri"]
            else:
                return [object_name + " types", object_name + " uses", object_name + " features", 
                       object_name + " about", object_name + " information"]