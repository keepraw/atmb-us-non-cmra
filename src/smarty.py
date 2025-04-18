import aiohttp
import asyncio
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from .utils import load_smarty_credentials
import requests
import json
import os
from dotenv import load_dotenv

@dataclass
class AddressInfo:
    """地址信息数据类"""
    is_cmra: bool
    is_residential: bool
    rdi: str  # Residential Delivery Indicator

class SmartyClient:
    """Smarty API 客户端"""
    
    def __init__(self):
        self.base_url = "https://us-street.api.smarty.com/street-address"
        self.credentials = self._load_credentials()
        self.current_credential_index = 0
    
    def _load_credentials(self) -> List[Tuple[str, str]]:
        """加载所有 Smarty API 凭证"""
        load_dotenv()
        credentials = []
        
        # 从环境变量中加载多个凭证
        index = 1
        while True:
            auth_id = os.getenv(f"SMARTY_AUTH_ID_{index}")
            auth_token = os.getenv(f"SMARTY_AUTH_TOKEN_{index}")
            
            if not auth_id or not auth_token:
                break
                
            credentials.append((auth_id, auth_token))
            index += 1
        
        if not credentials:
            raise ValueError("未找到任何 Smarty API 凭证。请确保在 .env 文件中设置了至少一组 SMARTY_AUTH_ID_1 和 SMARTY_AUTH_TOKEN_1。")
        
        return credentials
    
    def _get_next_credentials(self) -> Tuple[str, str]:
        """轮询获取下一个可用的 API 凭证"""
        auth_id, auth_token = self.credentials[self.current_credential_index]
        self.current_credential_index = (self.current_credential_index + 1) % len(self.credentials)
        return auth_id, auth_token
    
    def verify_address(self, address: str) -> Optional[Dict]:
        """验证地址信息"""
        try:
            auth_id, auth_token = self._get_next_credentials()
            
            params = {
                "auth-id": auth_id,
                "auth-token": auth_token,
                "street": address,
                "match": "enhanced"
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            results = response.json()
            if not results:
                return None
                
            result = results[0]
            
            # 返回标准化的结果
            return {
                "delivery_line_1": result.get("delivery_line_1", ""),
                "last_line": result.get("last_line", ""),
                "components": {
                    "city_name": result.get("components", {}).get("city_name", ""),
                    "state_abbreviation": result.get("components", {}).get("state_abbreviation", ""),
                    "zipcode": result.get("components", {}).get("zipcode", ""),
                },
                "metadata": {
                    "rdi": result.get("metadata", {}).get("rdi", ""),
                    "is_residential": result.get("metadata", {}).get("residential", "N"),
                    "building_default_indicator": result.get("metadata", {}).get("building_default_indicator", ""),
                    "carrier_route": result.get("metadata", {}).get("carrier_route", ""),
                    "congressional_district": result.get("metadata", {}).get("congressional_district", ""),
                    "county_fips": result.get("metadata", {}).get("county_fips", ""),
                    "county_name": result.get("metadata", {}).get("county_name", ""),
                    "dpc": result.get("metadata", {}).get("dpc", ""),
                    "elot_sequence": result.get("metadata", {}).get("elot_sequence", ""),
                    "elot_sort": result.get("metadata", {}).get("elot_sort", ""),
                    "latitude": result.get("metadata", {}).get("latitude", ""),
                    "longitude": result.get("metadata", {}).get("longitude", ""),
                    "precision": result.get("metadata", {}).get("precision", ""),
                    "time_zone": result.get("metadata", {}).get("time_zone", ""),
                    "utc_offset": result.get("metadata", {}).get("utc_offset", ""),
                    "dst": result.get("metadata", {}).get("dst", ""),
                },
                "analysis": {
                    "dpv_match_code": result.get("analysis", {}).get("dpv_match_code", ""),
                    "dpv_footnotes": result.get("analysis", {}).get("dpv_footnotes", ""),
                    "cmra": result.get("analysis", {}).get("cmra", ""),
                    "vacant": result.get("analysis", {}).get("vacant", ""),
                    "active": result.get("analysis", {}).get("active", ""),
                    "footnotes": result.get("analysis", {}).get("footnotes", ""),
                }
            }
            
        except requests.exceptions.RequestException as e:
            print(f"验证地址时出错: {str(e)}")
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