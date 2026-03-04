#!/usr/bin/env python3
"""
Fox每日新闻日报 v4.0
激活分析引擎 + 智能摘要 + 历史对比
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
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
except ImportError as e:
    print(f"⚠️ 分析引擎导入失败: {e}")
    ANALYSIS_AVAILABLE = False

# 导入RSS聚合器
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
CACHE_DIR = Path(__file__).parent / "news-aggregator" / ".cache"


def load_yesterday_data() -> Dict:
    """加载昨日新闻数据"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    cache_file = CACHE_DIR / "yesterday.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("date") == yesterday:
                    return data
        except Exception as e:
            print(f"⚠️ 加载昨日数据失败: {e}")
    
    return {}


def save_today_data(all_news: Dict, analysis: Dict):
    """保存今日数据供明天对比"""
    today = datetime.now().strftime("%Y-%m-%d")
    cache_file = CACHE_DIR / "yesterday.json"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    data = {
        "date": today,
        "headlines": [],
        "topics": []
    }
    
    # 提取标题
    for group_id, items in all_news.items():
        for item in items[:5]:  # 每组取前5条
            data["headlines"].append(item.title)
    
    # 提取分析主题
    if analysis.get("correlations"):
        for topic in analysis["correlations"].get("emerging_patterns", []):
            data["topics"].append(topic.get("name", ""))
    
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compare_with_yesterday(all_news: Dict, yesterday_data: Dict) -> Dict:
    """与昨日对比"""
    if not yesterday_data:
        return {"new_topics": [], "faded_topics": []}
    
    today_headlines = set()
    for group_id, items in all_news.items():
        for item in items[:5]:
            today_headlines.add(item.title)
    
    yesterday_headlines = set(yesterday_data.get("headlines", []))
    
    new_headlines = today_headlines - yesterday_headlines
    faded_headlines = yesterday_headlines - today_headlines
    
    return {
        "new_count": len(new_headlines),
        "faded_count": len(faded_headlines),
        "new_topics": list(new_headlines)[:5],
        "faded_topics": list(faded_headlines)[:5]
    }


def convert_to_dict_list(all_news: Dict[str, List]) -> List[Dict]:
    """将 all_news 转换为分析引擎需要的格式"""
    news_list = []
    for group_id, items in all_news.items():
        for item in items:
            # 处理不同类型的新闻项（NewsItem 或 RSSItem）
                news_dict = {
                    "title": item.title,
                    "url": getattr(item, 'url', '') or '',
                    "source": getattr(item, 'source', '') or group_id,
                    "group": group_id,
                    "hot_value": getattr(item, 'hot_value', 0),
                    "pub_date": getattr(item, 'pub_date', 0),
                }
                news_list.append(news_dict)
    return news_list


def run_analysis(all_news: Dict) -> Dict:
    """运行分析引擎"""
    if not ANALYSIS_AVAILABLE:
        return {}
    
    results = {}
    
    # 转换数据格式
    news_list = convert_to_dict_list(all_news)
    print(f"  转换 {len(news_list)} 条新闻进行分析...")
    
    try:
        # 1. 跨源关联分析
        print("🔍 运行关联分析...")
        correlation_results = analyze_correlations(news_list)
        
        if correlation_results:
            results["correlations"] = {
                "emerging_patterns": [
                    {
                        "name": p.name,
                        "count": p.count,
                        "level": p.level,
                        "sources": p.sources[:3] if hasattr(p, 'sources') else []
                    }
                    for p in (correlation_results.emerging_patterns or [])[:10]
                ],
                "cross_source": [
                    {
                        "name": c.name,
                        "source_count": c.source_count,
                        "level": c.level
                    }
                    for c in (correlation_results.cross_source_correlations or [])[:5]
                ]
            }
        else:
            results["correlations"] = {}
    except Exception as e:
        print(f"⚠️ 关联分析失败: {e}")
        import traceback
        traceback.print_exc()
        results["correlations"] = {}
    
    try:
        # 2. 告警检测
        print("🚨 运行告警检测...")
        alert_results = filter_alert_news(news_list)
        
        if alert_results:
            # alert_results 是列表，每个元素有 alert_info 字段
            critical_alerts = []
            high_alerts = []
            
            for news in alert_results:
                alert_info = news.get("alert_info", {})
                severity = alert_info.get("alert_severity", "low")
                matched_keywords = alert_info.get("matched_keywords", [])
                keyword = matched_keywords[0] if matched_keywords else ""
                
                if severity == "critical":
                    critical_alerts.append({
                        "title": news.get("title", ""),
                        "keyword": keyword
                    })
                elif severity == "high":
                    high_alerts.append({
                        "title": news.get("title", ""),
                        "keyword": keyword
                    })
            
            results["alerts"] = {
                "critical": critical_alerts[:3],
                "high": high_alerts[:5]
            }
        else:
            results["alerts"] = {}
    except Exception as e:
        print(f"⚠️ 告警检测失败: {e}")
        import traceback
        traceback.print_exc()
        results["alerts"] = {}
    
    try:
        # 3. 实体追踪
        print("👤 运行实体追踪...")
        entity_results = analyze_entities(news_list)
        
        if entity_results:
            # entity_results 是 Dict[str, List[EntityMention]]
            all_entities = []
            for category, entities in entity_results.items():
                for e in entities:
                    all_entities.append({
                        "name": e.name,
                        "count": e.count,
                        "category": category
                    })
            
            # 按出现次数排序
            all_entities.sort(key=lambda x: x["count"], reverse=True)
            results["entities"] = all_entities[:10]
        else:
            results["entities"] = []
    except Exception as e:
        print(f"⚠️ 实体追踪失败: {e}")
        import traceback
        traceback.print_exc()
        results["entities"] = []
    
    return results


