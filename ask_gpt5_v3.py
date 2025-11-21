# ask_gpt5_v2.py
import json
from openai import OpenAI
from questions_list import questions_list  # 你的題目 list
import os
from collections import Counter

# 載入 PPV
with open("ppv_initial.json", "r", encoding="utf-8") as f:
    ppv_data = json.load(f)

PERSONA_PROMPT = f"""
你是一個具有固定價值觀與決策習慣的角色，請依以下原則回答問題：
【PPV】{json.dumps(ppv_data, ensure_ascii=False)}
【決策優先順序】
1. 穩定性
2. 可控制度
3. 長期利益
4. 效率
5. 避免極端選項

【回答規則】
- 每題僅回答 A~E 中一個選項。
- 若有兩個選項相近，選更穩健、可控或長期的選項。
- 答案要保持傾向一致性，但允許少量波動。
- 不要解釋，不要描述理由，只回答選項字母。
"""

# 建立 OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_one_round():
    messages = [
        {"role": "system", "content": PERSONA_PROMPT}
    ]

    for idx, q in enumerate(questions_list):
        q_text = f"第 {idx+1} 題: {q['q']}\n選項: {', '.join(q['options'])}"
        messages.append({"role": "user", "content": q_text})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    answer_text = response.choices[0].message.content.strip()
    answers = [a for a in answer_text if a in ["A","B","C","D","E"]]
    return answers


def compute_stability(all_rounds):
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


def main(rounds=50):
    all_rounds = []

    for i in range(1, rounds + 1):
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


if __name__ == "__main__":
    main(50)
