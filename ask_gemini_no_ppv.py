# ask_gemini_no_ppv.py
import google.generativeai as genai
from questions_list import questions_list  # 你的題目 list
import os
from collections import Counter
import pandas as pd
from datetime import datetime
import time

# 無 PPV 的 Prompt
PERSONA_PROMPT = """
妳作為自己，從現在開始回答我給你的問題。

作答方式：
1 = 非常不符合
2 = 有點不符合
3 = 不算符合也不算不符合
4 = 有點符合
5 = 非常符合

輸出格式範例：1, 2, 3, 4, 5...
"""

# 設定 Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 配置模型（提高自由度，讓模型展現自己的風格）
generation_config = {
    "temperature": 1.0,  # 保持高溫度以增加多樣性
    "top_p": 0.98,       # 提高 top_p，允許更多樣的選擇
    "top_k": 64,         # 提高 top_k，增加候選詞彙
    "max_output_tokens": 8192,
}

# 設定安全設定（降低過濾敏感度）
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# 建立模型（使用 models/gemini-pro-latest）
model = genai.GenerativeModel(
    model_name="models/gemini-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
    system_instruction=PERSONA_PROMPT  # System prompt 會自動被緩存
)

def ask_one_round(max_retries=3):
    # 組合所有問題
    all_questions = ""
    for idx, q in enumerate(questions_list):
        all_questions += f"第 {idx+1} 題: {q['q']}\n"

    # 重試機制
    for attempt in range(max_retries):
        try:
            # 呼叫 Gemini（system_instruction 會自動被 cache）
            response = model.generate_content(all_questions)

            # 檢查回應狀態
            if not response.candidates or not response.candidates[0].content.parts:
                print(f"警告：回應被阻擋（嘗試 {attempt + 1}/{max_retries}）")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待後重試
                    continue
                else:
                    return []

            answer_text = response.text.strip()

            # 將答案拆成 list (1~5)
            answers = [a for a in answer_text if a in ["1","2","3","4","5"]]

            # 驗證答案數量（僅在出錯時顯示）
            if len(answers) != len(questions_list):
                print(f"警告：預期 {len(questions_list)} 個答案，但得到 {len(answers)} 個")
                print(f"原始回答: {answer_text}")

            return answers

        except Exception as e:
            print(f"錯誤（嘗試 {attempt + 1}/{max_retries}）: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                return []


def compute_stability(all_rounds):
    """計算每一題的穩定度"""
    # 過濾掉空的回合
    valid_rounds = [r for r in all_rounds if len(r) > 0]

    if not valid_rounds:
        print("警告：沒有有效的回合數據")
        return []

    num_questions = len(valid_rounds[0])
    stability_results = []

    for q_idx in range(num_questions):
        # 收集第 q_idx 題所有回合的答案（跳過長度不足的回合）
        answers = [round_answers[q_idx] for round_answers in valid_rounds if len(round_answers) > q_idx]

        if not answers:
            continue

        counter = Counter(answers)
        most_common_answer, count = counter.most_common(1)[0]

        stability = count / len(answers)

        stability_results.append({
            "question": q_idx + 1,
            "most_common": most_common_answer,
            "count": count,
            "stability": stability
        })

    return stability_results


def main(rounds=100):
    all_rounds = []
    for i in range(1, rounds+1):
        print(f"\n=== 回合 {i} ===")
        answers = ask_one_round()
        print("答案:", " ".join(answers))
        all_rounds.append(answers)

        # 每次呼叫後等待 7 秒，避免超過 API 速率限制（每分鐘最多 10 次請求）
        if i < rounds:  # 最後一次不需要等待
            time.sleep(7)

    print("\n=== 全部回合答案 ===")
    for i, ans in enumerate(all_rounds, 1):
        print(f"{i}: {' '.join(ans)}")

    # ⭐ 計算穩定度
    stability_results = compute_stability(all_rounds)

    print("\n=== 每一題穩定度（Consistency）===\n")
    for s in stability_results:
        print(
            f"第 {s['question']} 題："
            f"最常出現 {s['most_common']}（{s['count']} 次）｜"
            f"穩定度 = {s['stability']:.3f}"
        )

    # 保存到 Excel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gemini_no_ppv_results_{timestamp}.xlsx"

    # 準備數據
    # 1. 每回合的答案
    rounds_data = []
    for i, ans in enumerate(all_rounds, 1):
        row = {"回合": i}
        for q_idx, answer in enumerate(ans, 1):
            row[f"第{q_idx}題"] = answer
        rounds_data.append(row)

    # 2. 穩定度統計
    stability_data = []
    for s in stability_results:
        stability_data.append({
            "題號": s['question'],
            "最常出現答案": s['most_common'],
            "出現次數": s['count'],
            "穩定度": s['stability']
        })

    # 創建 Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # 寫入每回合答案
        df_rounds = pd.DataFrame(rounds_data)
        df_rounds.to_excel(writer, sheet_name='每回合答案', index=False)

        # 寫入穩定度統計
        df_stability = pd.DataFrame(stability_data)
        df_stability.to_excel(writer, sheet_name='穩定度統計', index=False)

    print(f"\n✅ 結果已保存到: {filename}")

if __name__ == "__main__":
    main(10)
