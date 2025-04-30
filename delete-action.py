import requests
import time
import os
from dotenv import load_dotenv

# 加载环境变量（可选）
load_dotenv()

# 配置信息
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "your_token_here")  # 从环境变量获取或手动设置
OWNER = os.getenv("GITHUB_OWNER", "owner_name_here")        # 仓库所有者
REPO = os.getenv("GITHUB_REPO", "repo_name_here")           # 仓库名称

# 请求头
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_all_workflow_runs():
    """获取所有工作流运行记录，处理分页"""
    all_runs = []
    page = 1
    per_page = 100  # 每页最大数量

    while True:
        print(f"获取第 {page} 页的工作流运行记录...")
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?per_page={per_page}&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"获取工作流运行记录失败: {response.status_code}")
            print(response.text)
            break
        
        data = response.json()
        runs = data.get("workflow_runs", [])
        
        if not runs:
            break  # 没有更多运行记录
            
        all_runs.extend(runs)
        page += 1
        
        # 检查是否还有下一页
        if "next" not in response.links:
            break
            
        # 避免触发API速率限制
        time.sleep(0.5)
    
    return all_runs

def delete_workflow_run(run_id):
    """删除指定ID的工作流运行记录"""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}"
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        return True
    else:
        print(f"删除运行记录 {run_id} 失败: {response.status_code}")
        print(response.text)
        return False

def main():
    # 检查令牌
    if GITHUB_TOKEN == "your_token_here":
        print("请先设置有效的GitHub令牌!")
        return
    
    # 获取所有工作流运行记录
    print(f"正在获取 {OWNER}/{REPO} 的所有工作流运行记录...")
    runs = get_all_workflow_runs()
    
    if not runs:
        print("没有找到工作流运行记录")
        return
    
    print(f"共找到 {len(runs)} 个工作流运行记录")
    
    # 确认删除
    confirm = input(f"确认要删除所有 {len(runs)} 个工作流运行记录吗? (y/n): ")
    if confirm.lower() != "y":
        print("操作已取消")
        return
    
    # 删除所有工作流运行记录
    success_count = 0
    for i, run in enumerate(runs, 1):
        run_id = run["id"]
        workflow_name = run.get("name", "Unknown workflow")
        print(f"[{i}/{len(runs)}] 正在删除 {workflow_name} (ID: {run_id})...")
        
        if delete_workflow_run(run_id):
            success_count += 1
            print(f"[{i}/{len(runs)}] 成功删除 {workflow_name} (ID: {run_id})")
        
        # 避免触发API速率限制
        time.sleep(1)
    
    print(f"\n删除完成! 成功: {success_count}/{len(runs)}")

if __name__ == "__main__":
    main()