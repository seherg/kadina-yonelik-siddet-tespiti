# test_detector.py (geçici dosya/test için)
from backend.detector import HandSignalDetector

detector = HandSignalDetector("backend/models/best.pt")
detector.run_camera()
