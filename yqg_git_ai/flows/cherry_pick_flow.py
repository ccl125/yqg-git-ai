import os
from typing import List, Dict
from ..git_utils import get_remote_branches, cherry_pick_commits
from prompt_toolkit import prompt
import git
from .daily_msg_flow import run_daily_msg_flow

def is_commit_in_branch(repo: git.Repo, commit_hash: str, branch: str) -> bool:
    """检查提交是否在指定分支上"""
    try:
        # 使用 merge-base 命令检查提交是否可达
        merge_base = repo.git.merge_base(commit_hash, branch)
        # 获取提交的树对象
        commit_tree = repo.commit(commit_hash).tree
        # 获取merge-base的树对象
        base_tree = repo.commit(merge_base).tree
        # 如果两个树相同，说明这个提交在分支上
        return commit_tree == base_tree
    except git.exc.GitCommandError:
        return False

def get_user_commits(repo_path: str, username: str) -> List[Dict]:
    """获取指定用户在 master 上但未被应用到当前分支的提交"""
    repo = git.Repo(repo_path)
    
    print("正在更新 master 分支...")
    try:
        # 切换到 master 分支
        current_branch = repo.active_branch.name
        repo.git.checkout('master')
        # 更新 master 分支
        repo.git.pull('origin', 'master')
        # 切回原来的分支
        repo.git.checkout(current_branch)
    except git.exc.GitCommandError as e:
        print(f"更新 master 分支失败：{str(e)}")
        print("请确保没有未提交的更改，然后重试。")
        return []
    
    # 使用 git cherry 获取未被应用的提交
    commits = []
    try:
        # 获取所有未被应用的提交
        cherry_output = repo.git.cherry(current_branch, 'master')
        
        # cherry 输出格式：
        # + commit_hash (未应用的提交)
        # - commit_hash (已应用的提交)
        unpicked_hashes = set()
        for line in cherry_output.split('\n'):
            if not line:
                continue
            status, commit_hash = line.split()
            if status == '+':  # 只关注未应用的提交
                unpicked_hashes.add(commit_hash.strip())
        
        if unpicked_hashes:
            # 获取这些提交的详细信息
            for commit_hash in unpicked_hashes:
                try:
                    commit = repo.commit(commit_hash)
                    # 只关注用户自己的提交
                    if commit.author.name == username:
                        commits.append({
                            'hash': commit_hash,
                            'subject': commit.message.split('\n')[0],
                            'date': commit.authored_datetime.strftime('%Y-%m-%d %H:%M')
                        })
                except git.exc.GitCommandError:
                    continue
    except git.exc.GitCommandError:
        # 可能是新分支还没有提交
        pass
        
    # 按日期排序
    commits.sort(key=lambda x: x['date'])
    return commits

def select_commits(commits: List[Dict]) -> List[str]:
    """让用户选择要 cherry-pick 的提交"""
    if not commits:
        print("没有找到需要 pick 的提交！")
        return []
        
    print("\n找到以下提交：")
    for i, commit in enumerate(commits, 1):
        print(f"{i}. [{commit['date']}] {commit['subject']}")
        
    print("\n提示：输入 q 或 quit 可以退出")
    
    while True:
        selection = prompt('\n请输入要 cherry-pick 的提交编号（用空格分隔，如：1 2 3）: ')
        selection = selection.strip().lower()
        
        if selection in ['q', 'quit']:
            print("已取消操作")
            return []
            
        try:
            indices = [int(x) - 1 for x in selection.split()]
            if all(0 <= i < len(commits) for i in indices):
                return [commits[i]['hash'] for i in indices]
            else:
                print("输入的编号超出范围，请重试！")
        except ValueError:
            if selection:  # 只有当输入为空时不显示错误信息
                print("输入格式错误，请输入数字并用空格分隔！")

def run_cherry_pick_flow(repo_path: str, username: str):
    """运行 cherry-pick 流程"""
    print("正在查找你的提交...")
    commits = get_user_commits(repo_path, username)
    
    if not commits:
        print("在 master 分支上没有找到需要 pick 的提交！")
        return
        
    selected_hashes = select_commits(commits)
    if selected_hashes:
        print("\n开始 cherry-pick...")
        try:
            cherry_pick_commits(repo_path, selected_hashes)
            print("Cherry-pick 完成！")
            print("\n===== 本次分支变更摘要 =====")
            run_daily_msg_flow(repo_path)
            print("==========================\n")
        except git.exc.GitCommandError as e:
            print(f"Cherry-pick 过程中出错：{str(e)}")
            print("请手动解决冲突后继续。") 