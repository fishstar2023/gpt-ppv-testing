import json
from openai import OpenAI
import os

# 讀取 PPV 初始內容
with open("ppv_initial.json", "r", encoding="utf-8") as f:
    ppv = json.load(f)

# 讀取你的題目
from questions_list import QUESTIONS

# 使用環境變數的 API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(ppv, questions):
    """向 GPT 詢問一次完整 10 題，回傳答案 list"""

    prompt = (
        "你會根據以下 PPV 進行回答。\n"
        "請直接回答 10 題的選項（A~E），格式如：\n\n"
        "A,C,B,E,...（全部 10 題）\n\n"
        "若不確定也請選一個最接近的。不要輸出題目。\n\n"
        f"以下是 PPV：\n{json.dumps(ppv, ensure_ascii=False)}"
    )

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": "你是模擬使用者，需依照 PPV 風格回答選項題。"},
            {"role": "user", "content": prompt}
        ]
    )

    answer_text = response.choices[0].message.content.strip()

    # 去除標點與空白
    answers = [x.strip() for x in answer_text.replace("，", ",").split(",")]

    return answers


# ----------------------------
# 🔁 執行 10 次
# ----------------------------

all_results = []   # 用來回收 10 輪結果

for i in range(1, 11):
    print(f"\n=== Loop {i} ===")

    ans = ask_gpt(ppv, QUESTIONS)
    print("回答：", ans)

    all_results.append(ans)

print("\n========================")
print("🎯 十回合的全部回答如下：")
print("========================\n")

for i, res in enumerate(all_results, 1):
    print(f"第 {i} 回：{res}")