def format_smart_summary(analysis: Dict, comparison: Dict) -> List[str]:
    """格式化智能摘要"""
    summary = []
    summary.append("【智能分析】")
    summary.append("")
    
    # 发酵话题
    if analysis.get("correlations", {}).get("emerging_patterns"):
        summary.append("🔥 发酵话题:")
        for pattern in analysis["correlations"]["emerging_patterns"][:5]:
            sources_str = "/".join(pattern["sources"][:3])
            summary.append(f"   • {pattern['name']} ({pattern['count']}次 [{sources_str}])")
        summary.append("")
    
    # 跨源热点
    if analysis.get("correlations", {}).get("cross_source"):
        summary.append("🌐 跨源热点:")
        for item in analysis["correlations"]["cross_source"][:3]:
            summary.append(f"   • {item['name']} ({item['source_count']}个来源)")
        summary.append("")
    
    # 告警新闻
    alerts = analysis.get("alerts", {})
    if alerts.get("critical") or alerts.get("high"):
        summary.append("⚠️ 重要告警:")
        for alert in alerts.get("critical", [])[:2]:
            summary.append(f"   🔴 {alert['title']} (关键词: {alert['keyword']})")
        for alert in alerts.get("high", [])[:3]:
            summary.append(f"   🟡 {alert['title']} (关键词: {alert['keyword']})")
        summary.append("")
    
    # 热门人物
    if analysis.get("entities"):
        summary.append("👤 热门人物:")
        entities_str = ", ".join([f"{e['name']}({e['count']})" for e in analysis["entities"][:5]])
        summary.append(f"   {entities_str}")
        summary.append("")
    
    # 历史对比
    if comparison.get("new_count"):
        summary.append("📊 历史对比:")
        summary.append(f"   新增热点: {comparison['new_count']}条")
        summary.append(f"   退热话题: {comparison['faded_count']}条")
        if comparison.get("new_topics"):
            summary.append(f"   新话题: {', '.join(comparison['new_topics'][:3])}")
        summary.append("")
    
    summary.append("-" * 60)
    summary.append("")
    
    return summary


