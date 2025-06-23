import openai
from .config import load_config

def ask_ai(prompt: str) -> str:
    config = load_config()
    api_key = config.get("api_key", "")
    base_url = config.get("base_url", "https://metahk.zenymes.com/v1")
    model = config.get("model", "deepseek-ai/DeepSeek-R1")

    #print(f"[yqg-git-ai] 当前使用的API KEY: {api_key}")
    if not api_key:
        raise ValueError("[yqg-git-ai] config.json 未正确配置 api_key，请检查当前目录下的 config.json 文件！")

    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个中文AI助手，善于理解和帮助开发者。"},
            {"role": "user", "content": prompt}
        ],
        stream=False
    )
    return response.choices[0].message.content.strip()
