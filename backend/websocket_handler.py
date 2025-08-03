# backend/websocket_handler.py

import cv2
import base64
import numpy as np
from fastapi import WebSocket
from backend.detector import HandSignalDetector

detector = HandSignalDetector("backend/models/best.pt")

async def handle_websocket(websocket: WebSocket):
    await websocket.accept()
    print("📡 WebSocket bağlantısı kabul edildi")

    try:
        while True:
            data = await websocket.receive_json()
            if "image" not in data:
                print("⚠️ 'image' alanı eksik!")
                continue

            img_data = base64.b64decode(data["image"])
            np_arr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                print("⚠️ Görüntü çözülemedi!")
                continue

            results = detector.detect(frame)

            detections = []
            if results.boxes is not None and len(results.boxes) > 0:
                print("🔍 Tespit edilen sınıflar:")
                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = detector.model.names[cls_id]
                    print(f"👉 {class_name} ({conf:.2f})")

                    detections.append({
                        "class": class_name,
                        "confidence": conf
                    })
            else:
                print("👀 Hiçbir şey tespit edilmedi.")

            current_step = detector.fsm.current_step
            is_complete = detector.fsm.is_complete
            print(f"🧠 FSM Adımı: {current_step} | Tamamlandı mı? {is_complete}")

            if is_complete:
                status = "alarm"
                print("🚨 ALARM DURUMU - TÜM ADIMLAR TAMAMLANDI!")
            elif current_step > 0:
                status = "tracking"
            else:
                status = "idle"

            response = {
                "type": "detection",
                "data": {
                    "detections": detections,
                    "sequence_step": current_step,
                    "status": status
                }
            }
            await websocket.send_json(response)

            if is_complete:
                alarm_response = {
                    "type": "alarm",
                    "message": "Yardım sinyali algılandı!"
                }
                await websocket.send_json(alarm_response)

    except Exception as e:
        print("❌ WebSocket Hatası:", e)
