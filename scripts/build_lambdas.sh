#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
SHARED_DIR="$ROOT_DIR/shared"
LAMBDA_DIR="$ROOT_DIR/lambda"

# Python-рантайм Lambda
PYTHON_VERSION="3.11"
PLATFORM="manylinux2014_x86_64"

# Какие Lambda собирать (аргументы) или все
LAMBDAS=("$@")
if [ ${#LAMBDAS[@]} -eq 0 ]; then
    LAMBDAS=($(ls "$LAMBDA_DIR"))
fi

echo "Building Lambdas: ${LAMBDAS[*]}"
echo "Build dir: $BUILD_DIR"
echo

mkdir -p "$BUILD_DIR"

for LAMBDA_NAME in "${LAMBDAS[@]}"; do
    LAMBDA_PATH="$LAMBDA_DIR/$LAMBDA_NAME"
    BUILD_PATH="$BUILD_DIR/$LAMBDA_NAME"
    
    if [ ! -d "$LAMBDA_PATH" ]; then
        echo "ERROR: Lambda '$LAMBDA_NAME' not found at $LAMBDA_PATH"
        exit 1
    fi
    
    echo "=== Building $LAMBDA_NAME ==="
    
    # Чистим
    rm -rf "$BUILD_PATH"
    mkdir -p "$BUILD_PATH"
    
    # Копируем handler.py
    if [ ! -f "$LAMBDA_PATH/handler.py" ]; then
        echo "ERROR: $LAMBDA_PATH/handler.py not found"
        exit 1
    fi
    cp "$LAMBDA_PATH/handler.py" "$BUILD_PATH/handler.py"
    
    # Копируем shared/
    mkdir -p "$BUILD_PATH/shared"
    cp "$SHARED_DIR"/*.py "$BUILD_PATH/shared/"
    
    # Устанавливаем зависимости
    if [ -f "$LAMBDA_PATH/requirements.txt" ]; then
        echo "Installing dependencies..."
        pip install \
            --target "$BUILD_PATH" \
            --no-cache-dir \
            --platform "$PLATFORM" \
            --only-binary=:all: \
            --python-version "$PYTHON_VERSION" \
            --upgrade \
            -r "$LAMBDA_PATH/requirements.txt" \
            --quiet
    fi
    
    # Упаковываем
    rm -f "$BUILD_DIR/${LAMBDA_NAME}.zip"
    
    if command -v zip > /dev/null 2>&1; then
        (cd "$BUILD_PATH" && zip -rq "$BUILD_DIR/${LAMBDA_NAME}.zip" .)
    else
        # Fallback: Python zipfile
        python -c "
import zipfile, os, sys
build_path = '$BUILD_PATH'
out_path = '$BUILD_DIR/${LAMBDA_NAME}.zip'
with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(build_path):
        for f in files:
            full = os.path.join(root, f)
            arc = os.path.relpath(full, build_path)
            zf.write(full, arc)
"
    fi
    
    SIZE=$(du -h "$BUILD_DIR/${LAMBDA_NAME}.zip" | cut -f1)
    echo "Built: $BUILD_DIR/${LAMBDA_NAME}.zip ($SIZE)"
    echo
done

echo "=== Done ==="
ls -lh "$BUILD_DIR"/*.zip