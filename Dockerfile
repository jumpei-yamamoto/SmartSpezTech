FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Reactのビルド資源をコピー（パスを修正）
COPY ./static /app/static

# 他のPython関連のコードをコピー
COPY . .

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]