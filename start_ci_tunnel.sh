#!/bin/bash
# ==============================================================================
# Script Runner Jenkins & Ngrok Port 8080 - AntriSehat
# ==============================================================================

set -e

PORT=8080

echo "🚀 [1/3] Memeriksa status Jenkins di port $PORT..."
if [ "$(docker ps -q -f name=jenkins-docker)" ]; then
    echo "✅ Container Jenkins (jenkins-docker) sudah berjalan aktif."
elif [ "$(docker ps -aq -f name=jenkins-docker)" ]; then
    echo "🔄 Memulai container Jenkins (jenkins-docker)..."
    docker start jenkins-docker
else
    echo "📦 Membuat & menjalankan container Jenkins via Docker Compose..."
    docker compose --profile ci up -d jenkins
fi

echo "⏳ [2/3] Menunggu service Jenkins siap di port $PORT..."
until curl -s http://localhost:$PORT > /dev/null; do
    echo "   Menunggu Jenkins booting..."
    sleep 3
done
echo "✅ Jenkins siap diakses pada: http://localhost:$PORT"

echo ""
echo "🌐 [3/3] Membuka Tunnel Ngrok untuk Port $PORT..."
echo "------------------------------------------------------------------------------"
echo "📌 PETUNJUK SETUP GITHUB WEBHOOK:"
echo "1. Salin URL Forwarding HTTPS yang muncul di bawah (contoh: https://xxxx.ngrok-free.app)"
echo "2. Buka repository GitHub: Settings -> Webhooks -> Add Webhook"
echo "3. Isi Payload URL dengan:"
echo "   https://<SUBDOMAIN_NGROK>.ngrok-free.app/github-webhook/"
echo "4. Content type: application/json"
echo "5. Trigger: Just the push event."
echo "------------------------------------------------------------------------------"
echo "Tekan CTRL+C jika ingin menghentikan tunnel ngrok."
echo ""

ngrok http $PORT

