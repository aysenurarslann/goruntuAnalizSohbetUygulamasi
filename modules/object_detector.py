# Revize edilmiş object_detector.py - Ensemble ve Model Optimization Desteği ile
import logging
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, List, Dict, Any, Optional
import os
import numpy as np
import torch
# YOLOv8 için ultralytics kütüphanesini kullanma
from ultralytics import YOLO

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObjectDetector:
    def __init__(self, model_path=None, confidence_threshold=0.3, custom_model=False, device=None, 
                 ensemble=True, optimize=True):
        """
        Nesne tanıma modelini yükler.
        
        Args:
            model_path: Özel eğitilmiş model yolu (varsa)
            confidence_threshold: Güven eşiği
            custom_model: Özel model kullanılıp kullanılmadığı
            device: Modelin çalışacağı cihaz ('cuda', 'cpu' vs.)
            ensemble: Birden fazla modeli birleştirerek kullan (daha iyi sonuçlar için)
            optimize: Modeli optimize ederek hızlandır ve iyileştir
        """
        self.confidence_threshold = confidence_threshold
        self.custom_model = custom_model
        self.ensemble = ensemble
        self.optimize = optimize
        
        # Device kontrolü
        if device is None:
            # Otomatik device seçimi
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Model şu cihazda çalışacak: {self.device}")
        
        # İlgilenilen nesneler - görüntüde tespit edilirse öncelik verilecek
        self.priority_objects = [
            'shoe', 'handbag', 'backpack', 'bottle', 'cup', 'sandwich', 
            'laptop', 'cell phone', 'book', 'cake', 'chair', 'table',
            'pizza', 'suitcase', 'watch', 'tie', 'umbrella', 'tvmonitor',
            'keyboard', 'mouse', 'sports ball', 'camera'
        ]
        
        # Türkçe karşılıklar
        self.tr_priority_objects = [
            'ayakkabı', 'el çantası', 'sırt çantası', 'şişe', 'fincan', 'sandviç',
            'dizüstü bilgisayar', 'cep telefonu', 'kitap', 'pasta', 'sandalye', 'masa',
            'pizza', 'bavul', 'kol saati', 'kravat', 'şemsiye', 'televizyon',
            'klavye', 'fare', 'spor topu', 'kamera'
        ]
        
        try:
            # Modelleri yükle
            self.models = []
            
            # Eğer ensemble modu etkinse, birden fazla model yükle
            if self.ensemble:
                logger.info("Ensemble modu etkin: Birden fazla model kullanılacak")
                
                # Kendi eğitilmiş modelimizi yükle
                if model_path and os.path.exists(model_path):
                    logger.info(f"Colab'da eğitilmiş YOLOv8 modeli yükleniyor: {model_path}")
                    custom_model = YOLO(model_path)
                    self.models.append(custom_model)
                
                # Ön eğitimli modelleri yükle (farklı boyutlarda)
                pretrained_models = ['yolov8n.pt', 'yolov8s.pt']  # Nano ve Small model (hızlı ve etkili)
                
                for model_name in pretrained_models:
                    try:
                        logger.info(f"Ön eğitimli model yükleniyor: {model_name}")
                        model = YOLO(model_name)
                        self.models.append(model)
                    except Exception as e:
                        logger.warning(f"{model_name} yüklenirken hata: {e}")
            else:
                # Tek model modu
                if model_path and os.path.exists(model_path):
                    logger.info(f"Colab'da eğitilmiş YOLOv8 modeli yükleniyor: {model_path}")
                    self.models.append(YOLO(model_path))
                else:
                    default_model = 'yolov8s.pt'
                    logger.info(f"Model bulunamadı veya belirtilmedi. Varsayılan model yükleniyor: {default_model}")
                    self.models.append(YOLO(default_model))
            
            # Modelleri optimize et (hızlandırma ve iyileştirme)
            if self.optimize:
                for i, model in enumerate(self.models):
                    logger.info(f"Model {i+1} optimize ediliyor...")
                    # Half-precision için (eğer GPU varsa)
                    if 'cuda' in self.device:
                        model.model = model.model.half()
                    
                    # Modelin inference ayarlarını optimize et
                    model.conf = self.confidence_threshold  # Güven eşiği ayarı
                    model.iou = 0.45  # IoU eşiği
                    model.agnostic = True  # Sınıftan bağımsız NMS
                    model.multi_label = False  # Tek etiket modu
            
            # Tüm modelleri belirtilen cihaza taşı
            for model in self.models:
                model.to(self.device)
                
            logger.info(f"{len(self.models)} model başarıyla yüklendi.")
                
        except Exception as e:
            logger.error(f"Model yüklenirken hata: {e}")
            raise
    
    def detect_objects(self, image: Image.Image) -> Tuple[str, Image.Image]:
        """
        Görüntüdeki nesneleri tespit eder ve en önemli nesneyi belirler.
        
        Args:
            image: İşlenecek PIL görüntü nesnesi
            
        Returns:
            (en_önemli_nesne_adı, işaretlenmiş_görüntü) çifti
        """
        try:
            # Tüm tespitleri saklayacak liste
            all_detections = []
            
            # Tüm modellerden tahmin al
            for i, model in enumerate(self.models):
                logger.info(f"Model {i+1} ile tespit yapılıyor...")
                
                # Görüntü boyutunu ayarla (farklı modeller için farklı boyutlar)
                img_size = 640 if i == 0 else 320 + i * 160  # ilk model 640, sonraki modeller farklı boyutlar
                
                # YOLOv8 ile nesneleri tespit et
                results = model(image, imgsz=img_size, device=self.device)
                
                # İlk sonucu al
                result = results[0]
                
                # Debug için tüm sonuçları logla
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    name = result.names[cls_id] 
                    conf = float(box.conf[0])
                    logger.info(f"Model {i+1} Tespiti: {name} (Güven: {conf:.2f})")
                
                # Güven eşiğini geçen nesneleri filtrele
                for box in result.boxes:
                    if box.conf[0] >= self.confidence_threshold:
                        cls_id = int(box.cls[0])
                        object_name = result.names[cls_id]
                        confidence = float(box.conf[0])
                        
                        # Her modele göre güven skorunu ayarla
                        # Eğer özel modelimiz ise daha fazla ağırlık ver
                        if i == 0 and self.custom_model:
                            confidence *= 1.2  # Özel modele %20 bonus
                        
                        # Bounding box koordinatları
                        bbox = (
                            float(box.xyxy[0][0]), 
                            float(box.xyxy[0][1]),
                            float(box.xyxy[0][2]),
                            float(box.xyxy[0][3])
                        )
                        
                        # Nesne boyutu (görüntüye oranı)
                        box_width = bbox[2] - bbox[0]
                        box_height = bbox[3] - bbox[1]
                        box_area = box_width * box_height
                        image_area = image.width * image.height
                        relative_size = box_area / image_area
                        
                        # Nesne merkezinin koordinatları
                        center_x = (bbox[0] + bbox[2]) / 2
                        center_y = (bbox[1] + bbox[3]) / 2
                        
                        # Görüntü merkezine olan uzaklık
                        image_center_x = image.width / 2
                        image_center_y = image.height / 2
                        distance_to_center = ((center_x - image_center_x) ** 2 + 
                                             (center_y - image_center_y) ** 2) ** 0.5
                        
                        # Normalize edilmiş merkeze uzaklık (0-1 arası)
                        normalized_distance = distance_to_center / ((image.width/2)**2 + (image.height/2)**2)**0.5
                        
                        # Merkeze yakınlık skoru (0-1 arası, 1 en yakın)
                        center_score = 1 - normalized_distance
                        
                        # Nesne önemi skoru hesapla
                        importance_score = 0
                        
                        # Önemli nesne listesinde ise ekstra puan
                        if object_name.lower() in [x.lower() for x in self.priority_objects]:
                            importance_score += 0.4
                        
                        # Ana önem skorunu hesapla
                        importance_score += (
                            confidence * 0.2 +  # Güven skoru etkisi
                            relative_size * 0.25 +  # Boyut etkisi
                            center_score * 0.15  # Merkeze yakınlık etkisi
                        )
                        
                        # Model indeksine göre ağırlık ver
                        model_weight = 1.0
                        if self.ensemble:
                            # İlk model özel model ise daha fazla ağırlık ver
                            if i == 0 and self.custom_model:
                                model_weight = 1.3
                            else:
                                model_weight = 1.0 - (i * 0.1)  # Sonraki modellere azalan ağırlık
                        
                        importance_score *= model_weight
                        
                        # İnsan tespitinde daha düşük öncelik ver
                        if object_name.lower() == 'person':
                            # Eğer görüntünün büyük kısmını kaplıyorsa (muhtemelen ana nesne değil)
                            if relative_size > 0.4:
                                importance_score -= 0.3
                        
                        all_detections.append({
                            'name': object_name,
                            'confidence': confidence,
                            'bbox': bbox,
                            'relative_size': relative_size,
                            'center_score': center_score,
                            'importance_score': importance_score,
                            'model_index': i
                        })
            
            if not all_detections:
                logger.warning("Yeterli güven düzeyinde nesne tespit edilemedi!")
                return None, image
            
            # Ensemble sonuçlarını işleme
            if self.ensemble:
                # Tespitleri birleştir ve ortalama
                merged_detections = self._merge_detections(all_detections)
                all_detections = merged_detections
            
            # Debug: Tüm tespit edilen nesnelerin önem skorlarını göster
            for obj in all_detections:
                logger.info(f"Nesne: {obj['name']}, Önem skoru: {obj['importance_score']:.3f}, "
                           f"Boyut: {obj['relative_size']:.3f}, Merkez skoru: {obj['center_score']:.3f}")
            
            # En önemli nesneyi bul
            primary_object = max(all_detections, key=lambda x: x['importance_score'])
            
            # Tüm tespit edilen nesneleri işaretle, ana nesneyi vurgula
            marked_image = self._mark_objects(image, all_detections, primary_object)
            
            return primary_object['name'], marked_image
                
        except Exception as e:
            logger.error(f"Nesne tespiti sırasında hata: {e}")
            raise

    def _merge_detections(self, detections):
        """
        Farklı modellerden gelen tespitleri birleştirir ve benzer olanları ortalar.
        
        Args:
            detections: Farklı modellerden gelen tüm tespitler
            
        Returns:
            Birleştirilmiş tespit listesi
        """
        if not detections:
            return []
            
        # Tespitleri nesne adına göre gruplandır
        object_groups = {}
        for det in detections:
            obj_name = det['name']
            if obj_name not in object_groups:
                object_groups[obj_name] = []
            object_groups[obj_name].append(det)
        
        # Birleştirilmiş sonuçlar
        merged_results = []
        
        # Her nesne türü için
        for obj_name, obj_detections in object_groups.items():
            # Nesne çok az tespit edilmişse, güvenilir değildir - düşük güven
            if len(obj_detections) == 1 and len(self.models) > 1:
                obj_detections[0]['confidence'] *= 0.8
                merged_results.append(obj_detections[0])
                continue
                
            # Benzer bounding box'ları birleştir (IoU > 0.5 olanlar)
            remaining = obj_detections.copy()
            while remaining:
                base_det = remaining.pop(0)
                matches = []
                
                i = 0
                while i < len(remaining):
                    if self._calculate_iou(base_det['bbox'], remaining[i]['bbox']) > 0.5:
                        matches.append(remaining.pop(i))
                    else:
                        i += 1
                
                # Eşleşen tespitleri birleştir
                if matches:
                    # Tüm eşleşenleri ve baz tespiti birleştir
                    all_matches = [base_det] + matches
                    
                    # Ortalama güven skoru ve ağırlıklı bounding box hesapla
                    avg_conf = sum(d['confidence'] for d in all_matches) / len(all_matches)
                    
                    # Ağırlıklı bounding box (güven skoruna göre)
                    weighted_bbox = [0, 0, 0, 0]
                    total_weight = 0
                    
                    for d in all_matches:
                        weight = d['confidence']
                        total_weight += weight
                        for i in range(4):
                            weighted_bbox[i] += d['bbox'][i] * weight
                    
                    # Normalize
                    weighted_bbox = [coord / total_weight for coord in weighted_bbox]
                    
                    # Diğer özellikleri de ortalama
                    avg_size = sum(d['relative_size'] for d in all_matches) / len(all_matches)
                    avg_center = sum(d['center_score'] for d in all_matches) / len(all_matches)
                    
                    # En yüksek önem skorunu al (maksimum strateji)
                    max_importance = max(d['importance_score'] for d in all_matches)
                    
                    # Yeni birleştirilmiş tespit oluştur
                    merged_det = {
                        'name': obj_name,
                        'confidence': avg_conf * 1.1,  # Çoklu tespit bonusu
                        'bbox': tuple(weighted_bbox),
                        'relative_size': avg_size,
                        'center_score': avg_center,
                        'importance_score': max_importance * 1.15,  # Çoklu tespit bonusu
                        'model_index': -1  # Birleştirilmiş
                    }
                    
                    merged_results.append(merged_det)
                else:
                    # Eşleşme yoksa direkt ekle
                    merged_results.append(base_det)
        
        return merged_results
    
    def _calculate_iou(self, box1, box2):
        """
        İki bounding box arasındaki IoU (Intersection over Union) değerini hesaplar.
        
        Args:
            box1, box2: (x1, y1, x2, y2) formatında iki bounding box
            
        Returns:
            IoU değeri (0-1 arası)
        """
        # Kesişim alanını hesapla
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        # Eğer kesişim yoksa
        if x2 < x1 or y2 < y1:
            return 0.0
            
        intersection = (x2 - x1) * (y2 - y1)
        
        # Her iki kutunun alanını hesapla
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        # IoU = kesişim / birleşim
        union = box1_area + box2_area - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _mark_objects(self, image: Image.Image, objects: List[Dict[str, Any]], 
                    primary_object: Dict[str, Any]) -> Image.Image:
        """
        Tespit edilen tüm nesneleri işaretler, ana nesneyi vurgular.
        
        Args:
            image: İşaretlenecek görüntü
            objects: Tespit edilen tüm nesnelerin listesi
            primary_object: Ana nesne bilgileri
            
        Returns:
            İşaretlenmiş görüntü
        """
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        # Tüm nesneleri işaretle
        for obj in objects:
            # Ana nesneyi farklı renk ve kalınlıkta işaretle
            if obj == primary_object:
                color = "red"
                width = 3
                text_color = "white"
                bg_color = "red"
            else:
                color = "blue"
                width = 2
                text_color = "white"
                bg_color = "blue"
            
            # Kutu çiz
            draw.rectangle(obj['bbox'], outline=color, width=width)
            
            # Etiket için arka plan çiz
            conf_text = f"{obj['confidence']:.2f}"
            if 'model_index' in obj and obj['model_index'] >= 0:
                text = f"{obj['name']}: {conf_text} (M{obj['model_index']+1})"
            else:
                text = f"{obj['name']}: {conf_text} (E)"  # E = Ensemble
            
            try:
                font = ImageFont.truetype("arial.ttf", 15)
            except IOError:
                font = ImageFont.load_default()
                
            text_bbox = draw.textbbox((obj['bbox'][0], obj['bbox'][1]-20), text, font=font)
            draw.rectangle(text_bbox, fill=bg_color)
            
            # Etiketi ekle
            draw.text((obj['bbox'][0], obj['bbox'][1]-20), text, fill=text_color, font=font)
        
        return img_copy

    def analyze_image_composition(self, image: Image.Image) -> Dict[str, Any]:
        """
        Görüntü kompozisyonunu analiz eder.
        
        Args:
            image: Analiz edilecek görüntü
            
        Returns:
            Görüntü ile ilgili bilgiler
        """
        # Görüntü boyutları
        width, height = image.imgsz
        
        # Görüntü renk analizi
        if image.mode == 'RGB':
            # RGB değerlerini numpy dizisine dönüştür
            img_array = np.array(image)
            
            # Ortalama renk değerleri
            avg_color = img_array.mean(axis=(0, 1))
            
            # Parlaklık (0-255 arası)
            brightness = np.mean(avg_color)
            
            # Kontrast (standart sapma)
            contrast = np.std(img_array)
            
            return {
                'width': width,
                'height': height,
                'aspect_ratio': width / height,
                'avg_color': avg_color.tolist(),
                'brightness': brightness,
                'contrast': contrast
            }
        
        return {
            'width': width,
            'height': height,
            'aspect_ratio': width / height
        }