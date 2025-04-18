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
   pip3 install -r requirements.txt
   ```

3. 注册 [smarty](https://www.smarty.com/) 帐号，并获取 API key。由于免费帐号一个月只能查询 1000 次，而 atmb 目前有 1700 多个美国地址，所以至少需要注册两个帐号来完成查询。

4. 创建 `.env` 文件，添加以下内容：
   ```
   # 第一个 Smarty 账号的凭证
   SMARTY_AUTH_ID_1=your_first_auth_id
   SMARTY_AUTH_TOKEN_1=your_first_auth_token
   
   # 第二个 Smarty 账号的凭证
   SMARTY_AUTH_ID_2=your_second_auth_id
   SMARTY_AUTH_TOKEN_2=your_second_auth_token
   
   # 如果需要更多账号，可以继续添加
   # SMARTY_AUTH_ID_3=your_third_auth_id
   # SMARTY_AUTH_TOKEN_3=your_third_auth_token
   ```
   将 `your_first_auth_id` 和 `your_first_auth_token` 替换为第一个账号的 API ID 和 TOKEN，
   将 `your_second_auth_id` 和 `your_second_auth_token` 替换为第二个账号的 API ID 和 TOKEN。

5. 运行程序：
   ```bash
   python3 -m src.main
   ```

6. 等待程序运行完成，查看运行结果：`non_cmra_mailboxes.csv`