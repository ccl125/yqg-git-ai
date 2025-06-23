import os
import sys
from prompt_toolkit import prompt
from .ai_agent import ask_ai
from .flows.release_flow import run_release_flow
from .flows.cherry_pick_flow import run_cherry_pick_flow
from .flows.arc_diff_flow import run_arc_diff_flow
from .flows.commit_review_flow import run_commit_review_flow
from .flows.daily_msg_flow import run_daily_msg_flow
from .config import load_config
import re

def should_publish(user_input):
    prompt_text = f"""用户输入：{user_input}\n你是一个命令行助手，请判断用户是否有"发布代码"或"上线代码"的意图。如果有，只回复"是"；如果没有，只回复"否"。不要输出其他内容。"""
    reply = ask_ai(prompt_text).strip().replace(' ', '').replace('\n', '')
    # 只要最后一句是"是"，就认为有意图
    if reply.endswith('是'):
        return True
    # 或者只要有"是"且没有"否"
    if '是' in reply and '否' not in reply:
        return True
    return False

def should_cherry_pick(user_input):
    prompt_text = f"""用户输入：{user_input}\n你是一个命令行助手，请判断用户是否有"cherry-pick代码"或"挑选提交"或"pick diff"的意图。如果有，只回复"是"；如果没有，只回复"否"。不要输出其他内容。"""
    reply = ask_ai(prompt_text).strip().replace(' ', '').replace('\n', '')
    if reply.endswith('是'):
        return True
    if '是' in reply and '否' not in reply:
        return True
    return False

def should_arc_diff(user_input):
    prompt_text = f"""用户输入：{user_input}\n你是一个命令行助手，请判断用户是否有"提交diff"、"arc diff"、"上传代码审查"等意图。如果有，只回复"是"；如果没有，只回复"否"。不要输出其他内容。"""
    reply = ask_ai(prompt_text).strip().replace(' ', '').replace('\n', '')
    if reply.endswith('是'):
        return True
    if '是' in reply and '否' not in reply:
        return True
    return False

def should_commit_review(user_input):
    # 只要包含"review"和7位及以上的commit hash
    return bool(re.search(r'review\s*[a-f0-9]{7,}', user_input, re.IGNORECASE))

def main():
    config = load_config()
    use_ai = config.get('use_ai', True)
    username = config.get('username', '')
    repo_path = os.getcwd()
    user_input = ' '.join(sys.argv[1:])
    if not user_input:
        user_input = prompt('请输入指令: ')
        
    # 精确命令支持：review-hashid
    if user_input.strip().lower().startswith('review-'):
        hashid = user_input.strip()[7:]
        if re.fullmatch(r'[a-f0-9]{7,}', hashid, re.IGNORECASE):
            run_commit_review_flow(repo_path, hashid)
            return
    
    # 精确命令支持：daily-msg
    if user_input.strip().lower() == 'daily-msg':
        run_daily_msg_flow(repo_path)
        return
    
    # 如果是 daily-flow，直接执行发布流程
    if user_input.strip().lower() == 'daily-flow':
        run_release_flow(repo_path)
        return
        
    # 如果是 pick-diff，直接执行 cherry-pick 流程
    if user_input.strip().lower() == 'pick-diff':
        if not username:
            print("错误：请在 config.json 中配置你的用户名！")
            return
        run_cherry_pick_flow(repo_path, username)
        return
    
    # 如果是 arc-diff，直接执行 arc diff 流程
    if user_input.strip().lower() == 'arc-diff':
        run_arc_diff_flow(repo_path)
        return
        
    # 其他情况，根据配置决定是否使用 AI
    if use_ai:
        # 检查是否是review commit意图
        if should_commit_review(user_input):
            match = re.search(r'review\s*([a-f0-9]{7,})', user_input, re.IGNORECASE)
            if match:
                run_commit_review_flow(repo_path, match.group(1))
                return
        # 检查是否是发布意图
        if should_publish(user_input):
            run_release_flow(repo_path)
            return
            
        # 检查是否是 cherry-pick 意图
        if should_cherry_pick(user_input):
            if not username:
                print("错误：请在 config.json 中配置你的用户名！")
                return
            run_cherry_pick_flow(repo_path, username)
            return
        
        # 检查是否是 arc diff 意图
        if should_arc_diff(user_input):
            run_arc_diff_flow(repo_path)
            return
            
        print("收到，已为你取消相关操作")
    else:
        print("未知命令，请使用以下命令：")
        print("1. yqg-git daily-flow - 发布流程")
        print("2. yqg-git pick-diff  - Cherry-pick 流程")
        print("3. yqg-git arc-diff   - 提交 arc diff 审查")
        print("4. yqg-git review-hashid - review 某个commit diff")
        print("5. yqg-git daily-msg - 打印本次daily分支变更摘要")
        print("或在 config.json 启用AI模式。")

if __name__ == '__main__':
    main() 