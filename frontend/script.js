let socket;
let currentStep = -1;

// 📸 Video akışını başlat - sadece mevcut elementi al
const video = document.getElementById("video-stream");

navigator.mediaDevices.getUserMedia({ video: true, audio: false })
    .then(stream => {
        video.srcObject = stream;
        console.log("✅ Kamera başarıyla açıldı");
    })
    .catch(err => {
        console.error("❌ Kamera erişim hatası:", err);
        alert("Kamera erişimi reddedildi. Lütfen tarayıcı ayarlarından kameraya izin verin.");
    });

const statusText = document.getElementById("status-text");
const fsmSteps = [
    document.getElementById("step-0"),
    document.getElementById("step-1"),
    document.getElementById("step-2")
];
const detectionsList = document.getElementById("detections");
const alarmSound = document.getElementById("alarm-sound");

// Ses dosyası yükleme kontrolü
alarmSound.addEventListener('loadeddata', () => {
    console.log("✅ Ses dosyası başarıyla yüklendi");
});

alarmSound.addEventListener('error', (e) => {
    console.error("❌ Ses dosyası yükleme hatası:", e);
    console.log("🔍 Ses dosyası yolu:", alarmSound.src);
});

// Ses dosyasını test et
alarmSound.load();

function updateFSM(step) {
    for (let i = 0; i < fsmSteps.length; i++) {
        fsmSteps[i].classList.remove("active", "done");
        if (i < step) {
            fsmSteps[i].classList.add("done");
        } else if (i === step) {
            fsmSteps[i].classList.add("active");
        }
    }
}

function updateStatus(mode) {
    statusText.classList.remove("status-idle", "status-tracking", "status-alarm");
    if (mode === "idle") {
        statusText.textContent = "Bekleniyor";
        statusText.classList.add("status-idle");
    } else if (mode === "tracking") {
        statusText.textContent = "Takip Ediliyor";
        statusText.classList.add("status-tracking");
    } else if (mode === "alarm") {
        statusText.textContent = "🚨 ALARM!";
        statusText.classList.add("status-alarm");
        console.log("🚨 ALARM TETİKLENDİ!");
        
        // Ses dosyası kontrolü ve çalma
        if (alarmSound) {
            console.log("🔊 Ses dosyası bulundu, çalıyor...");
            alarmSound.currentTime = 0; // Baştan başlat
            alarmSound.play().then(() => {
                console.log("✅ Ses başarıyla çalıyor");
            }).catch(err => {
                console.error("❌ Ses çalınamadı:", err);
                // Alternatif alarm - tarayıcı sesi
                console.log("🔔 Alternatif alarm kullanılıyor");
                window.alert("🚨 YARDIM SİNYALİ ALGILANDI!");
            });
        } else {
            console.error("❌ Ses dosyası bulunamadı!");
            window.alert("🚨 YARDIM SİNYALİ ALGILANDI!");
        }
    }
}

function appendDetection(detection) {
    const li = document.createElement("li");
    li.textContent = `🖐️ ${detection.class} (${Math.round(detection.confidence * 100)}%)`;
    detectionsList.prepend(li);
    if (detectionsList.children.length > 10) {
        detectionsList.removeChild(detectionsList.lastChild);
    }
}

function captureFrameAndSend() {
    // Video hazır değilse bekle
    if (!video.videoWidth || !video.videoHeight || video.readyState < 2) {
        return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL("image/jpeg", 0.8);
    const base64Image = dataURL.split(",")[1];

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ image: base64Image }));
    }
}

function connectWebSocket() {
    socket = new WebSocket("ws://localhost:8000/ws");

    socket.onopen = () => {
        console.log("🔌 WebSocket bağlantısı kuruldu.");
        updateStatus("idle");

        // Video yüklendikten sonra görüntüleri göndermeye başla
        const startSending = () => {
            if (video.readyState >= 2) {
                setInterval(captureFrameAndSend, 300); // 0.5 saniyede bir kare gönder
            } else {
                video.addEventListener('loadeddata', () => {
                    setInterval(captureFrameAndSend, 300);
                }, { once: true });
            }
        };
        startSending();
    };

    socket.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        console.log("📨 WebSocket mesajı alındı:", msg);

        if (msg.type === "detection") {
            const detections = msg.data.detections;
            const step = msg.data.sequence_step;
            const status = msg.data.status;

            console.log(`📊 Adım: ${step}, Durum: ${status}, Tespit sayısı: ${detections.length}`);

            if (detections.length > 0) {
                appendDetection(detections[0]);
            }

            updateFSM(step);
            updateStatus(status);

            // 🚨 ÖNEMLİ: Adım 2'ye ulaşınca zorla alarm tetikle (geçici test)
            if (step === 2 && status === "tracking") {
                console.log("🚨 ADIM 2 TESPİT EDİLDİ - ALARM TETİKLENİYOR!");
                setTimeout(() => {
                    updateStatus("alarm");
                }, 1000); // 1 saniye bekle
            }

            // Özel alarm kontrolü
            if (status === "alarm") {
                console.log("🚨 ALARM DURUMU TETİKLENDİ!");
                updateStatus("alarm");
            }
        }

        if (msg.type === "alarm") {
            console.log("🚨 ALARM MESAJI ALINDI!");
            updateStatus("alarm");
        }
    };

    socket.onclose = () => {
        console.warn("🔌 WebSocket bağlantısı kapandı. Yeniden bağlanılıyor...");
        updateStatus("idle");
        setTimeout(connectWebSocket, 2000);
    };

    socket.onerror = (err) => {
        console.error("WebSocket hatası:", err);
    };
}

// WebSocket bağlantısını başlat
connectWebSocket();