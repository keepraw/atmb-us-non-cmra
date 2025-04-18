import os
from typing import Dict, List
from dotenv import load_dotenv

def load_smarty_credentials() -> Dict[str, str]:
    """
    从环境变量加载 Smarty API 凭证
    返回格式: {api_id: api_token}
    """
    load_dotenv()
    credentials_str = os.getenv('SMARTY_API_CREDENTIALS')
    if not credentials_str:
        raise ValueError("SMARTY_API_CREDENTIALS environment variable not set")
    
    credentials = {}
    for cred in credentials_str.split(','):
        api_id, api_token = cred.split('=')
        credentials[api_id.strip()] = api_token.strip()
    
    return credentials

def ensure_dir(directory: str) -> None:
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """将列表分割成指定大小的块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)] 