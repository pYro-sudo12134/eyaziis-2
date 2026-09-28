#!/bin/bash
set -e

VOICES_DIR="/app/voices"
mkdir -p "$VOICES_DIR"

BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU"

download_voice() {
    local voice_name=$1
    local subdir=$2
    local quality=$3
    
    if [ ! -f "$VOICES_DIR/${voice_name}.onnx" ]; then
        echo "Downloading $voice_name..."
        wget -q -O "$VOICES_DIR/${voice_name}.onnx" \
            "$BASE_URL/${subdir}/${quality}/${voice_name}.onnx"
        wget -q -O "$VOICES_DIR/${voice_name}.onnx.json" \
            "$BASE_URL/${subdir}/${quality}/${voice_name}.onnx.json"
        echo "Downloaded $voice_name"
    else
        echo "$voice_name already exists"
    fi
}

download_voice "ru_RU-irina-medium" "irina" "medium"
download_voice "ru_RU-dmitri-medium" "dmitri" "medium"

echo "Voices available:"
ls -la "$VOICES_DIR"