import re
from datetime import date, datetime
from prompt_toolkit import prompt
from ..git_utils import get_remote_branches, create_branch_from
import git

def get_daily_branch_sort_key(branch_name):
    match = re.search(r'_(\d{8})_daily(?:_(\d+))?', branch_name)
    if match:
        date_part = int(match.group(1))
        num_part = int(match.group(2) or 0)
        return (date_part, num_part)
    return (0, 0)

def is_friday():
    return datetime.now().weekday() == 4  # 0是周一，4是周五
    #return datetime.now().weekday() == 0  # 临时改为周一测试

def run_release_flow(repo_path):
    repo = git.Repo(repo_path)
    print("正在拉取远端分支...")
    repo.remotes.origin.fetch()

    branches = get_remote_branches(repo_path)
    daily_branches = [b for b in branches if 'daily' in b]

    if not daily_branches:
        print("未找到任何 daily 分支！")
        return

    latest_daily = sorted(daily_branches, key=get_daily_branch_sort_key)[-1]

    today_str = date.today().strftime('%Y-%m-%d')
    print(f"最新的 daily 分支是：{latest_daily}，今天是 {today_str}")
    
    if is_friday():
        print("\n⚠️  友情提醒：今天是周五，非变更窗口期进行线上变更，需要格外谨慎！建议：")
        print("1. 确保测试充分覆盖")
        print("2. 避免大规模改动")
        print("3. 留出足够的观察时间")
        print("4. 确保有应急回滚方案\n")
    
    yn = prompt(f"是否要基于分支 {latest_daily} 切一个新分支？(Y/N): ")

    if yn.strip().lower() == 'y':
        today_branch_str = date.today().strftime('%Y%m%d')
        remote_prefix = '/'.join(latest_daily.split('/')[:-1])
        if remote_prefix.startswith('origin/'):
            remote_prefix = remote_prefix[len('origin/'):]
        base_name = latest_daily.split('/')[-1]
        prefix_match = re.match(r'(.+?_)\d{8}_daily', base_name)
        prefix = prefix_match.group(1) if prefix_match else "daily_"
        
        todays_branches = [b for b in daily_branches if f"_{today_branch_str}_daily" in b]
        
        if not todays_branches:
            suggested_branch = f"{remote_prefix}/{prefix}{today_branch_str}_daily"
        else:
            versions = [get_daily_branch_sort_key(b)[1] for b in todays_branches]
            next_version = max(versions) + 1
            suggested_branch = f"{remote_prefix}/{prefix}{today_branch_str}_daily_{next_version}"
        new_branch = prompt("请输入新分支名: ", default=suggested_branch)

        result = create_branch_from(repo_path, latest_daily, new_branch)
        if result == "created":
            print(f"已创建并切换到 {new_branch}")
        elif result == "existed":
            print(f"本地分支 {new_branch} 已存在，已切换到该分支。")
    else:
        yn2 = prompt(f"是否要切换到最新的 daily 分支 {latest_daily}？(Y/N): ")
        if yn2.strip().lower() == 'y':
            remote_branch_name = latest_daily  # 保持 origin/ 前缀
            local_branch_name = latest_daily.replace('origin/', '')
            if local_branch_name not in repo.heads:
                repo.git.checkout('-b', local_branch_name, remote_branch_name)
                print(f"本地不存在分支 {local_branch_name}，已基于远端创建并切换到该分支。")
            else:
                repo.git.checkout(local_branch_name)
                print(f"已切换到 {local_branch_name}")
        else:
            print("流程结束。\n")
        return 