def export_json(all_news: Dict, analysis: Dict):
    """导出JSON数据供网页使用"""
    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    json_data = {
        "date": today,
        "generated_at": datetime.now().isoformat(),
        "analysis": {
            "emerging_patterns": analysis.get("correlations", {}).get("emerging_patterns", []),
            "alerts": analysis.get("alerts", {}),
            "entities": analysis.get("entities", [])
        },
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
                "source": group_name,
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


def generate_daily_news_v4():
    """生成每日新闻日报 v4.0 - 带智能分析"""
    
    print("=" * 60)
    print("🦊 Fox每日新闻日报 v4.0")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    fetcher = ResilientFetcher(use_cache=True)
    report = []
    all_news = {}
    
    report.append("=" * 60)
    report.append("🦊 Fox每日新闻日报 v4.0")
    report.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 60)
    report.append("")
    
    # ==================== 获取所有新闻 ====================
    print("\n📡 开始获取新闻数据...")
    
    # 60秒读懂世界
    print("  获取60秒读懂世界...")
    daily_items = fetcher.fetch_group('daily')
    all_news['daily'] = daily_items
    
    # 微博热搜
    print("  获取微博热搜...")
    weibo_items = fetcher.fetch_group('weibo')
    all_news['weibo'] = weibo_items
    
    # 知乎热榜
    print("  获取知乎热榜...")
    zhihu_items = fetcher.fetch_group('zhihu')
    all_news['zhihu'] = zhihu_items
    
    # B站热搜
    print("  获取B站热搜...")
    bili_items = fetcher.fetch_group('bilibili')
    all_news['bilibili'] = bili_items
    
    # 抖音热点
    print("  获取抖音热点...")
    douyin_items = fetcher.fetch_group('douyin')
    all_news['douyin'] = douyin_items
    
    # 今日头条
    print("  获取今日头条...")
    toutiao_items = fetcher.fetch_group('toutiao')
    all_news['toutiao'] = toutiao_items
    
    # 豆瓣电影
    print("  获取豆瓣电影...")
    douban_items = fetcher.fetch_group('douban')
    all_news['douban'] = douban_items
    
    # V2EX
    print("  获取V2EX...")
    v2ex_items = fetcher.fetch_group('v2ex')
    all_news['v2ex'] = v2ex_items
    
    # 澎湃新闻
    print("  获取澎湃新闻...")
    thepaper_items = fetcher.fetch_group('thepaper')
    all_news['thepaper'] = thepaper_items
    
    # Epic免费游戏
    print("  获取Epic免费游戏...")
    epic_items = fetcher.fetch_group('epic')
    all_news['epic'] = epic_items
    
    # RSS数据源
    rss_total = 0
    if RSS_AVAILABLE:
        print("  获取RSS数据源...")
        rss_data = aggregate_all_rss(use_cache=True)
        for group_id, items in rss_data.items():
            if items:
                all_news[group_id] = items
                rss_total += len(items)
    
    # ==================== 运行分析引擎 ====================
    print("\n🧠 运行分析引擎...")
    analysis = run_analysis(all_news)
    
    # 加载昨日数据并对比
    print("📊 对比历史数据...")
    yesterday_data = load_yesterday_data()
    comparison = compare_with_yesterday(all_news, yesterday_data)
    
    # 保存今日数据
    save_today_data(all_news, analysis)
    
    # ==================== 生成智能摘要 ====================
    smart_summary = format_smart_summary(analysis, comparison)
    report.extend(smart_summary)
    
    # ==================== 常规新闻内容 ====================
    if daily_items:
        report.append("【60秒读懂世界】")
        report.append("")
        for i, item in enumerate(daily_items, 1):
            report.append(f"{i}. {item.title}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
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
    
    if zhihu_items:
        report.append("【知乎热榜 Top 10】")
        report.append("")
        for i, item in enumerate(zhihu_items[:10], 1):
            report.append(f"{i}. {item.title}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    if bili_items:
        report.append("【B站热搜 Top 10】")
        report.append("")
        for i, item in enumerate(bili_items[:10], 1):
            report.append(f"{i}. {item.title}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    if douyin_items:
        report.append("【抖音热点 Top 10】")
        report.append("")
        for i, item in enumerate(douyin_items[:10], 1):
            report.append(f"{i}. {item.title}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    if toutiao_items:
        report.append("【今日头条 Top 10】")
        report.append("")
        for i, item in enumerate(toutiao_items[:10], 1):
            report.append(f"{i}. {item.title}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
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
    
    if v2ex_items:
        report.append("【V2EX热帖】")
        report.append("")
        for i, item in enumerate(v2ex_items[:10], 1):
            report.append(f"{i}. {item.title[:50]}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    if thepaper_items:
        report.append("【澎湃新闻热榜】")
        report.append("")
        for i, item in enumerate(thepaper_items[:10], 1):
            report.append(f"{i}. {item.title[:50]}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
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
    
    # ==================== 投资匹配 ====================
    print("💰 运行投资匹配...")
    portfolio_results = match_portfolio(news_list, portfolio_config)
    
    # 生成投资影响摘要
    impact_summary = []
    for impact in impacts:
        sources = []
        for impact in impacts:
            sources.append(group_id)
    
    return "\n".join(impact_summary)

def format_investment_summary(impacts: List[Dict]) -> str:
    """格式化投资影响摘要"""
    summary = ["【投资相关】",    summary.append("📊 根据投资偏好匹配到的新闻：")
    
    # 按影响程度排序
    impacts.sort(
        key=lambda x: (x.get("impact_level", ""),
        reverse=True
    )
    
    return "\n".join(summary)    
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
    report.append(f"🦊 由 Fox v4.0 自动生成 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 60)
    
    # 导出JSON
    export_json(all_news, analysis)
    
    return "\n".join(report)


def main():
    report = generate_daily_news_v4()
    
    # 保存TXT
    output_path = Path(__file__).parent / "daily_news_report.txt"
    with open(output_path, "w") as f:
        f.write(report)
    
    print(f"\n✅ 日报已保存到: {output_path}")
    print(f"\n{health_tracker.get_report()}")


if __name__ == "__main__":
    main()
