#!/usr/bin/env bash
# 一鍵啟動 mini-RAG。
#   ./start.sh            同時啟動後端與前端，並自動打開瀏覽器
#   ./start.sh backend    只啟動後端（http://127.0.0.1:8000）
#   ./start.sh frontend   只啟動前端（http://localhost:5173）
# 按 Control + C 會一起關掉。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- 檢查工具 ---------------------------------------------------------------
UV="$(command -v uv || true)"
[ -z "$UV" ] && [ -x "$HOME/.local/bin/uv" ] && UV="$HOME/.local/bin/uv"
if [ -z "$UV" ]; then
  echo "❌ 找不到 uv。請先安裝：curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi
if ! command -v npm >/dev/null; then
  echo "❌ 找不到 npm。請先安裝 Node.js：https://nodejs.org"
  exit 1
fi

# 第一次執行時自動建立 .env
if [ ! -f "$ROOT/.env" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "✅ 已從 .env.example 建立 .env"
fi

backend() {
  cd "$ROOT/backend"
  echo "📦 檢查後端套件…"
  "$UV" sync --quiet
  echo "🚀 後端啟動中：http://127.0.0.1:8000"
  exec "$UV" run uvicorn app.main:app --reload --port 8000
}

frontend() {
  cd "$ROOT/frontend"
  if [ ! -d node_modules ]; then
    echo "📦 第一次執行，安裝前端套件…"
    npm install
  fi
  echo "🚀 前端啟動中：http://localhost:5173"
  exec npm run dev -- "$@"
}

wait_for_backend() {
  for _ in $(seq 1 120); do
    curl -fs http://127.0.0.1:8000/api/status >/dev/null 2>&1 && return 0
    sleep 1
  done
  echo "⚠️  後端 120 秒內沒有回應，請看上面的錯誤訊息。"
  return 1
}

case "${1:-all}" in
  backend)  backend ;;
  frontend) frontend ;;
  all)
    # Control + C 時把整組程式一起關掉
    trap 'trap - INT TERM EXIT; kill 0 2>/dev/null' INT TERM EXIT
    (backend) &
    wait_for_backend
    (frontend --open) &
    echo ""
    echo "✨ mini-RAG 已啟動 → http://localhost:5173 （按 Control + C 關閉）"
    echo ""
    wait
    ;;
  *)
    echo "用法：./start.sh [all|backend|frontend]"
    exit 1
    ;;
esac
