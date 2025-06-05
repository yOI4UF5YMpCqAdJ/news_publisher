#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量删除GitHub Actions中的所有workflow runs（运行记录）
适用于Windows系统，使用GitHub CLI
"""

import subprocess
import json
import sys
import time

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_gh_cli():
    """检查GitHub CLI是否安装并已登录"""
    print("检查GitHub CLI...")
    
    # 检查gh命令是否存在
    success, _, error = run_command("gh --version")
    if not success:
        print("❌ GitHub CLI未安装或未在PATH中")
        print("请先安装GitHub CLI: https://cli.github.com/")
        return False
    
    # 检查是否已登录
    success, output, error = run_command("gh auth status")
    if not success:
        print("❌ GitHub CLI未登录")
        print("请先运行: gh auth login")
        return False
    
    success, output, error = run_command("gh repo view")
    if not success:
        print("❌ 无法访问当前仓库")
        print("可能原因：")
        print("1. 没有仓库访问权限")
        print("2. 不在Git仓库目录中")
        print("3. 需要重新授权: gh auth login --scopes repo,workflow")
        return False
    
    print("✅ GitHub CLI已准备就绪")
    return True

def get_workflow_runs(limit=100):
    """获取所有workflow runs"""
    print(f"\n正在获取workflow runs (最多{limit}个)...")
    
    success, output, error = run_command(f"gh run list --limit {limit} --json databaseId,workflowName,status,conclusion,createdAt")
    if not success:
        print(f"❌ 获取workflow runs失败: {error}")
        return None
    
    if not output:
        print("没有找到任何workflow runs")
        return []
    
    try:
        runs = json.loads(output)
        return runs
    except json.JSONDecodeError as e:
        print(f"❌ 解析JSON失败: {e}")
        return None

def display_runs(runs):
    """显示workflow runs列表"""
    if not runs:
        return
    
    print(f"\n找到 {len(runs)} 个workflow runs:")
    print("-" * 80)
    print(f"{'ID':<12} {'状态':<12} {'结果':<12} {'工作流名称':<20} {'创建时间'}")
    print("-" * 80)
    
    for run in runs[:10]:  # 只显示前10个
        run_id = run.get('databaseId', 'N/A')
        workflow_name = run.get('workflowName', 'N/A')[:18]  # 截断长名称
        status = run.get('status', 'N/A')
        conclusion = run.get('conclusion', 'N/A') or 'N/A'
        created_at = run.get('createdAt', 'N/A')[:10]  # 只显示日期部分
        print(f"{run_id:<12} {status:<12} {conclusion:<12} {workflow_name:<20} {created_at}")
    
    if len(runs) > 10:
        print(f"... 还有 {len(runs) - 10} 个runs未显示")

def get_runs_by_status():
    """按状态分类获取runs"""
    print("\n按状态获取workflow runs...")
    
    # 可选的状态过滤
    statuses = ['completed', 'in_progress', 'queued', 'requested', 'waiting']
    
    all_runs = []
    for status in statuses:
        success, output, error = run_command(f"gh run list --status {status} --limit 50 --json databaseId,workflowName,status,conclusion")
        if success and output:
            try:
                runs = json.loads(output)
                all_runs.extend(runs)
                print(f"  - {status}: {len(runs)} 个runs")
            except:
                continue
    
    return all_runs

def confirm_deletion(runs):
    """确认删除操作"""
    print("\n" + "=" * 50)
    print(f"即将删除 {len(runs)} 个workflow runs")
    print("注意：此操作不可逆！")
    
    while True:
        response = input("确认要删除所有workflow runs吗？(y/N): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            print("请输入 y 或 n")

def delete_workflow_runs(runs, batch_size=10):
    """删除所有workflow runs"""
    if not runs:
        return
    
    print(f"\n开始删除 {len(runs)} 个workflow runs...")
    print(f"将分批处理，每批 {batch_size} 个")
    print("-" * 60)
    
    deleted_count = 0
    failed_count = 0
    
    # 分批处理
    for batch_start in range(0, len(runs), batch_size):
        batch_end = min(batch_start + batch_size, len(runs))
        batch_runs = runs[batch_start:batch_end]
        
        print(f"\n处理第 {batch_start//batch_size + 1} 批 ({batch_start + 1}-{batch_end}):")
        
        for i, run in enumerate(batch_runs):
            run_id = run.get('databaseId')
            workflow_name = run.get('workflowName', 'Unknown')
            
            print(f"  [{batch_start + i + 1}/{len(runs)}] 删除: {workflow_name} (ID: {run_id})")
            
            # 删除workflow run
            success, output, error = run_command(f"gh run delete {run_id}")
            
            if success:
                print(f"  ✅ 成功删除")
                deleted_count += 1
            else:
                print(f"  ❌ 删除失败: {error}")
                failed_count += 1
            
            # 批内延迟
            time.sleep(0.2)
        
        # 批间延迟，避免API限制
        if batch_end < len(runs):
            print(f"  等待 2 秒后处理下一批...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("删除完成！")
    print(f"成功删除: {deleted_count} 个runs")
    print(f"删除失败: {failed_count} 个runs")

def delete_runs_by_workflow():
    """按workflow分别删除runs"""
    print("\n获取各个workflow的runs...")
    
    # 先获取所有workflow
    success, output, error = run_command("gh workflow list --json id,name")
    if not success:
        print(f"❌ 获取workflows失败: {error}")
        return
    
    try:
        workflows = json.loads(output)
    except:
        print("❌ 解析workflows失败")
        return
    
    print(f"找到 {len(workflows)} 个workflows")
    
    for workflow in workflows:
        workflow_id = workflow.get('id')
        workflow_name = workflow.get('name')
        
        print(f"\n处理workflow: {workflow_name}")
        
        # 获取该workflow的所有runs
        success, output, error = run_command(f"gh run list --workflow {workflow_id} --limit 100 --json databaseId")
        if success and output:
            try:
                runs = json.loads(output)
                if runs:
                    print(f"  找到 {len(runs)} 个runs，开始删除...")
                    for run in runs:
                        run_id = run.get('databaseId')
                        subprocess.run(f"gh run delete {run_id}", shell=True, capture_output=True)
                        time.sleep(0.2)
                    print(f"  ✅ 完成删除 {workflow_name} 的所有runs")
                else:
                    print(f"  该workflow没有runs")
            except:
                print(f"  ❌ 处理该workflow失败")

def main():
    """主函数"""
    print("GitHub Actions Workflow Runs 批量删除工具")
    print("=" * 60)
    
    # 检查环境
    if not check_gh_cli():
        sys.exit(1)
    
    print("\n选择删除方式:")
    print("1. 删除所有workflow runs (推荐)")
    print("2. 按workflow分别删除runs")
    print("3. 退出")
    
    while True:
        choice = input("\n请选择 (1-3): ").strip()
        if choice == '1':
            # 获取所有runs
            runs = get_workflow_runs(200)  # 获取更多runs
            if runs is None:
                sys.exit(1)
            
            if not runs:
                print("✅ 没有需要删除的workflow runs")
                sys.exit(0)
            
            # 显示runs
            display_runs(runs)
            
            # 确认删除
            if not confirm_deletion(runs):
                print("操作已取消")
                sys.exit(0)
            
            # 执行删除
            delete_workflow_runs(runs)
            break
            
        elif choice == '2':
            delete_runs_by_workflow()
            break
            
        elif choice == '3':
            print("程序退出")
            sys.exit(0)
        else:
            print("请输入 1、2 或 3")
    
    print("\n程序执行完成！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        sys.exit(1)