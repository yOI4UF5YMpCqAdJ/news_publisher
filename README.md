运行在github Action
# 新闻推送服务

这是一个定时新闻推送服务，每10分钟检查一次所有新闻源的更新。

## 功能说明

- 自动从多个新闻源获取最新新闻
- 将新闻存储到数据库中
- 创建推送记录用于后续处理
- 支持多数据源配置

## 项目结构

```
├── api/
│   └── newsApi.py          # 新闻API调用接口
├── db/
│   ├── dbManager.py        # 数据库管理基类
│   ├── dbNewsInfos.py      # 新闻信息表操作类
│   ├── dbPushInfoLatest.py # 推送信息表操作类
│   └── tableStruct/        # 数据库表结构
├── .github/
│   └── workflows/          # GitHub Actions 配置
├── main.py                 # 主要任务代码
├── requirements.txt        # 项目依赖
└── news-source.json        # 新闻源配置
```

## 配置说明

1. 数据库配置
在 `db/.env` 文件中配置数据库连接信息：
```env
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
DB_CHARSET=utf8mb4
```

2. 新闻源配置
在 `news-source.json` 中配置新闻源信息：
```json
[
  {
    "id": "source_id",
    "name": "源名称"
  }
]
```

## 部署方法：使用 GitHub Actions

GitHub Actions 提供了免费的服务器资源来定时运行你的脚本，无需维护自己的服务器。

### 步骤 1: 将代码上传到 GitHub

1. 在 GitHub 上创建一个新仓库
2. 将本地代码上传到仓库：

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/news-publisher.git
git push -u origin main
```

### 步骤 2: 配置环境变量

在 GitHub 仓库中设置数据库连接所需的环境变量：

1. 打开仓库页面
2. 点击 "Settings" 标签
3. 在左侧菜单中点击 "Secrets and variables" → "Actions"
4. 点击 "New repository secret" 按钮
5. 添加以下 Secrets：
   - `DB_HOST`: 数据库主机地址
   - `DB_USER`: 数据库用户名
   - `DB_PASSWORD`: 数据库密码
   - `DB_NAME`: 数据库名称

### 步骤 3: 确认工作流程文件

项目中已包含 `.github/workflows/schedule.yml` 文件，它配置了 GitHub Actions 工作流程：

```yaml
name: Run News Publisher

on:
  schedule:
    - cron: '*/10 * * * *'  # 每10分钟运行一次
  workflow_dispatch:  # 允许手动触发

jobs:
  run-worker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        name: 检出代码
      
      - name: 设置 Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: 安装依赖
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: 运行任务
        run: python main.py
        env:
          DB_HOST: ${{ secrets.DB_HOST }}
          DB_USER: ${{ secrets.DB_USER }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          DB_NAME: ${{ secrets.DB_NAME }}
```

### 步骤 4: 监控执行情况

1. 在仓库页面点击 "Actions" 标签
2. 你将看到所有的工作流程运行记录
3. 点击任意一条记录可查看详细的执行日志
4. 如遇问题，可以根据日志进行排查

### 步骤 5: 手动触发工作流程

1. 在仓库页面点击 "Actions" 标签
2. 在左侧找到 "Run News Publisher" 工作流程
3. 点击 "Run workflow" 按钮
4. 确认后工作流程将立即执行

## 本地测试

运行主脚本：
```bash
python main.py
```

## 注意事项

1. GitHub Actions 有使用限制，但对于小型项目免费额度通常已足够：
   - 免费版每月有 2000 分钟的执行时间
   - 工作流程并行执行数量限制

2. 数据库连接：
   - 确保你的数据库允许来自 GitHub Actions 运行环境的连接
   - 考虑使用云数据库服务以确保可靠连接

3. 定时任务说明：
   - GitHub Actions 的定时任务不保证精确执行，可能会有几分钟的延迟
   - `*/10 * * * *` 表示每 10 分钟执行一次
