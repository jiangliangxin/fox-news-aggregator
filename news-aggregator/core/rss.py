"""
RSS聚合器

从RSS数据源获取新闻
"""

import time
import hashlib
import feedparser
import requests
from typing import List, Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RSSItem:
    """RSS新闻项"""
    title: str
    url: str
    source: str
    category: str
    pub_date: int = 0
    summary: str = ""
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "category": self.category,
            "pub_date": self.pub_date,
            "summary": self.summary,
        }


class RSSAggregator:
    """RSS聚合器"""
    
    def __init__(self, cache_dir: str = ".cache", cache_ttl: int = 1800):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = cache_ttl
    
    def _get_cache_path(self, url: str) -> Path:
        key = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"rss_{key}.json"
    
    def fetch_feed(self, url: str, use_cache: bool = True) -> List[RSSItem]:
        """获取单个RSS源"""
        
        cache_path = self._get_cache_path(url)
        
        # 检查缓存
        if use_cache and cache_path.exists():
            cache_age = time.time() - cache_path.stat().st_mtime
            if cache_age < self.cache_ttl:
                try:
                    import json
                    with open(cache_path, "r") as f:
                        data = json.load(f)
                    return [RSSItem(**item) for item in data]
                except:
                    pass
        
        # 获取RSS
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(resp.content)
            
            items = []
            for entry in feed.entries[:10]:  # 每个源最多10条
                items.append(RSSItem(
                    title=entry.get("title", ""),
                    url=entry.get("link", ""),
                    source=feed.feed.get("title", ""),
                    category="rss",
                    pub_date=int(time.mktime(entry.get("published_parsed", time.localtime()))),
                    summary=entry.get("summary", "")[:200],
                ))
            
            # 缓存
            if use_cache and items:
                import json
                with open(cache_path, "w") as f:
                    json.dump([item.to_dict() for item in items], f)
            
            return items
        except Exception as e:
            print(f"  ⚠️ RSS获取失败 {url}: {e}")
            return []
    
    def fetch_group(self, feeds: List[str], group_name: str = "") -> List[RSSItem]:
        """获取一组RSS源"""
        all_items = []
        
        for url in feeds:
            source_name = url.split("/")[2] if "/" in url else url
            print(f"    - {source_name}...", end=" ")
            
            items = self.fetch_feed(url)
            print(f"✅ {len(items)}条" if items else "❌")
            
            all_items.extend(items)
        
        # 按时间排序
        all_items.sort(key=lambda x: x.pub_date, reverse=True)
        
        return all_items


def aggregate_all_rss(use_cache: bool = True) -> Dict[str, List[RSSItem]]:
    """聚合所有RSS源"""
    from config.sources import RSS_SOURCES, EXTENDED_RSS_SOURCES
    
    # 尝试导入 AI 数据源
    try:
        from config.ai_sources import AI_RSS_SOURCES
    except ImportError:
        AI_RSS_SOURCES = {}
    
    aggregator = RSSAggregator()
    result = {}
    
    # 主RSS源
    print("\n📰 获取RSS数据源...")
    for group_id, group_config in RSS_SOURCES.items():
        print(f"\n  【{group_config['name']}】")
        items = aggregator.fetch_group(group_config['feeds'])
        result[group_id] = items
    
    # 扩展RSS源
    print("\n📰 获取扩展RSS数据源...")
    for group_id, group_config in EXTENDED_RSS_SOURCES.items():
        print(f"\n  【{group_config['name']}】")
        items = aggregator.fetch_group(group_config['feeds'])
        result[group_id] = items
    
    # AI专业数据源
    if AI_RSS_SOURCES:
        print("\n🤖 获取AI数据源...")
        for group_id, group_config in AI_RSS_SOURCES.items():
            print(f"\n  【{group_config['name']}】")
            items = aggregator.fetch_group(group_config['feeds'])
            result[group_id] = items
    
    return result
