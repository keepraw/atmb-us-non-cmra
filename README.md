# atmb-us-non-cmra

优选 [anytimemailbox](https://www.anytimemailbox.com/) 地址。

## 功能

结合 [第三方](https://www.smarty.com/) 查询接口，过滤出非 CMRA 的地址。
并按照是否为住宅地址进行排序。

运行结果保存为 csv 文件，可以在 [这里](./result/mailboxes.csv) 查看。

## 环境要求

- Python 3.8 或以上版本
- pip（Python 包管理器）
- Git

## 本地运行

1. 克隆项目到本地：
   ```bash
   git clone https://github.com/keepraw/atmb-us-non-cmra.git
   cd atmb-us-non-cmra
   ```

2. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 注册 [smarty](https://www.smarty.com/) 帐号，并获取 API key。由于免费帐号一个月只能查询 1000 次，而 atmb 目前有 1700 多个美国地址，所以至少需要注册两个帐号来完成查询。

4. 创建 `.env` 文件，添加以下内容：
   ```
   SMARTY_API_CREDENTIALS=API_ID1=API_TOKEN1,API_ID2=API_TOKEN2
   ```
   将 `API_ID1`、`API_TOKEN1` 等替换为实际的 API ID 和 TOKEN。

5. 运行程序：
   ```bash
   python -m src.main
   ```

6. 等待程序运行完成，查看运行结果：`result/mailboxes.csv`

## 使用 GitHub Action 自动更新

本项目支持使用 GitHub Action 自动更新地址列表。设置步骤如下：

1. Fork 本仓库到你的 GitHub 账号

2. 在你的仓库中设置 GitHub Secrets：
   - 进入仓库的 "Settings" > "Secrets and variables" > "Actions"
   - 点击 "New repository secret"
   - 名称填写：`SMARTY_API_CREDENTIALS`
   - 值填写：`API_ID1=API_TOKEN1,API_ID2=API_TOKEN2`
   - 点击 "Add secret" 保存

3. 启用 GitHub Actions：
   - 进入仓库的 "Actions" 标签页
   - 点击 "I understand my workflows, go ahead and enable them"

4. 手动触发工作流（可选）：
   - 在 "Actions" 标签页中，选择 "Update Mailbox List" 工作流
   - 点击 "Run workflow" 按钮

工作流将每月自动运行一次（每月1号），更新地址列表并提交到仓库。你也可以在 "Actions" 标签页中查看运行历史和日志。

**注意**：请确保你的 Smarty API 凭证安全，不要将其分享给他人或提交到公共仓库中。

## 项目结构

```
.
├── src/
│   ├── main.py           # 主程序入口
│   ├── atmb.py          # ATMB 网站爬虫
│   ├── smarty.py        # Smarty API 客户端
│   └── utils.py         # 工具函数
├── result/              # 结果输出目录
├── requirements.txt     # Python 依赖
└── .env                # 环境变量配置
```
