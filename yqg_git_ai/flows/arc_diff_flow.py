import subprocess
import re
import os
from ..config import load_config
from ..ai_agent import ask_ai
import time

def run_arc_diff_flow(repo_path: str):
    """
    自动执行 arc diff --preview --browse，输出结果并高亮 Diff URI。
    若配置了AI，则对本次diff的patch内容进行AI review。
    """
    print("检查工作区状态...")
    # 检查 git 工作区是否干净
    status = subprocess.run(['git', 'status', '--porcelain'], cwd=repo_path, capture_output=True, text=True)
    if status.returncode != 0:
        print("无法获取 git 状态，请检查仓库！")
        return
    if status.stdout.strip():
        print("检测到有未提交的更改，请先提交后再执行 arc diff！")
        return
    
    print("执行 arc diff --preview --browse ...")
    try:
        result = subprocess.run(
            ['arc', 'diff', '--preview', '--browse'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        output = result.stdout + '\n' + result.stderr
        print(output)
        # 提取 Diff URI 并高亮
        match = re.search(r'Diff URI: (https?://\S+)', output)
        if match:
            print(f"\n[32mDiff URI: {match.group(1)}[0m")
        else:
            print("未检测到 Diff URI，请检查 arc diff 输出。")
    except Exception as e:
        print(f"执行 arc diff 失败: {e}")
        return

    # AI review 部分
    config = load_config()
    use_ai = config.get('use_ai', True)
    if not use_ai:
        print("未启用AI代码审查，已跳过 review。")
        return

    print("\n正在获取本次 diff 的 patch 内容并调用 AI 进行 review...")
    try:
        # 提取 Diff ID
        match = re.search(r'Diff URI: https?://\S+/diff/(\d+)/', output)
        if not match:
            # 尝试更宽松的正则匹配
            match = re.search(r'Diff URI: https?://.*/diff/(\d+)/', output)
        if not match:
            print("未检测到 Diff ID，跳过 review。")
            return
        diff_id = match.group(1)
        # 用 arc export 获取 patch，增加 --git 参数
        arc_proc = subprocess.run(
            ['arc', 'export', '--diff', diff_id, '--git'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        patch = arc_proc.stdout.strip()
        # print("\n[调试] patch内容预览：\n" + patch[:500] + "\n[调试结束]\n")
        if not patch:
            print("未检测到 diff 变更内容，跳过 review。")
            return
        # 只截取前10,000字符，防止 prompt 过长
        max_len = 10000
        patch_short = patch[:max_len]
        prompt = (
            "请帮我 review 下面的代码 diff patch，分为两部分输出：\n"
            "1. 必须修正：列出所有必须要修正的严重问题，每点一句话，简明扼要。\n"
            "2. 优化建议：列出可以进一步优化的建议，每点一句话，简明扼要。\n"
            "只输出分点内容，不要输出任何思考过程、分析过程或 <think> 标签内容，也不要输出多余解释。\n"
            f"\n代码 diff patch：\n{patch_short}"
        )
        print("\nAI 正在分析 diff ...\n")
        start_time = time.time()
        review = ask_ai(prompt)
        elapsed = time.time() - start_time
        # 只在这里做正则清理，去除<think>...</think>及其内容
        review = re.sub(r'<think[\s\S]*?>[\s\S]*?</think>', '', review, flags=re.IGNORECASE).strip()
        print(f"\n===== AI 代码审查建议（本次AI review耗时 {elapsed:.1f}s） =====\n")
        print(review)
        print("\n===== 结束 =====\n")
    except Exception as e:
        print(f"AI review 失败: {e}") 