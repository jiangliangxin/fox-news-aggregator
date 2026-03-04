"""
知乎热榜 - 官方API
https://www.zhihu.com/api/v3/feed/topstory/hot-list-web
"""

import requests
from . import NewsItem, BaseSource, register_source


@register_source
class ZhihuAPISource(BaseSource):
    """知乎热榜 - 官方API"""
    
    name = "知乎热榜"
    source_id = "zhihu_api"
    category = "hot"
    group = "zhihu"
    priority = 1  # 降级源（60s优先）
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    
    def fetch(self) -> list:
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-list-web?limit=30&desktop=true"
        headers = {"User-Agent": self.USER_AGENT}
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        items = []
        for item in data.get("data", []):
            target = item.get("target", {})
            title_area = target.get("title_area", {})
            link = target.get("link", {})
            metrics = target.get("metrics_area", {})
            
            items.append(NewsItem(
                id=link.get("url", "").split("/")[-1] or str(len(items)),
                title=title_area.get("text", ""),
                url=link.get("url", ""),
                source="知乎",
                category=self.category,
                hot_value=self._parse_hot(metrics.get("text", "0")),
            ))
        
        return items
    
    def _parse_hot(self, text: str) -> int:
        """解析热度值"""
        if not text:
            return 0
        
        text = text.replace(" ", "").replace(",", "")
        
        # 处理 "709热度" 这种格式
        if "热度" in text:
            text = text.replace("热度", "")
        
        if "万" in text:
            return int(float(text.replace("万", "")) * 10000)
        if "亿" in text:
            return int(float(text.replace("亿", "")) * 100000000)
        
        try:
            return int(float(text))
        except:
            return 0
