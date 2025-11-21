# ask_gpt5_no_ppv_with_reasons.py
from openai import OpenAI
from questions_list import questions_list
import os
from collections import Counter

# 系統提示，不帶 PPV
PERSONA_PROMPT = """
你是一個具有固定決策傾向的角色，回答問題時遵循以下原則：
1. 優先選擇穩健、可控、長期有利的選項。
2. 避免極端或冒險的選擇。

【回答規則】
- 每題僅回答 A~E 中一個選項。
- 答案應保持一致性，但允許少量波動。
"""

# 建立 OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_question_2_with_reason():
    """針對第二題詢問答案並要求解釋原因"""
    # 第二題是 index 1
    question = questions_list[1]
    q_text = f"第 2 題: {question['q']}\n選項: {', '.join(question['options'])}"

    messages = [
        {"role": "system", "content": PERSONA_PROMPT},
        {"role": "user", "content": f"{q_text}\n\n請先回答選項字母（A~E），然後用 1-2 句話簡明扼要地說明選擇這個答案的理由。"}
    ]

    response = client.chat.completions.create(
        model="gpt-5.1-2025-11-13",
        messages=messages
    )

    answer_text = response.choices[0].message.content.strip()

    # 提取答案（第一個出現的 A-E）
    answer = None
    for char in answer_text:
        if char in ["A", "B", "C", "D", "E"]:
            answer = char
            break

    return answer, answer_text

def main():
    """執行第二題的詢問 10 次"""
    print("=== 針對第二題詢問 GPT 10 次（無 PPV）===\n")

    question = questions_list[1]
    print(f"題目: {question['q']}\n")

    all_answers = []

    for i in range(1, 11):
        answer, reason = ask_question_2_with_reason()
        all_answers.append(answer)

        print(f"第 {i} 次 - 答案: {answer}")
        print(f"理由: {reason}\n")

    # 統計結果
    print("="*60)
    print("統計結果")
    print("="*60)

    counter = Counter(all_answers)
    print(f"\n答案分布：")
    for answer, count in counter.most_common():
        percentage = (count / 10) * 100
        print(f"  {answer}: {count} 次 ({percentage:.0f}%)")

    most_common_answer, most_common_count = counter.most_common(1)[0]
    stability = most_common_count / 10

    print(f"\n最常出現的答案: {most_common_answer}")
    print(f"穩定度: {stability:.3f} ({most_common_count}/10 次)")

if __name__ == "__main__":
    main()
