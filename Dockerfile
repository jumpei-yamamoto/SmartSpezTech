# Python FastAPI backend step
FROM python:3.9

WORKDIR /app

# Pythonの依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 他のPython関連のコードをコピー
COPY . .

# デバッグモードの切り替え
ARG DEBUG_MODE=false
ENV DEBUG_MODE=${DEBUG_MODE}

CMD if [ "$DEBUG_MODE" = "true" ]; then \
        python -m debugpy --listen 0.0.0.0:5678 -m uvicorn main:app --host 0.0.0.0 --port 80 --reload; \
    else \
        uvicorn main:app --host 0.0.0.0 --port 80; \
    fi
