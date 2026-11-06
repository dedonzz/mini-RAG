# mini-RAG

一個在你自己電腦上執行的「文件問答」系統：上傳文件，用中文或英文提問，它會從文件裡找出最相關的段落。

> 目前還沒有接上 LLM（沒有 API Key），所以畫面上會顯示「尚未設定 LLM」，並列出**找到的段落**和**原本要送給 AI 的 prompt**。這是正常現象，接上 LLM 的方法請看[最後一節](#之後接上真正的-llm)。

---

## 🚀 最快的啟動方式

### 方法 A：在 VS Code 裡按一個快捷鍵（推薦）

1. 打開 VS Code，選單 **File → Open Folder…**，選擇 `mini-RAG` 這個資料夾。
2. 右下角跳出「是否安裝推薦的擴充功能」時，按 **Install**（Python、Vue）。
3. 按 **`Command + Shift + B`**。
4. 下方會開兩個終端機分頁：「後端 (FastAPI)」和「前端 (Vue)」。等前端分頁出現 `Local: http://localhost:5173/`。
5. 用瀏覽器打開 **http://localhost:5173**。

要關閉時：在每個終端機分頁裡按 `Control + C`，或點分頁右上角的垃圾桶圖示。

> 找不到快捷鍵時，也可以從選單 **Terminal → Run Build Task…** 執行。

### 方法 B：在終端機打一行指令

在 VS Code 按 `` Control + ` `` 打開終端機（或使用 macOS 的「終端機」App），然後執行：

```bash
cd "/Users/dontemp/claude project/mini-RAG"
./start.sh
```

它會依序完成這些事：

- 第一次執行時，自動安裝所有套件（大約需要 2～5 分鐘）
- 啟動後端和前端
- **自動打開瀏覽器**，進入 http://localhost:5173

要關閉時按 `Control + C`，兩個伺服器會一起停止。

> 路徑裡有空格（`claude project`），所以 `cd` 後面一定要加雙引號。

---

## 🖱️ 怎麼使用

| 步驟 | 在哪裡 | 做什麼 |
|---|---|---|
| 1. 上傳文件 | 左側「文件」區 | 把 `.txt`、`.md`、`.pdf` 拖進虛線框，或點「選擇檔案」 |
| 2. 提問 | 右側聊天區 | 輸入問題，按 `Enter` 送出（`Shift + Enter` 換行） |
| 3. 看結果 | 回答下方 | 「引用來源」列出找到的段落和相似度；「查看送給 LLM 的 prompt」顯示完整 prompt |
| 4. 調整參數 | 左側「設定」區 | 段落大小、重疊字數、top-k。改了段落參數之後，按「重建索引」才會套用到已上傳的文件 |
| 5. 切換語言 | 右上角 | 中文 / EN |

⏳ **第一次上傳文件會比較久**：系統要下載約 470MB 的 embedding 模型，下載一次之後就不用再等。

---

## 📍 網址一覽

| 網址 | 用途 |
|---|---|
| http://localhost:5173 | **平常用這個**：網頁介面（開發模式，改前端程式碼會自動更新畫面） |
| http://127.0.0.1:8000/docs | 後端 API 的自動文件，可以直接在網頁上測試每個 API |
| http://127.0.0.1:8000 | 只開後端時使用的網頁（要先 `cd frontend && npm run build` 打包前端） |

---

## 🧰 VS Code 裡還能做什麼

| 想做的事 | 怎麼做 |
|---|---|
| 啟動全部 | `Command + Shift + B` |
| 只啟動後端或只啟動前端 | `Command + Shift + P` → 輸入 `Run Task` → 選「後端 (FastAPI)」或「前端 (Vue)」 |
| 執行測試 | `Command + Shift + P` → `Run Task` → 「執行測試」，或點左側燒杯圖示（Testing） |
| 對後端設中斷點偵錯 | 先停掉正在跑的後端，再按 `Command + Shift + D` → 選「偵錯後端 (FastAPI)」→ 按 ▶︎ |

這些設定都放在 `.vscode/` 資料夾裡。

---

## 🗂️ 檔案放在哪裡

```
mini-RAG/
├── start.sh          ← 一鍵啟動腳本
├── .env              ← ★ 設定與 API Key 放這裡（不會被 git 追蹤）
├── .env.example      ← .env 的範本（不要填真的 Key）
├── .vscode/          ← VS Code 的快捷鍵與偵錯設定
├── data/             ← 你上傳的文件和索引（第一次啟動後自動建立，不會被 git 追蹤）
├── backend/          ← 後端（Python + FastAPI）
│   └── app/
│       ├── llm/      ← ★ 接 LLM 的插座
│       ├── embed/    ← ★ 接 Embedding 的插座
│       └── rag/      ← 讀檔、切段、向量檢索、組 prompt
└── frontend/         ← 前端（Vue 網頁）
```

完整的架構圖與每個資料夾的說明，請看 👉 [mini-RAG 新手使用指南](https://claude.ai/artifact/ACCe6NbP26bk2Xqzx6PyBx)。

---

## 🔑 之後接上真正的 LLM

1. 所有 API Key **只放在 `.env`**，路徑是 `mini-RAG/.env`。
2. 在 `backend/app/llm/` 新增一個 adapter（對接程式），然後在 `backend/app/llm/__init__.py` 的 `PROVIDERS` 裡註冊它。
3. 修改 `.env`，例如：
   ```
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-4o-mini
   LLM_API_KEY=sk-你的金鑰
   ```
4. 重新啟動後端。

可以直接複製的完整程式碼，以及 OpenAI、DeepSeek、Groq、Gemini、Ollama 各家的網址，都在[新手使用指南](https://claude.ai/artifact/ACCe6NbP26bk2Xqzx6PyBx)的「接上真正的 LLM」一節。

⚠️ 接上雲端 LLM 後，每次提問時，找到的文件段落都會送到該廠商。如果放的是個人資料，請先想清楚；不希望資料離開電腦的話，可以改用本機的 Ollama。

---

## ❓ 出問題時

| 狀況 | 解決方法 |
|---|---|
| `command not found: uv` | 關掉並重開終端機。還是不行的話，先安裝 uv：`curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `permission denied: ./start.sh` | 執行 `chmod +x start.sh` |
| 網頁顯示「無法連線到後端」 | 後端沒在執行。看看「後端」終端機分頁有沒有紅色錯誤訊息 |
| `Address already in use` | 上一次開的伺服器還沒關。找到那個終端機按 `Control + C`，或重開 VS Code |
| 改了 `.env` 卻沒有生效 | 後端要重新啟動才會讀取新的 `.env` |
| 想清空所有文件、從頭開始 | 先關掉程式，再刪除 `data/` 資料夾 |

---

## 🛠️ 給想深入了解的人

- 技術組成：Python 3.12、FastAPI、sentence-transformers（`intfloat/multilingual-e5-small`）、numpy 寫的向量儲存；前端是 Vue 3、TypeScript、Vite、vue-i18n。
- 手動啟動（等同 `./start.sh`，需要開兩個終端機）：
  ```bash
  cd backend && uv sync && uv run uvicorn app.main:app --reload   # 終端機 1
  cd frontend && npm install && npm run dev                       # 終端機 2
  ```
- 測試：`cd backend && uv run pytest`
