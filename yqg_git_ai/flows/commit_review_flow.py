import subprocess
import re
import time
from ..ai_agent import ask_ai

def run_commit_review_flow(repo_path: str, commit_hash: str):
    """
    获取指定commit的summary和diff，调用AI给出review建议。
    """
    # 获取commit summary
    try:
        summary_proc = subprocess.run(
            ['git', 'show', '--no-patch', '--pretty=format:%s', commit_hash],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        summary = summary_proc.stdout.strip()
    except Exception as e:
        print(f"获取commit summary失败: {e}")
        return
    # 获取commit diff
    try:
        diff_proc = subprocess.run(
            ['git', 'show', '--pretty=format:', commit_hash],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        diff = diff_proc.stdout.strip()
    except Exception as e:
        print(f"获取commit diff失败: {e}")
        return
    if not diff:
        print("未检测到该commit的diff内容，跳过review。")
        return
    # 组装prompt
    max_len = 10000
    diff_short = diff[:max_len]
    prompt = (
        f"请帮我review下面这个git commit的diff，结合summary和代码内容，分为两部分输出：\n"
        f"1. 必须修正：列出所有必须要修正的严重问题，每点一句话，简明扼要。\n"
        f"2. 优化建议：列出可以进一步优化的建议，每点一句话，简明扼要。\n"
        f"请严格对比 summary 和代码 diff，重点检查代码实现是否完全符合 summary 的描述，是否有遗漏、误导或实现不符的情况。如发现 summary 与代码实现不一致、未覆盖、或有误导，请在'必须修正'部分明确指出。\n"
        f"请尽可能全面、细致地列出所有你能发现的问题和建议，不要遗漏任何细节。\n"
        f"只输出分点内容，不要输出任何思考过程、分析过程或<think>标签内容，也不要输出多余解释。\n"
        f"\ncommit summary：{summary}\n\ncommit diff：\n{diff_short}"
    )
    print("\nAI 正在比对 summary 与 commit diff，生成详细 review 建议 ...\n")
    start_time = time.time()
    review = ask_ai(prompt)
    elapsed = time.time() - start_time
    # 正则清理<think>标签
    review = re.sub(r'<think[\s\S]*?>[\s\S]*?</think>', '', review, flags=re.IGNORECASE).strip()
    print(f"\n===== AI 代码审查建议（本次AI review耗时 {elapsed:.1f}s） =====\n")
    print(review)
    print("\n===== 结束 =====\n") 