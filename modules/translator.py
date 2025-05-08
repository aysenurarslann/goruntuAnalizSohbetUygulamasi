# modules/translator.py
import requests
from deep_translator import GoogleTranslator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Translator:
    def __init__(self):
        """İngilizce-Türkçe çeviri sınıfı."""
        # YOLOv8'in tanıyabildiği yaygın nesnelerin Türkçe karşılıkları
        self.common_objects = {
            # İnsanlar ve Kişiler
    "person": "insan",
    "people": "insanlar",
    "man": "adam",
    "woman": "kadın",
    "child": "çocuk",
    "baby": "bebek",
    "girl": "kız",
    "boy": "erkek çocuk",
    
    # Taşıtlar
    "bicycle": "bisiklet",
    "car": "araba",
    "motorcycle": "motosiklet",
    "airplane": "uçak",
    "bus": "otobüs",
    "train": "tren",
    "truck": "kamyon",
    "boat": "tekne",
    "ship": "gemi",
    "helicopter": "helikopter",
    "skateboard": "kaykay",
    "scooter": "skuter",
    "taxi": "taksi",
    "ambulance": "ambulans",
    "fire truck": "itfaiye aracı",
    "police car": "polis arabası",
    "van": "minibüs",
    "trailer": "römork",
    "tractor": "traktör",
    "bicycle": "bisiklet",
    
    # Mobilya ve Ev Eşyaları
    "chair": "sandalye",
    "table": "masa",
    "sofa": "kanepe",
    "bed": "yatak",
    "couch": "koltuk",
    "toilet": "tuvalet",
    "sink": "lavabo",
    "bathtub": "küvet",
    "mirror": "ayna",
    "clock": "saat",
    "vase": "vazo",
    "lamp": "lamba",
    "bookcase": "kitaplık",
    "shelf": "raf",
    "cabinet": "dolap",
    "desk": "çalışma masası",
    "door": "kapı",
    "window": "pencere",
    "carpet": "halı",
    "pillow": "yastık",
    "blanket": "battaniye",
    "curtain": "perde",
    
    # Elektronik Cihazlar
    "laptop": "dizüstü bilgisayar",
    "computer": "bilgisayar",
    "phone": "telefon",
    "cell phone": "cep telefonu",
    "mobile phone": "cep telefonu",
    "smartphone": "akıllı telefon",
    "keyboard": "klavye",
    "mouse": "fare",
    "remote": "kumanda",
    "tv": "televizyon",
    "monitor": "monitör",
    "microwave": "mikrodalga fırın",
    "oven": "fırın",
    "toaster": "tost makinesi",
    "refrigerator": "buzdolabı",
    "washing machine": "çamaşır makinesi",
    "dishwasher": "bulaşık makinesi",
    "printer": "yazıcı",
    "camera": "kamera",
    "speaker": "hoparlör",
    "headphones": "kulaklık",
    "projector": "projektör",
    "vacuum cleaner": "elektrikli süpürge",
    "fan": "vantilatör",
    "air conditioner": "klima",
    
    # Hayvanlar
    "dog": "köpek",
    "cat": "kedi",
    "horse": "at",
    "sheep": "koyun",
    "cow": "inek",
    "elephant": "fil",
    "bear": "ayı",
    "zebra": "zebra",
    "giraffe": "zürafa",
    "bird": "kuş",
    "chicken": "tavuk",
    "duck": "ördek",
    "penguin": "penguen",
    "fish": "balık",
    "turtle": "kaplumbağa",
    "hamster": "hamster",
    "rabbit": "tavşan",
    "mouse": "fare",
    "frog": "kurbağa",
    "snake": "yılan",
    "monkey": "maymun",
    "lion": "aslan",
    "tiger": "kaplan",
    "deer": "geyik",
    "fox": "tilki",
    "squirrel": "sincap",
    "butterfly": "kelebek",
    "spider": "örümcek",
    
    # Mutfak Eşyaları ve Gıda
    "bottle": "şişe",
    "cup": "fincan",
    "glass": "bardak",
    "fork": "çatal",
    "knife": "bıçak",
    "spoon": "kaşık",
    "bowl": "kase",
    "plate": "tabak",
    "pot": "tencere",
    "pan": "tava",
    "apple": "elma",
    "banana": "muz",
    "orange": "portakal",
    "pizza": "pizza",
    "cake": "pasta",
    "bread": "ekmek",
    "sandwich": "sandviç",
    "carrot": "havuç",
    "hot dog": "sosis",
    "donut": "donut",
    "cookie": "kurabiye",
    "broccoli": "brokoli",
    "tomato": "domates",
    "potato": "patates",
    "wine glass": "şarap kadehi",
    "coffee": "kahve",
    "tea": "çay",
    
    # Kıyafet ve Aksesuarlar
    "backpack": "sırt çantası",
    "umbrella": "şemsiye",
    "handbag": "el çantası",
    "tie": "kravat",
    "suitcase": "bavul",
    "hat": "şapka",
    "cap": "kep",
    "shoe": "ayakkabı",
    "boot": "çizme",
    "shirt": "gömlek",
    "t-shirt": "tişört",
    "jacket": "ceket",
    "coat": "palto",
    "dress": "elbise",
    "pants": "pantolon",
    "jeans": "kot pantolon",
    "shorts": "şort",
    "skirt": "etek",
    "glove": "eldiven",
    "sock": "çorap",
    "scarf": "eşarp",
    "belt": "kemer",
    "watch": "kol saati",
    "glasses": "gözlük",
    "sunglasses": "güneş gözlüğü",
    "wallet": "cüzdan",
    "ring": "yüzük",
    "necklace": "kolye",
    "bracelet": "bilezik",
    
    # Spor ve Eğlence
    "ball": "top",
    "frisbee": "frizbi",
    "kite": "uçurtma",
    "baseball bat": "beyzbol sopası",
    "baseball glove": "beyzbol eldiveni",
    "skateboard": "kaykay",
    "surfboard": "sörf tahtası",
    "tennis racket": "tenis raketi",
    "basketball": "basketbol topu",
    "football": "futbol topu",
    "volleyball": "voleybol topu",
    "tennis ball": "tenis topu",
    "baseball": "beyzbol topu",
    "golf ball": "golf topu",
    "ski": "kayak",
    "snowboard": "snowboard",
    "bicycle": "bisiklet",
    "gym equipment": "spor aleti",
    "dumbbell": "dambıl",
    "treadmill": "koşu bandı",
    "swimming pool": "yüzme havuzu",
    "playground": "oyun alanı",
    
    # Dış Mekan ve Yapılar
    "traffic light": "trafik ışığı",
    "street sign": "sokak tabelası",
    "stop sign": "dur tabelası",
    "parking meter": "parkmetre",
    "fire hydrant": "yangın musluğu",
    "bench": "bank",
    "tree": "ağaç",
    "flower": "çiçek",
    "grass": "çimen",
    "mountain": "dağ",
    "river": "nehir",
    "lake": "göl",
    "sea": "deniz",
    "sky": "gökyüzü",
    "cloud": "bulut",
    "sun": "güneş",
    "moon": "ay",
    "star": "yıldız",
    "building": "bina",
    "house": "ev",
    "apartment": "apartman",
    "bridge": "köprü",
    "fountain": "çeşme",
    "statue": "heykel",
    "tower": "kule",
    "skyscraper": "gökdelen",
    "road": "yol",
    "sidewalk": "kaldırım",
    "crosswalk": "yaya geçidi",
    
    # Ofis ve Eğitim
    "book": "kitap",
    "notebook": "defter",
    "paper": "kağıt",
    "pen": "kalem",
    "pencil": "kurşun kalem",
    "scissors": "makas",
    "ruler": "cetvel",
    "eraser": "silgi",
    "calculator": "hesap makinesi",
    "backpack": "sırt çantası",
    "briefcase": "evrak çantası",
    "stapler": "zımba",
    "file": "dosya",
    "folder": "klasör",
    "whiteboard": "beyaz tahta",
    "blackboard": "kara tahta",
    "projector": "projektör",
    "map": "harita",
    "globe": "küre",
    "calendar": "takvim",
    "card": "kart",
    "envelope": "zarf",
    "stamp": "pul",
    "document": "belge",
    
    # Müzik ve Sanat
    "guitar": "gitar",
    "piano": "piyano",
    "violin": "keman",
    "drum": "davul",
    "flute": "flüt",
    "trumpet": "trompet",
    "saxophone": "saksafon",
    "microphone": "mikrofon",
    "musical instrument": "müzik aleti",
    "painting": "tablo",
    "sculpture": "heykel",
    "canvas": "tuval",
    "brush": "fırça",
    "palette": "palet",
    "easel": "şövale",
    
    # Sağlık ve Tıp
    "stethoscope": "stetoskop",
    "syringe": "şırınga",
    "wheelchair": "tekerlekli sandalye",
    "crutch": "koltuk değneği",
    "bandage": "bandaj",
    "pill": "hap",
    "medicine": "ilaç",
    "thermometer": "termometre",
    "mask": "maske",
    "gloves": "eldivenler",
    
    # Teknoloji ve Bilim
    "robot": "robot",
    "drone": "drone",
    "microscope": "mikroskop",
    "telescope": "teleskop",
    "satellite": "uydu",
    "laboratory": "laboratuvar",
    "circuit": "devre",
    "battery": "pil",
    "solar panel": "güneş paneli",
    "antenna": "anten",
    "wire": "kablo",
    "chip": "çip",
    
    # Diğer
    "fire": "ateş",
    "smoke": "duman",
    "water": "su",
    "money": "para",
    "coin": "madeni para",
    "key": "anahtar",
    "padlock": "asma kilit",
    "scissors": "makas",
    "toothbrush": "diş fırçası",
    "hair drier": "saç kurutma makinesi",
    "broom": "süpürge",
    "candle": "mum",
    "gift": "hediye",
    "toy": "oyuncak",
    "teddy bear": "oyuncak ayı",
    "doll": "bebek",
    "puzzle": "yapboz",
    "box": "kutu",
    "package": "paket",
    "sign": "tabela",
    "flag": "bayrak",
    "trash can": "çöp kutusu",
    "recycle bin": "geri dönüşüm kutusu"
        }
    def translate(self, text, from_lang="en", to_lang="tr"):
        """Metni İngilizce'den Türkçe'ye çevirir."""
        try:
            # Önce sözlükte ara (daha hızlı)
            if text.lower() in self.common_objects:
                return self.common_objects[text.lower()]
            
            # Sözlükte yoksa Google Translate kullan
            try:
                translated = GoogleTranslator(source=from_lang, target=to_lang).translate(text)
                return translated
            except Exception as e:
                logger.warning(f"Google çeviri hatası: {e}, alternatif metot deneniyor")
                
                # Alternatif olarak başka bir çeviri metodu kullanın
                # Örneğin: LibreTranslate (ücretsiz, API key gerektirmez)
                try:
                    url = "https://libretranslate.de/translate"
                    params = {
                        "q": text,
                        "source": from_lang,
                        "target": to_lang
                    }
                    response = requests.post(url, data=params, timeout=5)
                    if response.status_code == 200:
                        return response.json()["translatedText"]
                except Exception as e2:
                    logger.error(f"Alternatif çeviri hatası: {e2}")
            
            # Hiçbir çeviri çalışmazsa orijinal metni döndür
            return text
            
        except Exception as e:
            logger.error(f"Çeviri sırasında hata: {e}")
            return text  # Hata durumunda orijinal metni döndür