# backend/detector.py

import cv2
from ultralytics import YOLO
from backend.fsm import HelpSignalFSM
from backend.alarm import trigger_alarm
from backend.database import save_alarm

class HandSignalDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.fsm = HelpSignalFSM()
    
    def detect(self, frame):
        results = self.model(frame, conf=0.3)  # Güven eşiğini düşür
        
        # Tüm tespitleri yazdır
        print(f"🔍 Toplam tespit: {len(results[0].boxes) if results[0].boxes is not None else 0}")
        
        # En yüksek güven skoruna sahip tespit
        if results[0].boxes is not None and len(results[0].boxes) > 0:
            best_detection = None
            best_confidence = 0
            
            for box in results[0].boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id]
                print(f"  - {class_name}: {conf:.3f}")
                
                if conf > best_confidence:
                    best_confidence = conf
                    best_detection = box
            
            if best_detection is not None and best_confidence > 0.3:  # Minimum güven
                cls_id = int(best_detection.cls[0])
                class_name = self.model.names[cls_id]
                
                print(f"🎯 En iyi tespit: {class_name} ({best_confidence:.3f})")
                
                # FSM'e gönder
                if self.fsm.update(class_name):
                    print("🚨 ALARM TETİKLENDİ!")
                    trigger_alarm()
                save_alarm(
                sequence=" -> ".join(self.fsm.sequence),
                confidence=best_confidence,
                video_name=""  # ileride kaydedeceksen buraya dosya adını yaz
            )

        return results[0]