#!/usr/bin/env python3
"""
Fox每日新闻日报 v3.2
增加AI数据源、来源显示、搜索链接
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from urllib.parse import quote

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "news-aggregator"))

from sources import NewsItem, SOURCE_REGISTRY, GROUP_MAPPING, list_sources
from core.fetcher import ResilientFetcher, fetch_group
from core.health import health_tracker
from core.cache import cache_manager

# 导入分析引擎
try:
    from analysis import analyze_correlations, filter_alert_news, analyze_entities
    ANALYSIS_AVAILABLE = True
except ImportError:
    ANALYSIS_AVAILABLE = False

# 导入RSS聚合器（保留）
try:
    from config.sources import RSS_SOURCES, EXTENDED_RSS_SOURCES
    from config.ai_sources import AI_RSS_SOURCES
    from core.rss import aggregate_all_rss
    RSS_AVAILABLE = True
except ImportError:
    RSS_AVAILABLE = False
    AI_RSS_SOURCES = {}

# 网页数据输出目录
WEB_DATA_DIR = Path("/var/www/news/data")

def export_json(all_news: Dict[str, List]):
    """导出JSON数据供网页使用"""
    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    json_data = {
        "date": today,
        "generated_at": datetime.now().isoformat(),
        "sections": {}
    }
    
    # 分组名称映射
    group_names = {
        "daily": "60秒读懂世界",
        "weibo": "微博热搜",
        "zhihu": "知乎热榜",
        "bilibili": "B站热搜",
        "douyin": "抖音热点",
        "toutiao": "今日头条",
        "douban": "豆瓣电影",
        "v2ex": "V2EX热帖",
        "thepaper": "澎湃新闻",
        "epic": "Epic免费游戏",
        "tech_intl": "国际科技",
        "tech_cn": "中文科技",
        "finance": "财经新闻",
        "science": "科学文化",
        "intelligence": "国际情报",
        "ai_models": "AI大模型",
        "ai_opensource": "AI开源生态",
        "ai_research": "AI前沿论文",
        "ai_tools": "AI开发工具",
        "ai_news": "AI行业动态",
        "ai_china": "AI中文资讯"
    }
    
    total_count = 0
    for group_id, items in all_news.items():
        if not items:
            continue
        
        group_name = group_names.get(group_id, group_id)
        section = {
            "id": group_id,
            "name": group_name,
            "count": len(items),
            "items": []
        }
        
        for item in items[:30]:
            url = getattr(item, 'url', '') or ''
            
            # 如果没有URL，生成Bing搜索链接
            search_url = ''
            if not url:
                search_url = f"https://www.bing.com/search?q={quote(item.title)}"
            
            item_data = {
                "title": item.title,
                "url": url,
                "searchUrl": search_url,
                "hasUrl": bool(url),
                "source": group_name,  # 添加来源
            }
            
            # 热度值
            if hasattr(item, 'hot_value') and item.hot_value:
                item_data["hot"] = item.hot_value
                item_data["hot_text"] = f"{item.hot_value // 10000}万" if item.hot_value >= 10000 else str(item.hot_value)
            
            # 评分（豆瓣）
            if hasattr(item, 'extra') and item.extra:
                if "rating" in item.extra:
                    item_data["rating"] = item.extra["rating"]
                if "source" in item.extra:
                    item_data["source"] = item.extra["source"]
                if "original_price" in item.extra:
                    item_data["price"] = item.extra["original_price"]
                if "end_date" in item.extra:
                    item_data["end_date"] = item.extra["end_date"]
            
            section["items"].append(item_data)
            total_count += 1
        
        json_data["sections"][group_id] = section
    
    json_data["stats"] = {
        "total": total_count,
        "groups": len(json_data["sections"])
    }
    
    # 保存今日数据
    today_file = WEB_DATA_DIR / f"{today}.json"
    with open(today_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    # 更新 latest.json
    latest_file = WEB_DATA_DIR / "latest.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    # 更新索引
    index_file = WEB_DATA_DIR / "index.json"
    index_data = {"dates": []}
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            index_data = json.load(f)
    
    if today not in index_data["dates"]:
        index_data["dates"].insert(0, today)
        index_data["dates"] = index_data["dates"][:30]
    
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ JSON数据已导出到: {WEB_DATA_DIR}")
    return today_file


def generate_daily_news_v3():
    """生成每日新闻日报 v3.1"""
    
    print("=" * 60)
    print("🦊 Fox每日新闻日报 v3.1")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    fetcher = ResilientFetcher(use_cache=True)
    report = []
    all_news = {}  # 收集所有新闻数据
    
    report.append("=" * 60)
    report.append("🦊 Fox每日新闻日报 v3.0")
    report.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 60)
    report.append("")
    
    # ==================== 60秒读懂世界 ====================
    print("\n📡 获取60秒读懂世界...")
    daily_items = fetcher.fetch_group('daily')
    all_news['daily'] = daily_items
    if daily_items:
        report.append("【60秒读懂世界】")
        report.append("")
        for i, item in enumerate(daily_items, 1):
            report.append(f"{i}. {item.title}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # ==================== 微博热搜 ====================
    print("📡 获取微博热搜...")
    weibo_items = fetcher.fetch_group('weibo')
    all_news['weibo'] = weibo_items
    if weibo_items:
        report.append("【微博热搜 Top 10】")
        report.append("")
        for i, item in enumerate(weibo_items[:10], 1):
            hot = item.hot_value
            hot_str = f"{hot // 10000}万" if hot >= 10000 else str(hot)
            report.append(f"{i}. {item.title} (🔥{hot_str})")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # ==================== 知乎热榜 ====================
    print("📡 获取知乎热榜...")
    zhihu_items = fetcher.fetch_group('zhihu')
    all_news['zhihu'] = zhihu_items
    if zhihu_items:
        report.append("【知乎热榜 Top 10】")
        report.append("")
        for i, item in enumerate(zhihu_items[:10], 1):
            report.append(f"{i}. {item.title}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # ==================== B站热搜 ====================
    print("📡 获取B站热搜...")
    bili_items = fetcher.fetch_group('bilibili')
    all_news['bilibili'] = bili_items
    if bili_items:
        report.append("【B站热搜 Top 10】")
        report.append("")
        for i, item in enumerate(bili_items[:10], 1):
            report.append(f"{i}. {item.title}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # ==================== 抖音热点 ====================
    print("📡 获取抖音热点...")
    douyin_items = fetcher.fetch_group('douyin')
    all_news['douyin'] = douyin_items
    if douyin_items:
        report.append("【抖音热点 Top 10】")
        report.append("")
        for i, item in enumerate(douyin_items[:10], 1):
            report.append(f"{i}. {item.title}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # ==================== 今日头条 ====================
    print("📡 获取今日头条...")
    toutiao_items = fetcher.fetch_group('toutiao')
    all_news['toutiao'] = toutiao_items
    if toutiao_items:
        report.append("【今日头条 Top 10】")
        report.append("")
        for i, item in enumerate(toutiao_items[:10], 1):
            report.append(f"{i}. {item.title}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # ==================== 豆瓣电影 ====================
    print("📡 获取豆瓣电影...")
    douban_items = fetcher.fetch_group('douban')
    all_news['douban'] = douban_items
    if douban_items:
        report.append("【豆瓣热门电影】")
        report.append("")
        for i, item in enumerate(douban_items[:10], 1):
            rating = item.extra.get("rating", 0)
            rating_str = f"⭐{rating}" if rating else ""
            report.append(f"{i}. {item.title} {rating_str}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # ==================== V2EX ====================
    print("📡 获取V2EX...")
    v2ex_items = fetcher.fetch_group('v2ex')
    all_news['v2ex'] = v2ex_items
    if v2ex_items:
        report.append("【V2EX热帖】")
        report.append("")
        for i, item in enumerate(v2ex_items[:10], 1):
            report.append(f"{i}. {item.title[:50]}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # ==================== 澎湃新闻 ====================
    print("📡 获取澎湃新闻...")
    thepaper_items = fetcher.fetch_group('thepaper')
    all_news['thepaper'] = thepaper_items
    if thepaper_items:
        report.append("【澎湃新闻热榜】")
        report.append("")
        for i, item in enumerate(thepaper_items[:10], 1):
            report.append(f"{i}. {item.title[:50]}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # ==================== Epic免费游戏 ====================
    print("📡 获取Epic免费游戏...")
    epic_items = fetcher.fetch_group('epic')
    all_news['epic'] = epic_items
    if epic_items:
        report.append("【Epic免费游戏】")
        report.append("")
        for item in epic_items:
            price = item.extra.get("original_price", "")
            end_date = item.extra.get("end_date", "")
            report.append(f"🎮 {item.title}")
            if price:
                report.append(f"   原价: {price}")
            if end_date:
                report.append(f"   截止: {end_date}")
            report.append("")
        report.append("-" * 60)
        report.append("")
    
    # ==================== RSS数据源 ====================
    rss_total = 0
    if RSS_AVAILABLE:
        print("\n📰 获取RSS数据源...")
        rss_data = aggregate_all_rss(use_cache=True)
        
        for group_id, items in rss_data.items():
            if not items:
                continue
            
            all_news[group_id] = items  # 添加到总数据
            
            group_name = RSS_SOURCES.get(group_id, EXTENDED_RSS_SOURCES.get(group_id, {})).get("name", group_id)
            rss_total += len(items)
            
            report.append(f"【{group_name}】")
            report.append("")
            for i, item in enumerate(items[:10], 1):
                report.append(f"{i}. [{item.source}] {item.title[:60]}")
            report.append("")
            report.append("-" * 60)
            report.append("")
    
    # ==================== 统计信息 ====================
    api_total = len(daily_items) + len(weibo_items) + len(zhihu_items) + \
                len(bili_items) + len(douyin_items) + len(toutiao_items) + \
                len(douban_items) + len(v2ex_items) + len(thepaper_items) + len(epic_items)
    total_items = api_total + rss_total
    
    report.append("【统计信息】")
    report.append("")
    report.append(f"📊 API数据源: {len(SOURCE_REGISTRY)}个 ({api_total}条)")
    if RSS_AVAILABLE:
        report.append(f"📰 RSS数据源: {len(RSS_SOURCES) + len(EXTENDED_RSS_SOURCES)}组 ({rss_total}条)")
    report.append(f"📈 总计: {total_items}条新闻")
    
    stats = health_tracker.get_stats()
    if stats["unhealthy"] > 0:
        report.append(f"⚠️ 不健康源: {stats['unhealthy']}个")
    
    report.append("")
    report.append("=" * 60)
    report.append(f"🦊 由 Fox v3.1 自动生成 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 60)
    
    # 导出JSON
    export_json(all_news)
    
    return "\n".join(report)


def main():
    report = generate_daily_news_v3()
    
    # 保存TXT
    output_path = Path(__file__).parent / "daily_news_report.txt"
    with open(output_path, "w") as f:
        f.write(report)
    
    print(f"\n✅ 日报已保存到: {output_path}")
    print(f"\n{health_tracker.get_report()}")


if __name__ == "__main__":
    main()
