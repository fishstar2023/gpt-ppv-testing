# ask_gpt5_v2_finetuned_prompt.py
import json
from openai import OpenAI
from questions_list import questions_list  # 你的題目 list
import os
from collections import Counter
import pandas as pd
from datetime import datetime

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
- 請仔細思考並且基於 PPV 中的哪些具體維度做出選擇。
- 請先回答選項字母（A~E），然後用 1-2 句話簡明扼要地說明選擇這個答案的理由。
- 在回答時，請附上選擇當下時的信心水準（0-100分，100分代表最有信心）。
- 若有不確定的部分，請給予較低的信心分數（例如：30-50分）。
- 請依序回答所有題目，格式範例：
  第1題：A（理由說明）- 信心水準：85分
  第2題：B（理由說明）- 信心水準：70分
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

    # 顯示完整回答
    print(f"\n完整回答:\n{answer_text}")

    # 將答案拆成 list (A~E) - 使用更精確的提取方式
    import re
    # 尋找「第N題：X」的模式
    pattern = r'第\d+題[：:]\s*([A-E])'
    matches = re.findall(pattern, answer_text)
    answers = matches if matches else [a for a in answer_text if a in ["A","B","C","D","E"]]

    # 提取信心水準（0-100分）
    confidence_pattern = r'信心水準[：:]\s*(\d+)'
    confidence_matches = re.findall(confidence_pattern, answer_text)

    # 將信心水準轉換為數值
    confidence_scores = [int(score) for score in confidence_matches]

    # 驗證答案數量（僅在出錯時顯示）
    if len(answers) != len(questions_list):
        print(f"警告：預期 {len(questions_list)} 個答案，但得到 {len(answers)} 個")
        print(f"提取到的答案: {answers}")

    return answers, answer_text, confidence_scores


def compute_stability(all_rounds):
    """計算每一題的穩定度"""
    if not all_rounds or not all_rounds[0]:
        return []

    num_questions = len(questions_list)
    stability_results = []

    for q_idx in range(num_questions):
        # 收集第 q_idx 題所有回合的答案（跳過不完整的回合）
        answers = []
        for round_answers in all_rounds:
            if q_idx < len(round_answers):
                answers.append(round_answers[q_idx])

        if not answers:
            continue

        counter = Counter(answers)
        most_common_answer, count = counter.most_common(1)[0]

        stability = count / len(answers)

        stability_results.append({
            "question": q_idx + 1,
            "most_common": most_common_answer,
            "count": count,
            "total": len(answers),
            "stability": stability
        })

    return stability_results


def main(rounds=10):
    all_rounds = []
    all_full_responses = []
    all_confidence_scores = []
    for i in range(1, rounds+1):
        print(f"\n=== 回合 {i} ===")
        answers, full_response, confidence = ask_one_round()
        print("答案:", " ".join(answers))
        if confidence:
            avg_conf = sum(confidence) / len(confidence)
            print(f"本回合平均信心水準: {avg_conf:.2f}")
        all_rounds.append(answers)
        all_full_responses.append(full_response)
        all_confidence_scores.append(confidence)

    print("\n=== 全部回合答案 ===")
    for i, ans in enumerate(all_rounds, 1):
        print(f"{i}: {' '.join(ans)}")

    # ⭐ 計算穩定度
    stability_results = compute_stability(all_rounds)

    print("\n=== 每一題穩定度（Consistency）===\n")
    for s in stability_results:
        print(
            f"第 {s['question']} 題："
            f"最常出現 {s['most_common']}（{s['count']}/{s['total']} 次）｜"
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

    # 3. 完整回答內容和信心水準
    full_responses_data = []
    for i, response in enumerate(all_full_responses, 1):
        conf_scores = all_confidence_scores[i-1]
        avg_conf = sum(conf_scores) / len(conf_scores) if conf_scores else 0
        full_responses_data.append({
            "回合": i,
            "完整回答": response,
            "平均信心水準": round(avg_conf, 2)
        })

    # 4. 計算總體信心水準統計
    all_conf_flat = [score for conf_list in all_confidence_scores for score in conf_list]
    overall_avg_conf = sum(all_conf_flat) / len(all_conf_flat) if all_conf_flat else 0

    print(f"\n=== 信心水準統計 ===")
    print(f"總平均信心水準: {overall_avg_conf:.2f} 分")
    if all_conf_flat:
        print(f"最高信心: {max(all_conf_flat)} 分")
        print(f"最低信心: {min(all_conf_flat)} 分")
        # 分組統計
        high_conf = [s for s in all_conf_flat if s >= 80]
        mid_conf = [s for s in all_conf_flat if 50 <= s < 80]
        low_conf = [s for s in all_conf_flat if s < 50]
        print(f"高信心 (≥80分): {len(high_conf)} 次 ({len(high_conf)/len(all_conf_flat)*100:.1f}%)")
        print(f"中信心 (50-79分): {len(mid_conf)} 次 ({len(mid_conf)/len(all_conf_flat)*100:.1f}%)")
        print(f"低信心 (<50分): {len(low_conf)} 次 ({len(low_conf)/len(all_conf_flat)*100:.1f}%)")

    # 創建 Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # 寫入每回合答案
        df_rounds = pd.DataFrame(rounds_data)
        df_rounds.to_excel(writer, sheet_name='每回合答案', index=False)

        # 寫入穩定度統計
        df_stability = pd.DataFrame(stability_data)
        df_stability.to_excel(writer, sheet_name='穩定度統計', index=False)

        # 寫入完整回答和信心水準
        df_full = pd.DataFrame(full_responses_data)
        df_full.to_excel(writer, sheet_name='完整回答含理由', index=False)

        # 寫入信心水準統計
        if all_conf_flat:
            high_conf = [s for s in all_conf_flat if s >= 80]
            mid_conf = [s for s in all_conf_flat if 50 <= s < 80]
            low_conf = [s for s in all_conf_flat if s < 50]
            conf_summary = pd.DataFrame([{
                "總平均信心水準": round(overall_avg_conf, 2),
                "最高信心": max(all_conf_flat),
                "最低信心": min(all_conf_flat),
                "高信心(≥80分)次數": len(high_conf),
                "高信心百分比": round(len(high_conf)/len(all_conf_flat)*100, 1),
                "中信心(50-79分)次數": len(mid_conf),
                "中信心百分比": round(len(mid_conf)/len(all_conf_flat)*100, 1),
                "低信心(<50分)次數": len(low_conf),
                "低信心百分比": round(len(low_conf)/len(all_conf_flat)*100, 1),
                "總回答數": len(all_conf_flat)
            }])
            conf_summary.to_excel(writer, sheet_name='信心水準統計', index=False)

    print(f"\n✅ 結果已保存到: {filename}")

if __name__ == "__main__":
    main(10)
