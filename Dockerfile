# Python FastAPI backend step
FROM python:3.9

# ワーキングディレクトリを設定
WORKDIR /app

# Pythonの依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY ./app /app/app

# デバッグモードの切り替え
ARG DEBUG_MODE=false
ENV DEBUG_MODE=${DEBUG_MODE}

# templateフォルダをコピー
COPY /app/template /app/template

CMD if [ "$DEBUG_MODE" = "true" ]; then \
        python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --host 0.0.0.0 --port 80 --reload; \
    else \
        uvicorn app.main:app --host 0.0.0.0 --port 80; \
    fi