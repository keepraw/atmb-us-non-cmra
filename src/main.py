import asyncio
import pandas as pd
from src.atmb import ATMBCrawler
from src.smarty import SmartyClient
from tqdm import tqdm
import os
import json
from dotenv import load_dotenv

async def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()
    
    # 初始化爬虫和 API 客户端
    crawler = ATMBCrawler()
    client = SmartyClient()
    
    # 获取邮箱地址
    print("正在获取 ATMB 邮箱地址...")
    mailboxes = await crawler.fetch_mailboxes()
    print(f"共获取到 {len(mailboxes)} 个邮箱地址")
    
    if not mailboxes:
        print("错误: 未能获取到任何邮箱地址。请检查 ATMB 网站是否可访问，或者更新硬编码的地址列表。")
        return
    
    # 验证地址信息
    print("正在验证地址信息...")
    verified_addresses = []
    
    # 使用 tqdm 显示进度
    for mailbox in tqdm(mailboxes, desc="处理地址批次"):
        try:
            # 构建完整地址
            full_address = f"{mailbox.address}, {mailbox.city}, {mailbox.state} {mailbox.zip_code}"
            
            # 验证地址
            result = client.verify_address(full_address)
            
            if result:
                # 添加原始邮箱信息
                result["original_name"] = mailbox.name
                result["original_address"] = mailbox.address
                result["original_city"] = mailbox.city
                result["original_state"] = mailbox.state
                result["original_zip_code"] = mailbox.zip_code
                
                # 添加必要的字段
                result["is_residential"] = result["metadata"]["is_residential"]
                result["rdi"] = result["metadata"]["rdi"]
                
                verified_addresses.append(result)
        except Exception as e:
            print(f"验证地址时出错: {str(e)}")
    
    # 转换为 DataFrame
    if not verified_addresses:
        print("错误: 未能成功验证任何地址。请检查 Smarty API 凭证是否正确，或者 API 服务是否可用。")
        return
        
    df = pd.DataFrame(verified_addresses)
    
    # 检查必要的列是否存在
    required_columns = ["is_residential", "rdi"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"错误: DataFrame 中缺少以下列: {', '.join(missing_columns)}")
        print("可用的列:", df.columns.tolist())
        return
    
    # 排序
    df = df.sort_values(["is_residential", "rdi"], ascending=[False, True])
    
    # 保存结果
    output_file = "non_cmra_mailboxes.csv"
    df.to_csv(output_file, index=False)
    print(f"结果已保存到 {output_file}")
    
    # 打印统计信息
    total = len(df)
    residential = len(df[df["is_residential"] == "Y"])
    commercial = len(df[df["is_residential"] == "N"])
    
    print(f"\n统计信息:")
    print(f"总地址数: {total}")
    print(f"住宅地址: {residential}")
    print(f"商业地址: {commercial}")
    
    # 保存为 JSON 格式
    json_file = "non_cmra_mailboxes.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
    print(f"JSON 格式结果已保存到 {json_file}")

if __name__ == "__main__":
    asyncio.run(main()) 