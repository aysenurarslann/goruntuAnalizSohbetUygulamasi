# tests/test_image_processor.py
# Ayşenur Arslan - 16.04.2025

import unittest
from unittest.mock import patch, MagicMock
from PIL import Image
import io
import sys
import os

# Ana dizini ekle (relative import'lar için)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.image_processor import is_url, get_image_from_source, preprocess_image

class TestImageProcessor(unittest.TestCase):
    def test_is_url(self):
        # URL doğru tespit edilmeli
        self.assertTrue(is_url("http://example.com/image.jpg"))
        self.assertTrue(is_url("https://example.com/image.jpg"))
        
        # Dosya yolları URL olarak algılanmamalı
        self.assertFalse(is_url("/path/to/image.jpg"))
        self.assertFalse(is_url("C:\\Users\\images\\photo.png"))
    
    @patch('modules.image_processor.requests.get')
    def test_get_image_from_url(self, mock_get):
        # Mock response hazırla
        mock_response = MagicMock()
        mock_response.content = b'fake image data'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # PIL.Image.open'ı taklit et
        with patch('modules.image_processor.Image.open') as mock_open:
            mock_image = MagicMock(spec=Image.Image)
            mock_image.mode = 'RGB'
            mock_open.return_value = mock_image
            
            # Test
            result = get_image_from_source("https://example.com/image.jpg")
            
            # Assertions
            mock_get.assert_called_once_with("https://example.com/image.jpg", stream=True, timeout=10)
            mock_response.raise_for_status.assert_called_once()
            mock_open.assert_called_once()
            self.assertEqual(result, mock_image)
    
    def test_preprocess_image(self):
        # Test görüntüsü oluştur
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # İşleme fonksiyonunu çağır
        result = preprocess_image(test_image, target_size=(640, 640))
        
        # Sonuçları kontrol et
        self.assertEqual(result.size, (640, 640))
        self.assertEqual(result.mode, test_image.mode)

if __name__ == '__main__':
    unittest.main()