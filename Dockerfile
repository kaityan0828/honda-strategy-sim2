# ベースイメージとして軽量なPythonを使用
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係ファイルのコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポートの開放（Dashのデフォルトは8050）
EXPOSE 8050

# Gunicornを使用して本番環境を起動
# worker数はApp Runnerなどのリソースに合わせて調整（通常はCPUコア数*2+1）
CMD ["gunicorn", "-b", "0.0.0.0:8050", "app:server", "--workers", "2"]
