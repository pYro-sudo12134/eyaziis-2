const $ = (id) => document.getElementById(id);

let mediaRecorder = null;
let chunks = [];
let recording = false;

$("record-btn").onclick = async () => {
    if (!recording) {
        await startRecording();
    } else {
        stopRecording();
    }
};

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
        chunks = [];

        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) chunks.push(e.data);
        };

        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach((t) => t.stop());
            const blob = new Blob(chunks, { type: "audio/webm" });
            await sendAudio(blob);
        };

        mediaRecorder.start();
        recording = true;
        $("record-btn").textContent = "⏹ Остановить";
        $("record-btn").classList.add("recording");
        $("rec-status").textContent = "Идёт запись...";
    } catch (e) {
        alert("Микрофон недоступен: " + e.message);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
    }
    recording = false;
    $("record-btn").textContent = "🎤 Записать";
    $("record-btn").classList.remove("recording");
}

async function sendAudio(blob) {
    $("rec-status").textContent = "Отправка...";
    const form = new FormData();
    form.append("audio", blob, "recording.webm");
    form.append("voice", $("voice").value);

    try {
        const r = await fetch("/api/ask-audio", { method: "POST", body: form });
        if (!r.ok) throw new Error(await r.text());
        const { request_id } = await r.json();
        $("rec-status").textContent = "Обработка...";
        await pollResult(request_id);
    } catch (e) {
        $("rec-status").textContent = "Ошибка: " + e.message;
    }
}

async function pollResult(requestId) {
    const started = Date.now();
    while (Date.now() - started < 360000) {
        await new Promise((r) => setTimeout(r, 1500));
        const r = await fetch(`/api/result/${requestId}`);
        const data = await r.json();

        if (data.status === "COMPLETED") {
            $("rec-status").textContent = "Готово";
            showResult(data);
            return;
        }
        if (data.status === "FAILED") {
            $("rec-status").textContent = "Ошибка: " + (data.error || "unknown");
            return;
        }
        $("rec-status").textContent = `Обработка... (${data.status})`;
    }
    $("rec-status").textContent = "Превышено время ожидания";
}

function showResult(data) {
    $("result-card").hidden = false;
    $("answer-text").textContent = data.text || "(ответ не распознан)";
    $("player").src = data.audio_url;
}