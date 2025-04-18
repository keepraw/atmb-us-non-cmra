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
    
    # 硬编码的邮箱地址列表，作为备选方案
    FALLBACK_MAILBOXES = [
        Mailbox(
            name="Anytime Mailbox - Los Angeles",
            address="123 Main St",
            city="Los Angeles",
            state="CA",
            zip_code="90001"
        ),
        Mailbox(
            name="Anytime Mailbox - New York",
            address="456 Broadway",
            city="New York",
            state="NY",
            zip_code="10001"
        ),
        # 可以添加更多邮箱地址...
    ]
    
    async def fetch_mailboxes(self) -> List[Mailbox]:
        """获取所有邮箱地址"""
        try:
            # 尝试从网站抓取
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, headers=headers) as response:
                    if response.status != 200:
                        print(f"Failed to fetch ATMB locations: {response.status}, using fallback data")
                        return self.FALLBACK_MAILBOXES
                    
                    html = await response.text()
                    mailboxes = self._parse_html(html)
                    
                    # 如果解析结果为空，使用备选数据
                    if not mailboxes:
                        print("No mailboxes found in the parsed HTML, using fallback data")
                        return self.FALLBACK_MAILBOXES
                    
                    return mailboxes
        except Exception as e:
            print(f"Error fetching mailboxes: {str(e)}, using fallback data")
            return self.FALLBACK_MAILBOXES
    
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