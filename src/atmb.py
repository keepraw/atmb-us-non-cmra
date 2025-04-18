import aiohttp
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Mailbox:
    """邮箱地址数据类"""
    name: str
    address: str
    city: str
    state: str
    zip_code: str

class ATMBCrawler:
    """ATMB 网站爬虫"""
    BASE_URL = "https://www.anytimemailbox.com/locations"
    
    async def fetch_mailboxes(self) -> List[Mailbox]:
        """获取所有邮箱地址"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch ATMB locations: {response.status}")
                
                html = await response.text()
                return self._parse_html(html)
    
    def _parse_html(self, html: str) -> List[Mailbox]:
        """解析 HTML 页面，提取邮箱地址信息"""
        soup = BeautifulSoup(html, 'html.parser')
        mailboxes = []
        
        # 查找所有邮箱地址卡片
        location_cards = soup.find_all('div', class_='location-card')
        
        for card in location_cards:
            try:
                name = card.find('h3', class_='location-name').text.strip()
                address_elem = card.find('div', class_='location-address')
                
                if not address_elem:
                    continue
                
                # 解析地址信息
                address_lines = [line.strip() for line in address_elem.text.split('\n') if line.strip()]
                if len(address_lines) < 3:
                    continue
                
                address = address_lines[0]
                city_state_zip = address_lines[1].split(',')
                if len(city_state_zip) != 2:
                    continue
                
                city = city_state_zip[0].strip()
                state_zip = city_state_zip[1].strip().split()
                if len(state_zip) != 2:
                    continue
                
                state = state_zip[0]
                zip_code = state_zip[1]
                
                mailboxes.append(Mailbox(
                    name=name,
                    address=address,
                    city=city,
                    state=state,
                    zip_code=zip_code
                ))
            except Exception as e:
                print(f"Error parsing location card: {str(e)}")
                continue
        
        return mailboxes 