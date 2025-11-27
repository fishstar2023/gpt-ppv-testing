# ask_gpt5_v2_noppv_finetuned.py
from openai import OpenAI
from questions_list import questions_list  # 你的題目 list
import os
from collections import Counter
import pandas as pd
from datetime import datetime

PERSONA_PROMPT = """
妳作為自己，從現在開始回答我給你的問題。

作答方式：
1 = 不符合
2 = 不算符合也不算不符合
3 = 符合

輸出格式範例：1, 2, 3...
"""

# 建立 OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_one_round():
    messages = [
        {"role": "system", "content": PERSONA_PROMPT}
    ]
    # 依序加入每題
    for idx, q in enumerate(questions_list):
        q_text = f"第 {idx+1} 題: {q['q']}"
        messages.append({"role": "user", "content": q_text})

    # 呼叫 GPT-5
    response = client.chat.completions.create(
        model="gpt-5.1-2025-11-13",
        messages=messages        # 移除 temperature 以避免錯誤
    )
    # 取得 GPT 回答
    answer_text = response.choices[0].message.content.strip()

    # 將答案拆成 list (1~3)
    answers = [a for a in answer_text if a in ["1","2","3"]]

    # 驗證答案數量（僅在出錯時顯示）
    if len(answers) != len(questions_list):
        print(f"警告：預期 {len(questions_list)} 個答案，但得到 {len(answers)} 個")
        print(f"原始回答: {answer_text}")

    return answers


def compute_stability(all_rounds):
    """計算每一題的穩定度"""
    num_questions = len(all_rounds[0])
    stability_results = []

    for q_idx in range(num_questions):
        # 收集第 q_idx 題所有回合的答案
        answers = [round_answers[q_idx] for round_answers in all_rounds]

        counter = Counter(answers)
        most_common_answer, count = counter.most_common(1)[0]

        stability = count / len(all_rounds)

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
    filename = f"gpt_stability_results_{timestamp}.xlsx"

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
    main(100)
