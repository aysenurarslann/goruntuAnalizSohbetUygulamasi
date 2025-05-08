#JSON/veritabanı işlemleri

# modules/data_storage.py
# Ayşenur Arslan - 16.04.2025

import json
import os
from datetime import datetime
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataStorage:
    def __init__(self, storage_file="data/history.json"):
        """Veri saklama sınıfı."""
        self.storage_file = storage_file
        
        # Klasörü oluştur (yoksa)
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        
        # Dosyayı kontrol et ve gerekirse oluştur
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def save_data(self, object_name, keywords, content):
        """Nesne, anahtar kelimeler ve içeriği kaydeder."""
        try:
            # Mevcut verileri oku
            current_data = self._read_data()
            
            # Yeni veriyi oluştur
            new_entry = {
                "timestamp": datetime.now().isoformat(),
                "object": object_name,
                "keywords": keywords,
                "content": content
            }
            
            # Veriyi ekle
            current_data.append(new_entry)
            
            # Veriyi kaydet
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Veri başarıyla kaydedildi: {object_name}")
            return True
            
        except Exception as e:
            logger.error(f"Veri kaydedilirken hata: {e}")
            return False
    
    def _read_data(self):
        """JSON dosyasından verileri okur."""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Veri okunurken hata: {e}")
            return []
    
    def get_previous_data(self, limit=5):
        """Son kaydedilen verileri döndürür."""
        data = self._read_data()
        return data[-limit:] if data else []