import aiohttp
import asyncio
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from .utils import load_smarty_credentials

@dataclass
class AddressInfo:
    """地址信息数据类"""
    is_cmra: bool
    is_residential: bool
    rdi: str  # Residential Delivery Indicator

class SmartyClient:
    """Smarty API 客户端"""
    BASE_URL = "https://us-street.api.smarty.com/street-address"
    
    def __init__(self):
        self.credentials = load_smarty_credentials()
        self.current_credential_index = 0
        self.credential_keys = list(self.credentials.keys())
    
    def _get_next_credentials(self) -> Tuple[str, str]:
        """轮询获取下一个可用的 API 凭证"""
        api_id = self.credential_keys[self.current_credential_index]
        api_token = self.credentials[api_id]
        self.current_credential_index = (self.current_credential_index + 1) % len(self.credential_keys)
        return api_id, api_token
    
    async def verify_address(self, address: str) -> Optional[AddressInfo]:
        """验证地址并返回详细信息"""
        api_id, api_token = self._get_next_credentials()
        
        params = {
            "street": address,
            "auth-id": api_id,
            "auth-token": api_token,
            "match": "enhanced"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.BASE_URL, params=params) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    if not data:
                        return None
                    
                    result = data[0]
                    metadata = result.get("metadata", {})
                    
                    return AddressInfo(
                        is_cmra=metadata.get("cmra", "").lower() == "y",
                        is_residential=metadata.get("rdi", "").lower() == "residential",
                        rdi=metadata.get("rdi", "unknown")
                    )
            except Exception as e:
                print(f"Error verifying address {address}: {str(e)}")
                return None

class SmartyClientPool:
    """Smarty API 客户端池，用于并发请求"""
    def __init__(self, pool_size: int = 3):
        self.clients = [SmartyClient() for _ in range(pool_size)]
        self.current_index = 0
    
    def get_client(self) -> SmartyClient:
        """获取下一个可用的客户端"""
        client = self.clients[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.clients)
        return client
    
    async def verify_addresses(self, addresses: List[str]) -> Dict[str, Optional[AddressInfo]]:
        """并发验证多个地址"""
        tasks = []
        for address in addresses:
            client = self.get_client()
            tasks.append(client.verify_address(address))
        
        results = await asyncio.gather(*tasks)
        return dict(zip(addresses, results)) 