# model_debug.py - Model sınıflarını kontrol etmek için

from ultralytics import YOLO

# Modelinizi yükleyin - doğru yol
model = YOLO("models/best.pt")

# Sınıf isimlerini yazdırın
print("📋 Model sınıf isimleri:")
for i, class_name in model.names.items():
    print(f"  {i}: {class_name}")

print("\n🔍 FSM'de beklenen sınıflar:")
expected_classes = ['open_hand', 'thumb_in', 'closed_fingers']
for cls in expected_classes:
    print(f"  - {cls}")

print("\n✅ Eşleşen sınıflar:")
for cls in expected_classes:
    if cls in model.names.values():
        print(f"  ✓ {cls}")
    else:
        print(f"  ❌ {cls}")

# Benzer isimleri kontrol et
print("\n🔍 Benzer isimler:")
all_classes = list(model.names.values())
for expected in expected_classes:
    similar = [cls for cls in all_classes if expected.lower() in cls.lower() or cls.lower() in expected.lower()]
    if similar:
        print(f"  {expected} için benzer: {similar}")