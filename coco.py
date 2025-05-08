from ultralytics import YOLO

# Bu komut COCO128 veri setini indirir
model = YOLO("yolov8s.pt")
model.train(data="coco128.yaml", epochs=1)  # Sadece indirmek için epoch sayısını düşük tutabilirsiniz

