# ask_gpt5_v2.py
import json
from openai import OpenAI
from questions_list import questions_list  # 你的題目 list
import os

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
    # 依序加入每題
    for idx, q in enumerate(questions_list):
        q_text = f"第 {idx+1} 題: {q['q']}\n選項: {', '.join(q['options'])}"
        messages.append({"role": "user", "content": q_text})

    # 呼叫 GPT-5
    response = client.chat.completions.create(
        model="gpt-5.1-2025-11-13",
        messages=messages        # 移除 temperature 以避免錯誤
    )
    # 取得 GPT 回答
    answer_text = response.choices[0].message.content.strip()
    # 將答案拆成 list (A~E)
    answers = [a for a in answer_text if a in ["A","B","C","D","E"]]
    return answers

def main(rounds=50):
    all_rounds = []
    for i in range(1, rounds+1):
        print(f"\n=== 回合 {i} ===")
        answers = ask_one_round()
        print("答案:", " ".join(answers))
        all_rounds.append(answers)

    print("\n=== 十回合全部答案 ===")
    for i, ans in enumerate(all_rounds, 1):
        print(f"{i}: {' '.join(ans)}")

if __name__ == "__main__":
    main(50)
