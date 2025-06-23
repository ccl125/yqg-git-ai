import git
from typing import List

def get_remote_branches(repo_path: str) -> List[str]:
    repo = git.Repo(repo_path)
    return [ref.name for ref in repo.remotes.origin.refs]

def create_branch_from(repo_path: str, base_branch: str, new_branch: str):
    repo = git.Repo(repo_path)
    # 处理远端分支名
    if base_branch.startswith("origin/"):
        local_base = base_branch.replace("origin/", "")
        if local_base not in repo.heads:
            repo.git.checkout('-b', local_base, base_branch)
        else:
            repo.git.checkout(local_base)
    else:
        local_base = base_branch
        repo.git.checkout(local_base)
    repo.git.pull('origin', local_base)
    # 检查新分支是否已存在
    if new_branch in repo.heads:
        repo.git.checkout(new_branch)
        return "existed"
    else:
        repo.git.checkout('-b', new_branch)
        return "created"

def cherry_pick_commits(repo_path: str, commits: List[str]):
    repo = git.Repo(repo_path)
    for commit in commits:
        repo.git.cherry_pick(commit)

def push_branch(repo_path: str, branch: str):
    repo = git.Repo(repo_path)
    repo.git.push('--set-upstream', 'origin', branch)

