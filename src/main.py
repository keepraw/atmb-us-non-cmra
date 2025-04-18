import asyncio
import pandas as pd
from typing import List
from tqdm import tqdm
from .atmb import ATMBCrawler, Mailbox
from .smarty import SmartyClientPool, AddressInfo
from .utils import ensure_dir, chunk_list

async def main():
    # 创建结果目录
    ensure_dir("result")
    
    # 获取所有邮箱地址
    print("正在获取 ATMB 邮箱地址...")
    crawler = ATMBCrawler()
    mailboxes = await crawler.fetch_mailboxes()
    print(f"共获取到 {len(mailboxes)} 个邮箱地址")
    
    # 创建 Smarty 客户端池
    client_pool = SmartyClientPool(pool_size=3)
    
    # 将地址分批处理，每批 10 个
    chunks = chunk_list(mailboxes, 10)
    results = []
    
    print("正在验证地址信息...")
    for chunk in tqdm(chunks, desc="处理地址批次"):
        addresses = [f"{m.address}, {m.city}, {m.state} {m.zip_code}" for m in chunk]
        address_info = await client_pool.verify_addresses(addresses)
        
        for mailbox, address in zip(chunk, addresses):
            info = address_info.get(address)
            if info and not info.is_cmra:
                results.append({
                    "name": mailbox.name,
                    "address": mailbox.address,
                    "city": mailbox.city,
                    "state": mailbox.state,
                    "zip_code": mailbox.zip_code,
                    "is_residential": info.is_residential,
                    "rdi": info.rdi
                })
    
    # 转换为 DataFrame 并排序
    df = pd.DataFrame(results)
    df = df.sort_values(["is_residential", "rdi"], ascending=[False, True])
    
    # 保存结果
    output_file = "result/mailboxes.csv"
    df.to_csv(output_file, index=False)
    print(f"结果已保存到 {output_file}")
    print(f"共找到 {len(df)} 个非 CMRA 地址")

if __name__ == "__main__":
    asyncio.run(main()) 