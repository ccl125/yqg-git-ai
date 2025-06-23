import subprocess
import re

def run_daily_msg_flow(repo_path: str):
    """
    输出当前分支基于哪个分支创建、当前分支名、以及pick diff（hash+首行message）。
    """
    # 获取当前分支名
    try:
        branch_proc = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        current_branch = branch_proc.stdout.strip()
    except Exception as e:
        print(f"获取当前分支失败: {e}")
        return
    # 获取当前分支的上游/基准分支（假设命名规则为 releases/xxx_daily 或 origin/releases/xxx_daily）
    # 用 reflog 或 merge-base 方式推断
    try:
        # 获取所有本地分支和远程分支
        branch_list_proc = subprocess.run(
            ['git', 'branch', '-a'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        branches = branch_list_proc.stdout.strip().split('\n')
        # 只保留daily分支
        daily_branches = [b.strip().replace('remotes/origin/', '').replace('origin/', '').replace('* ', '')
                          for b in branches if 'daily' in b and b.strip() != current_branch]
        # 按日期排序，取最新的不是当前分支的daily分支作为base
        # 假设分支名格式为 releases/xxx_daily 或 releases/xxx_daily_x
        def extract_date(b):
            m = re.search(r'(\d{8})', b)
            return m.group(1) if m else ''
        daily_branches = sorted(daily_branches, key=extract_date, reverse=True)
        base_branch = ''
        for b in daily_branches:
            if b != current_branch:
                base_branch = b
                break
        if not base_branch:
            print("未找到合适的基准daily分支！")
            return
    except Exception as e:
        print(f"获取daily分支失败: {e}")
        return
    # 输出分支信息
    print(f"基于{base_branch}切{current_branch}")
    # 获取pick diff（当前分支相对于base分支的提交）
    try:
        log_proc = subprocess.run(
            ['git', 'log', f'{base_branch}..{current_branch}', '--pretty=format:%h %s'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        pick_diff = log_proc.stdout.strip()
        print("pick diff：")
        if pick_diff:
            print(pick_diff)
        else:
            print("无diff")
    except Exception as e:
        print(f"获取pick diff失败: {e}") 