# 🛡️ Gerçek Zamanlı Şiddet Tespiti

Bu proje, el işaretleri aracılığıyla yardım sinyali veren bireylerin acil durumlarını **gerçek zamanlı** olarak algılayan bir sistem sunar. Sistem; bilgisayar kamerası, özel eğitilmiş YOLO modeli, bir FSM (Sonlu Durum Makinesi), WebSocket tabanlı iletişim ve sesli/görsel uyarılarla çalışır. Kullanıcı aşağıdaki üç aşamalı el işareti dizisini gerçekleştirdiğinde:

**open\_hand → thumb\_in → closed\_fingers**
<img width="1884" height="844" alt="image" src="https://github.com/user-attachments/assets/f7568d5e-bf1e-4f18-9066-7df5948d9ab5" />


* Sistem önce alarm sesi çalar ve ekranda görsel bir uyarı gösterir.
* Ardından otomatik olarak 10 saniyelik bir WebM video kaydı başlatır ve kaydın tamamlanmasının ardından indirme linki sağlar.
* Tüm olayı `SQLite` veritabanına kaydeder.

## 🚀 Özellikler

* 📹 Gerçek zamanlı kamera görüntüsü işleme
* 🧠 FSM ile sıralı hareket takibi
* 🔊 Alarm sesi ve görsel uyarı
* 🎬 Otomatik 10 saniyelik video kaydı ve indirme linki
* 💬 WebSocket ile anlık veri aktarımı
* 📦 `SQLite` veritabanına tespit loglama
* 🖱️ Başlat butonu sayesinde tarayıcı izinlerinin otomatik yönetimi
* 🎨 Responsive ve kullanıcı dostu arayüz (HTML5, CSS3, JavaScript)

---

## ⚙️ Kurulum

1. **Ortamı Hazırla**

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```
2. **Sunucuyu Başlat**

   ```bash
   uvicorn backend.main:app --reload
   ```
3. **Tarayıcıda Uygulamayı Aç**

   ```
   http://127.0.0.1:8000/
   ```

## 🧪 Nasıl Test Edilir?

1. Sayfada **Uygulamayı Başlat** butonuna tıklayarak kamera, ses ve kayıt izinlerini verin.
2. El işaretlerini şu sırayla yapın:

   1. 🖐️ **open\_hand**
   2. 👍 **thumb\_in**
   3. ✊ **closed\_fingers**
3. Başarılı tespitte:

   * Sistem alarm sesi çalar ve görsel uyarı gösterir.
   * 10 saniyelik video kaydı otomatik başlatılır, ardından indirme linki ekranda belirir.

## 🗃️ Kayıtlar

Tespit edilen olaylar `database/alarms.db` dosyasında şu bilgilerle saklanır:

* **timestamp** (tarih ve saat)
* **sequence** (hareket dizisi)
* **confidence** (güven skoru)

## 🛠️ Kullanılan Teknolojiler

* Python 3.13
* FastAPI & Uvicorn
* YOLOv8 (Ultralytics)
* WebSocket API
* MediaRecorder API (WebM video kaydı)
* HTML5, CSS3, JavaScript
* SQLite3

## 👩‍💻 Geliştirici

Seher Gumusay
