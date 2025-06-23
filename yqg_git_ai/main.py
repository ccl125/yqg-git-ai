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
    prompt_text = f"""用户输入：{user_input}\n你是一个命令行助手，请判断用户是否有\"发布代码\"或\"上线代码\"的意图。如果有，只回复\"是\"；如果没有，只回复\"否\"。不要输出其他内容。"""
    reply = ask_ai(prompt_text).strip().replace(' ', '').replace('\n', '')
    if reply.endswith('是'):
        return True
    if '是' in reply and '否' not in reply:
        return True
    return False

def should_cherry_pick(user_input):
    prompt_text = f"""用户输入：{user_input}\n你是一个命令行助手，请判断用户是否有\"cherry-pick代码\"或\"挑选提交\"或\"pick diff\"的意图。如果有，只回复\"是\"；如果没有，只回复\"否\"。不要输出其他内容。"""
    reply = ask_ai(prompt_text).strip().replace(' ', '').replace('\n', '')
    if reply.endswith('是'):
        return True
    if '是' in reply and '否' not in reply:
        return True
    return False

def should_arc_diff(user_input):
    prompt_text = f"""用户输入：{user_input}\n你是一个命令行助手，请判断用户是否有\"提交diff\"、\"arc diff\"、\"上传代码审查\"等意图。如果有，只回复\"是\"；如果没有，只回复\"否\"。不要输出其他内容。"""
    reply = ask_ai(prompt_text).strip().replace(' ', '').replace('\n', '')
    if reply.endswith('是'):
        return True
    if '是' in reply and '否' not in reply:
        return True
    return False

def should_commit_review(user_input):
    return bool(re.search(r'review\s*[a-f0-9]{7,}', user_input, re.IGNORECASE))

def print_help():
    print("""
yqg-git: AI 智能 Git 命令行助手

用法:
  yqg-git <命令> [参数]
  yqg-git <自然语言指令>

常用命令：
  daily-flow         自动拉取最新 daily 分支并创建新分支
  pick-diff          智能 cherry-pick 你在 master 上的提交
  arc-diff           一键 arc diff 并自动 AI 代码审查
  review <hashid>    review 某个 commit diff，AI 审查建议
  daily-msg          输出分支变更摘要

你也可以直接输入自然语言，如：
  yqg-git 我要发布代码
  yqg-git 帮我review 9d6f998f
  yqg-git 我要pick diff

更多用法请参考 README.md

【安全提示】
本工具不会自动强制 push，遇到冲突建议手动处理，确保代码安全和团队协作规范。
使用 AI 相关功能时，请注意代码隐私，避免上传密钥、凭证、敏感业务逻辑等信息。
""")

def main():
    config = load_config()
    use_ai = config.get('use_ai', True)
    username = config.get('username', '')
    repo_path = os.getcwd()

    known_cmds = ['daily-flow', 'pick-diff', 'arc-diff', 'daily-msg', 'review']

    # 无参数或--help/-h时输出帮助
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        return

    first_arg = sys.argv[1]
    if first_arg in known_cmds:
        if first_arg == 'daily-flow':
            run_release_flow(repo_path)
            return
        elif first_arg == 'pick-diff':
            if not username:
                print("错误：请在 config.json 中配置你的用户名！")
                return
            run_cherry_pick_flow(repo_path, username)
            return
        elif first_arg == 'arc-diff':
            run_arc_diff_flow(repo_path)
            return
        elif first_arg == 'daily-msg':
            run_daily_msg_flow(repo_path)
            return
        elif first_arg == 'review':
            if len(sys.argv) < 3:
                print("用法: yqg-git review <commit_hash>")
                return
            run_commit_review_flow(repo_path, sys.argv[2])
            return

    # 其余情况全部拼成自然语言，走AI分流
    user_input = ' '.join(sys.argv[1:])
    if use_ai:
        if should_commit_review(user_input):
            match = re.search(r'review\s*([a-f0-9]{7,})', user_input, re.IGNORECASE)
            if match:
                run_commit_review_flow(repo_path, match.group(1))
                return
        if should_publish(user_input):
            run_release_flow(repo_path)
            return
        if should_cherry_pick(user_input):
            if not username:
                print("错误：请在 config.json 中配置你的用户名！")
                return
            run_cherry_pick_flow(repo_path, username)
            return
        if should_arc_diff(user_input):
            run_arc_diff_flow(repo_path)
            return
        print("收到，已为你取消相关操作")
    else:
        print_help()

if __name__ == '__main__':
    main() 