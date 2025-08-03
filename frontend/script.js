// static/script.js

let socket;
const video = document.getElementById("video-stream");
const startBtn = document.getElementById("start-btn");
const statusText = document.getElementById("status-text");
const fsmSteps = [
    document.getElementById("step-0"),
    document.getElementById("step-1"),
    document.getElementById("step-2")
];
const detectionsList = document.getElementById("detections");
const alarmSound = document.getElementById("alarm-sound");

// Recording vars
let mediaRecorder;
let recordedChunks = [];

// Audio load / error logging
alarmSound.addEventListener('loadeddata', () => {
    console.log("✅ Alarm sesi başarıyla yüklendi");
});
alarmSound.addEventListener('error', e => {
    console.error("❌ Alarm sesi yüklenemedi:", e);
});
alarmSound.load();

// Start button: unlock audio & connect WS
startBtn.addEventListener('click', () => {
    // tiny play-pause to unlock autoplay
    alarmSound.play()
        .then(() => alarmSound.pause())
        .catch(() => {/* ignore */});

    connectWebSocket();
    startBtn.disabled = true;
    startBtn.textContent = "Bağlanıyor…";
});

// ——— Recording setup ———
function setupRecorder() {
    const stream = video.srcObject;
    if (!stream) {
        console.warn("📹 Kayıt için video stream hazır değil");
        return;
    }
    recordedChunks = [];
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm; codecs=vp9' });

    mediaRecorder.ondataavailable = e => {
        if (e.data && e.data.size > 0) {
            recordedChunks.push(e.data);
        }
    };
    mediaRecorder.onstop = saveRecording;
}

function startRecording(durationMs = 10000) {
    setupRecorder();
    if (!mediaRecorder) return;

    mediaRecorder.start();
    console.log(`📹 Kayıt başladı (${durationMs/1000}s)`);

    setTimeout(() => {
        if (mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            console.log("📹 Kayıt durduruluyor");
        }
    }, durationMs);
}

function saveRecording() {
    const blob = new Blob(recordedChunks, { type: 'video/webm' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `alarm-recording-${Date.now()}.webm`;
    document.body.appendChild(a);
    a.click();

    setTimeout(() => {
        URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }, 100);

    console.log("📹 Kayıt indiriliyor");
}
// —————————

// Play alarm sound + start recording
function playAlarm() {
    console.log("🚨 playAlarm() çağrıldı");
    statusText.textContent = "🚨 ALARM!";
    statusText.className = "status-alarm";

    alarmSound.currentTime = 0;
    alarmSound.play()
        .then(() => console.log("🔊 Alarm sesi çaldı"))
        .catch(err => console.error("❌ Ses çalınamadı:", err));

    // Automatically record 10s on alarm
    startRecording(10000);
}

// Update FSM visualization
function updateFSM(step) {
    fsmSteps.forEach((el, i) => {
        el.classList.toggle("done", i < step);
        el.classList.toggle("active", i === step);
    });
}

// Update status text for idle / tracking
function updateStatus(mode) {
    console.log("── updateStatus:", mode);
    statusText.className = "";
    if (mode === "idle") {
        statusText.textContent = "Bekleniyor";
        statusText.classList.add("status-idle");
    } else if (mode === "tracking") {
        statusText.textContent = "Takip Ediliyor";
        statusText.classList.add("status-tracking");
    }
}

// Append a detection to the list
function appendDetection(d) {
    const li = document.createElement("li");
    li.textContent = `🖐️ ${d.class} (${Math.round(d.confidence * 100)}%)`;
    detectionsList.prepend(li);
    if (detectionsList.children.length > 10) {
        detectionsList.removeChild(detectionsList.lastChild);
    }
}

// Capture frame & send to server
function captureFrameAndSend() {
    if (video.readyState < 2) return;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    const b64 = canvas.toDataURL("image/jpeg", 0.8).split(",")[1];
    if (socket?.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ image: b64 }));
    }
}

// WebSocket connection & messaging
function connectWebSocket() {
    socket = new WebSocket("ws://localhost:8000/ws");

    socket.onopen = () => {
        console.log("🔌 WebSocket açık");
        startBtn.textContent = "Bağlandı ✅";

        // Start video & frame sending
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
                setInterval(captureFrameAndSend, 300);
            })
            .catch(err => {
                console.error("❌ Kamera erişim hatası:", err);
                alert("Kamera erişimi reddedildi.");
            });
    };

    socket.onmessage = ({ data }) => {
        const msg = JSON.parse(data);
        console.log("📨 mesaj:", msg);

        if (msg.type === "alarm") {
            console.log("🚨 SUNUCUDAN ALARM");
            playAlarm();
            return;
        }
        if (msg.type === "detection") {
            const { detections, sequence_step: step, status } = msg.data;
            console.log("📊", { step, status, detections });

            updateFSM(step);
            if (detections.length) {
                const det = detections[0];
                appendDetection(det);
                // Trigger on closed_finger(s)
                if (det.class === "closed_finger" || det.class === "closed_fingers") {
                    console.log(`🚨 ${det.class} tespit edildi - Alarm tetikleniyor!`);
                    playAlarm();
                    return;
                }
            }
            updateStatus(status);
        }
    };

    socket.onclose = () => {
        console.warn("🔌 WS kapandı, yeniden bağlanılıyor…");
        updateStatus("idle");
        setTimeout(connectWebSocket, 2000);
    };

    socket.onerror = err => console.error("⚠️ WS hata:", err);
}
