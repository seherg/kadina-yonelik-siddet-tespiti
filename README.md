# 🛡️ Gerçek Zamanlı Şiddet Tespiti

Bu proje, el hareketleriyle yardım sinyali veren bireylerin acil durumlarını **gerçek zamanlı olarak algılayan** bir sistemdir. Sistem; bilgisayar kamerası, özel eğitilmiş YOLO modeli ve bir FSM (Sonlu Durum Makinesi) kullanarak üç aşamalı bir el işareti sırasını izler:

**open_hand → thumb_in → closed_fingers**

![image](https://github.com/user-attachments/assets/2f387bd5-ed6a-4876-b270-62930f3218d0)

![image](https://github.com/user-attachments/assets/35b08828-84f9-44f9-86b7-fc8f1b868d60)


## 🚀 Özellikler

- 📹 Gerçek zamanlı kamera görüntüsü işleme
- 🧠 FSM ile sıralı hareket takibi
- 🔊 Alarm sesi ve görsel uyarı
- 💬 WebSocket ile anlık veri iletişimi
- 📦 SQLite veritabanına olay loglama
- 🎯 Kullanıcı dostu arayüz (HTML/CSS/JS)

---

## 📁 Proje Yapısı
violence-detection/

├── backend/

│   ├── alarm.py                 # Alarm sesi oynatımı

│   ├── database.py              # SQLite kayıt yönetimi

│   ├── detector.py              # YOLO + FSM ile hareket tespiti

│   ├── fsm.py                   # Yardım sinyali FSM sınıfı

│   ├── main.py                  # FastAPI uygulaması

│   ├── model_debug.py           # Model çıktısı test aracı (isteğe bağlı)

│   ├── requirements.txt         # Python bağımlılıkları

│   ├── websocket_handler.py     # WebSocket bağlantı yöneticisi

│   ├── __pycache__/             # Python önbellek klasörü

│   ├── models/                  # YOLO model dosyaları (.pt)

│

├── database/

│   └── alarms.db                # Yardım sinyali kayıtlarının tutulduğu SQLite veritabanı

│

├── frontend/

│   ├── alert.mp3                # Alarm sesi

│   ├── index.html               # Web arayüzü

│   ├── script.js                # Kamera ve FSM kontrolü + WebSocket

│   └── style.css                # Arayüz tasarımı

│

├── tests/

│   ├── test_detector.py         # YOLO tespitleri için test dosyası

│

├── videos/                      # Gelecekte kayıtlı videolar için kullanılabilir

│

└── README.md                    # Proje açıklaması


## ⚙️ Kurulum

### 1. Ortamı Hazırla

python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt

### 2. Sunucuyu başlat
python -m uvicorn backend.main:app --reload

### 3. Tarayıcıda Aç
http://127.0.0.1:8000/

## 🧪 Test İçin
Kamera erişimine izin verin.

El işaretini şu sırayla yapın:

🖐️ open_hand

👍 thumb_in

✊ closed_fingers

Başarılı tespitte sistem alarm verir 🔊

## 🗃️ Kayıtlar
Tespit edilen yardım sinyalleri database/alarms.db içinde şu bilgilerle saklanır:

timestamp (tarih/saat)

gesture sequence

confidence


## 🛠️ Kullanılan Teknolojiler
Python 3.13

FastAPI & Uvicorn

YOLOv8 (Ultralytics)

WebSocket

HTML5 + CSS3 + JS

SQLite3

# 👩‍💻 Geliştirici
Seher Gumusay
