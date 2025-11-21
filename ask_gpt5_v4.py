# ask_gpt5_no_ppv.py
import re
from openai import OpenAI
from questions_list import questions_list  # 你的題目 list
import os
import time

# 系統提示，不帶 PPV
PERSONA_PROMPT = """
你是一個具有固定決策傾向的角色，回答問題時遵循以下原則：
1. 優先選擇穩健、可控、長期有利的選項。
2. 避免極端或冒險的選擇。

【回答規則】
- 每題僅回答 A~E 中一個選項。
- 答案應保持一致性，但允許少量波動。
- 不要解釋，不要描述理由，只回答選項字母。
"""

# 建立 OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_one_round():
    messages = [{"role": "system", "content": PERSONA_PROMPT}]
    for idx, q in enumerate(questions_list):
        q_text = f"第 {idx+1} 題: {q['q']}\n選項: {', '.join(q['options'])}"
        messages.append({"role": "user", "content": q_text})

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages
    )
    answer_text = response.choices[0].message.content.strip()
    answers = re.findall(r"[A-E]", answer_text)  # 抓 A~E
    return answers

def main(rounds=10):
    all_rounds = []
    for i in range(1, rounds+1):
        print(f"\n=== 回合 {i} ===")
        try:
            answers = ask_one_round()
            print("答案:", " ".join(answers))
            all_rounds.append(answers)
        except Exception as e:
            print(f"回合 {i} 發生錯誤: {e}")
            all_rounds.append([])
        time.sleep(1)  # 避免請求過快

    print("\n=== 全部回合結果 ===")
    for i, ans in enumerate(all_rounds, 1):
        print(f"{i}: {' '.join(ans)}")

if __name__ == "__main__":
    main(10)
