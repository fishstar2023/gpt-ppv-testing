# GPT/Gemini PPV 穩定度測試專案

## 專案說明

本專案用於測試 GPT-5 和 Gemini 模型在給定 PPV (Personal Preference Vector) 人格設定時的答題穩定度。透過多次重複測試，評估 AI 模型在扮演特定人格時的一致性。

## 核心檔案說明

### 1. 測試腳本（目前設定為 10 回合測試）

#### GPT-5 測試
- **ask_gpt5_final.py** - 使用 PPV 人格設定的 GPT-5 測試
  - 模型：gpt-5.1-2025-11-13
  - 載入 ppv_initial.json 作為人格設定
  - 執行 100 回合測試（需修改為 10 回合）

- **ask_gpt5_final_noppv.py** - 不使用 PPV 的 GPT-5 基準測試
  - 讓模型以自己的風格回答
  - 用於對照組比較
  - 執行 100 回合測試（需修改為 10 回合）

#### Gemini 測試
- **ask_gemini_final.py** - 使用 PPV 人格設定的 Gemini 測試 ✅ **已設為 10 回合**
  - 模型：models/gemini-pro-latest
  - 載入 ppv_initial.json 作為人格設定
  - 包含重試機制和錯誤處理
  - 每次請求間隔 7 秒（API 速率限制）

- **ask_gemini_no_ppv.py** - 不使用 PPV 的 Gemini 基準測試 ✅ **已設為 10 回合**
  - 讓模型以自己的風格回答
  - 用於對照組比較
  - 包含相同的速率限制和錯誤處理

### 2. 資料檔案

- **ppv_initial.json** - ESFJ 人格類型的 PPV 設定
  - Big5 人格特質分數
  - MBTI 類型：ESFJ
  - DISC、Enneagram 等多維度人格資料
  - 價值觀、道德觀、風險偏好等設定

- **questions_list.py** - Big5 人格量表（50 題）
  - 外向性 (Extraversion): 10 題
  - 神經質 (Neuroticism): 10 題
  - 盡責性 (Conscientiousness): 10 題
  - 親和性 (Agreeableness): 10 題
  - 開放性 (Openness): 10 題

### 3. 輔助工具

- **list_gemini_models.py** - 列出可用的 Gemini 模型
- **test_gemini_simple.py** - Gemini API 簡單測試

## 作答格式

所有測試使用 **1-5 Likert 量表**：
- 1 = 非常不符合
- 2 = 有點不符合
- 3 = 不算符合也不算不符合
- 4 = 有點符合
- 5 = 非常符合

## 環境設定

### 必要套件
```bash
pip install openai google-generativeai pandas openpyxl
```

### API Key 設定
創建 `.env` 檔案（可參考 `.env.example`）：
```bash
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

## 執行方式

### GPT-5 測試
```bash
# 有 PPV
python ask_gpt5_final.py

# 無 PPV（基準測試）
python ask_gpt5_final_noppv.py
```

### Gemini 測試（已設定為 10 回合）
```bash
# 有 PPV
python ask_gemini_final.py

# 無 PPV（基準測試）
python ask_gemini_no_ppv.py
```

⚠️ **注意**：Gemini 測試因 API 速率限制（10 次/分鐘），10 回合約需 **70 秒**完成。

## 輸出結果

測試完成後會自動生成 Excel 檔案，包含兩個工作表：

1. **每回合答案** - 記錄每一回合的所有答案
2. **穩定度統計** - 分析每一題的：
   - 最常出現的答案
   - 出現次數
   - 穩定度（Consistency）百分比

檔案命名格式：
- GPT: `gpt_stability_results_YYYYMMDD_HHMMSS.xlsx`
- Gemini: `gemini_stability_results_YYYYMMDD_HHMMSS.xlsx` / `gemini_no_ppv_results_YYYYMMDD_HHMMSS.xlsx`

## Prompt 設計理念

### 有 PPV 版本
```
請扮演以下 PPV 的人格：
{完整 PPV JSON 資料}

從現在開始回答我給你的問題。
```

### 無 PPV 版本
```
妳作為自己，從現在開始回答我給你的問題。
```

- ✅ 簡潔直接，減少偏見
- ✅ 讓模型自然表達，避免過度引導
- ✅ 不強加特定決策框架或視角

## 模型配置

### GPT-5
- 不使用 temperature 參數（使用預設值）
- 每次請求包含所有 50 題

### Gemini
- temperature: 1.0（高自由度）
- top_p: 0.98
- top_k: 64
- 安全設定：全部設為 BLOCK_NONE（避免過度過濾）
- System instruction 自動緩存

## 版本歷程

### 2025-11-27
- 將 Gemini 測試檔案改為 10 回合小量測試
- 更新問卷為 Big5 人格量表（50 題）
- 答題格式從 A-E 改為 1-5 Likert 量表
- 更新 PPV 為 ESFJ 人格類型
- 優化 prompt 減少偏見

### 2025-11-26
- 新增 Gemini API 測試腳本
- 實作有/無 PPV 對照測試架構

## 注意事項

1. **GPT-5 測試**目前仍設定為 100 回合，需手動修改為 10 回合
2. **API 費用**：請注意 API 使用量，100 回合測試會產生相當費用
3. **速率限制**：Gemini 免費版限制為 10 次/分鐘
4. **Python 版本**：建議使用 Python 3.10+（目前使用 3.9.6 會有警告）

## 故障排除

### Gemini API 錯誤
```
DefaultCredentialsError: No API_KEY or ADC found
```
➜ 檢查 `.env` 檔案中的 `GOOGLE_API_KEY` 是否正確設定

### 答案數量不符
如果出現「預期 50 個答案，但得到 XX 個」，可能原因：
- 模型輸出格式異常
- 回應被安全過濾阻擋
- API 請求失敗

程式會自動顯示原始回答內容以便除錯。
