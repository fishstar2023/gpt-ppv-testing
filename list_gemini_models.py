import google.generativeai as genai
import os

# 設定 API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("正在列出所有可用的 Gemini 模型...\n")

try:
    # 列出所有模型
    models = genai.list_models()

    print("=== 可用的模型 ===\n")
    for model in models:
        # 檢查是否支援 generateContent
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
            print(f"  描述: {model.display_name}")
            print(f"  支援的方法: {', '.join(model.supported_generation_methods)}")
            print()

except Exception as e:
    print(f"錯誤: {e}")
