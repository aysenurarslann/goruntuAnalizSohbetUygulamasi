# Görüntü işleme fonksiyonları
# Ayşenur ARSLAN -16.04.2025
# Importing necessary libraries
# modules/image processor.py
import os
import requests
from PIL import Image
from io import BytesIO
import logging    # Hata ve işlem kayıtlarını (log) tutmak için

#Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_url(source):
    """Verilen kaynağın URL mi yoksa dosya yolu mu olduğunu kontrol eder."""
    return source.startswith(('http://', 'https://'))


def is_url(source):
    """Verilen kaynağın URL mi yoksa dosya yolu mu olduğunu kontrol eder."""
    return source.startswith(('http://', 'https://'))

def get_image_from_source(source):
    """URL veya dosya yolundan görüntü yükler."""
    try:
        if is_url(source):
            logger.info(f"URL'den görüntü indiriliyor: {source}")
            response = requests.get(source, stream=True, timeout=10)
            response.raise_for_status()  # HTTP hatalarını kontrol et
            image = Image.open(BytesIO(response.content))
        else:
            logger.info(f"Dosyadan görüntü yükleniyor: {source}")
            if not os.path.exists(source):
                raise FileNotFoundError(f"Dosya bulunamadı: {source}")
            image = Image.open(source)
        
        # Görüntüyü RGB formatına dönüştür (model gereksinimleri için)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Görüntü indirilirken hata oluştu: {e}")
        raise
    except FileNotFoundError as e:
        logger.error(f"Dosya bulunamadı: {e}")
        raise
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        raise

def preprocess_image(image, target_size=(640, 640)):
    # Görüntü kontrastını artır
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)  # 1.5 kontrast artışı
    
    # Görüntüyü yeniden boyutlandır
    resized_image = image.resize(target_size, Image.LANCZOS)
    return resized_image