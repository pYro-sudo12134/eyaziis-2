const $ = (id) => document.getElementById(id);

["speed", "volume", "pitch"].forEach((id) => {
    $(id).addEventListener("input", () => {
        $(`${id}-val`).textContent = $(id).value;
    });
});

$("paste-btn").onclick = async () => {
    try {
        const text = await navigator.clipboard.readText();
        $("text").value = text;
    } catch (e) {
        alert("Не удалось прочитать буфер обмена: " + e.message);
    }
};

$("selection-btn").onclick = () => {
    const sel = window.getSelection().toString();
    if (sel) $("text").value = sel;
};

$("submit-btn").onclick = async () => {
    const text = $("text").value.trim();
    if (!text) {
        alert("Введите текст");
        return;
    }

    const payload = {
        text,
        voice: $("voice").value,
        speed: parseFloat($("speed").value),
        volume: parseFloat($("volume").value),
        pitch: parseFloat($("pitch").value),
        format: $("format").value,
    };

    setBusy(true, "Отправка...");
    try {
        const r = await fetch("/api/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (!r.ok) throw new Error(await r.text());
        const { request_id } = await r.json();
        await pollResult(request_id);
    } catch (e) {
        setBusy(false, "Ошибка: " + e.message);
    }
};

async function pollResult(requestId) {
    setBusy(true, "Обработка...");
    const started = Date.now();
    while (Date.now() - started < 180000) {
        await new Promise((r) => setTimeout(r, 1500));
        const r = await fetch(`/api/result/${requestId}`);
        const data = await r.json();

        if (data.status === "COMPLETED") {
            showResult(data.audio_url);
            setBusy(false, "Готово");
            return;
        }
        if (data.status === "FAILED") {
            setBusy(false, "Ошибка: " + (data.error || "unknown"));
            return;
        }
        setBusy(true, `Обработка... (${data.status})`);
    }
    setBusy(false, "Превышено время ожидания");
}

function showResult(audioUrl) {
    $("result-card").hidden = false;
    $("player").src = audioUrl;
    $("download-link").href = audioUrl;
}

function setBusy(busy, message) {
    $("submit-btn").disabled = busy;
    $("status").textContent = message || "";
}