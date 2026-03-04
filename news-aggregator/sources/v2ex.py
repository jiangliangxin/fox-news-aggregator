"""
V2EX热帖
https://www.v2ex.com/feed/share.json
"""

import requests
from . import NewsItem, BaseSource, register_source


@register_source
class V2EXSource(BaseSource):
    """V2EX热帖"""
    
    name = "V2EX"
    source_id = "v2ex"
    category = "tech"
    group = "v2ex"
    priority = 0
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    
    def fetch(self) -> list:
        url = "https://www.v2ex.com/feed/share.json"
        headers = {"User-Agent": self.USER_AGENT}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        items = []
        for item in data.get("items", []):
            items.append(NewsItem(
                id=item.get("id", item.get("url", "")),
                title=item.get("title", ""),
                url=item.get("url", ""),
                source="V2EX",
                category=self.category,
                extra={
                    "date": item.get("date_published", ""),
                    "content": item.get("content_html", "")[:200] if item.get("content_html") else "",
                },
            ))
        
        return items
