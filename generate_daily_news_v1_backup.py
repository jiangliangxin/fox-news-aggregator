#!/usr/bin/env python3
"""
Fox每日新闻日报 - 使用新闻聚合器
整合60s API + OpenClaw-Feeds RSS + NewsNow数据源
改进版：添加国内新闻、AI板块、优化来源显示
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

# 添加新闻聚合器路径
sys.path.insert(0, str(Path(__file__).parent / "news-aggregator"))

from fetcher import aggregate_all

def extract_source_from_url(url: str) -> str:
    """从URL提取来源域名"""
    try:
        domain = urlparse(url).netloc
        # 移除www前缀
        domain = re.sub(r'^www\.', '', domain)
        # 简化常见域名
        domain_map = {
            'arstechnica.com': 'Ars Technica',
            'wired.com': 'Wired',
            'techcrunch.com': 'TechCrunch',
            'theverge.com': 'The Verge',
            'slashdot.org': 'Slashdot',
            'hnrss.org': 'Hacker News',
            'reddit.com': 'Reddit',
            '36kr.com': '36氪',
            'ithome.com': 'IT之家',
            'sspai.com': '少数派',
            'infoq.cn': 'InfoQ',
            'bloomberg.com': 'Bloomberg',
            'ft.com': '金融时报',
            'cnbc.com': 'CNBC',
        }
        return domain_map.get(domain, domain)
    except:
        return 'Unknown'

def is_ai_related(title: str) -> bool:
    """判断标题是否与AI相关"""
    ai_keywords = [
        'ai', 'artificial intelligence', 'machine learning', 'deep learning',
        'neural network', 'gpt', 'chatgpt', 'claude', 'gemini', 'llm',
        'openai', 'anthropic', '人工智能', '机器学习', '深度学习',
        '神经网络', '大模型', '自动驾驶', 'autonomous',
        'ml', 'nlp', 'computer vision', '机器人', 'robot'
    ]
    title_lower = title.lower()
    return any(kw in title_lower for kw in ai_keywords)

def generate_daily_news():
    """生成每日新闻日报"""
    
    print("=" * 60)
    print("🦊 Fox每日新闻日报")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取所有新闻数据
    print("\n正在聚合新闻数据...")
    data = aggregate_all(use_cache=True)
    
    # 开始生成日报
    report = []
    report.append("=" * 60)
    report.append("🦊 Fox每日新闻日报")
    report.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 60)
    report.append("")
    
    # ==================== 国内热点 ====================
    
    # 1. 每天60秒读懂世界
    if '60s_daily' in data['api']:
        daily = data['api']['60s_daily']['data']
        report.append("【国内要闻 - 每天60秒】")
        report.append(f"📅 {daily['date']} {daily['day_of_week']} {daily['lunar_date']}")
        report.append("")
        
        for i, news in enumerate(daily['news'], 1):
            report.append(f"{i}. {news}")
        
        report.append("")
        report.append(f"💡 每日微语：{daily['tip']}")
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # 2. 澎湃新闻（国内新闻）
    if 'thepaper' in data.get('newsnow', {}):
        thepaper = data['newsnow']['thepaper'].get('items', [])
        if thepaper:
            report.append("【澎湃新闻 - 国内新闻】")
            report.append("")
            
            for i, item in enumerate(thepaper[:10], 1):
                report.append(f"{i}. {item['title']}")
            
            report.append("")
            report.append("-" * 60)
            report.append("")
    
    # 3. 微博热搜
    if 'weibo_hot' in data['api']:
        weibo = data['api']['weibo_hot']['data']
        report.append("【微博热搜 Top 10】")
        report.append("")
        
        for i, item in enumerate(weibo[:10], 1):
            hot_value = item.get('hot_value', 0)
            hot_str = f"{hot_value // 10000}万" if hot_value >= 10000 else str(hot_value)
            report.append(f"{i}. {item['title']} (🔥{hot_str})")
        
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # 4. 知乎热榜
    if 'zhihu_hot' in data['api']:
        zhihu = data['api']['zhihu_hot']['data']
        report.append("【知乎热榜 Top 10】")
        report.append("")
        
        for i, item in enumerate(zhihu[:10], 1):
            title = item['title'][:80]
            report.append(f"{i}. {title}")
        
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # 5. 抖音热点
    if 'douyin_hot' in data['api']:
        douyin = data['api']['douyin_hot']['data']
        report.append("【抖音热点 Top 10】")
        report.append("")
        
        for i, item in enumerate(douyin[:10], 1):
            report.append(f"{i}. {item['title']}")
        
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # 6. 今日头条
    if 'toutiao_hot' in data['api']:
        toutiao = data['api']['toutiao_hot']['data']
        report.append("【今日头条 Top 10】")
        report.append("")
        
        for i, item in enumerate(toutiao[:10], 1):
            report.append(f"{i}. {item['title']}")
        
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # ==================== 科技新闻 ====================
    
    # 7. IT之家
    if 'ithome' in data.get('newsnow', {}):
        ithome = data['newsnow']['ithome'].get('items', [])
        if ithome:
            report.append("【IT之家科技资讯】")
            report.append("")
            
            for i, item in enumerate(ithome[:10], 1):
                title = item['title'][:70]
                report.append(f"{i}. {title}")
            
            report.append("")
            report.append("-" * 60)
            report.append("")
    
    # 8. AI新闻（专门板块）
    ai_news = []
    
    # 从RSS国际科技中提取AI相关
    if 'tech_intl' in data.get('rss', {}):
        for item in data['rss']['tech_intl'].get('entries', []):
            if is_ai_related(item['title']):
                source = extract_source_from_url(item['url'])
                ai_news.append({
                    'title': item['title'],
                    'source': source,
                    'url': item['url']
                })
    
    # 从IT之家中提取AI相关
    if 'ithome' in data.get('newsnow', {}):
        for item in data['newsnow']['ithome'].get('items', []):
            if is_ai_related(item['title']):
                ai_news.append({
                    'title': item['title'],
                    'source': 'IT之家',
                    'url': item.get('url', '')
                })
    
    # 去重
    seen_titles = set()
    unique_ai_news = []
    for item in ai_news:
        if item['title'] not in seen_titles:
            seen_titles.add(item['title'])
            unique_ai_news.append(item)
    
    if unique_ai_news:
        report.append("【AI人工智能】")
        report.append("")
        
        for i, item in enumerate(unique_ai_news[:10], 1):
            title = item['title'][:70]
            source = item['source']
            report.append(f"{i}. [{source}] {title}")
        
        report.append("")
        report.append("-" * 60)
        report.append("")
    
    # 9. 国际科技新闻（来自RSS，优化来源显示）
    if 'tech_intl' in data.get('rss', {}):
        tech = data['rss']['tech_intl'].get('entries', [])
        if tech:
            report.append("【国际科技】")
            report.append("")
            
            for i, item in enumerate(tech[:10], 1):
                title = item['title'][:70]
                source = extract_source_from_url(item['url'])
                report.append(f"{i}. [{source}] {title}")
            
            report.append("")
            report.append("-" * 60)
            report.append("")
    
    # 10. GitHub Trending
    if 'github' in data.get('newsnow', {}):
        github = data['newsnow']['github'].get('items', [])
        if github:
            report.append("【GitHub Trending】")
            report.append("")
            
            for i, item in enumerate(github[:5], 1):
                report.append(f"{i}. {item['title']}")
                if item.get('extra'):
                    desc = item['extra'][:80]
                    report.append(f"   {desc}...")
            
            report.append("")
            report.append("-" * 60)
            report.append("")
    
    # 11. Hacker News
    if 'hackernews' in data.get('newsnow', {}):
        hn = data['newsnow']['hackernews'].get('items', [])
        if hn:
            report.append("【Hacker News】")
            report.append("")
            
            for i, item in enumerate(hn[:5], 1):
                title = item['title'][:70]
                report.append(f"{i}. {title}")
            
            report.append("")
            report.append("-" * 60)
            report.append("")
    
    # ==================== 财经新闻 ====================
    
    # 12. 财经（来自RSS）
    if 'finance' in data.get('rss', {}):
        finance = data['rss']['finance'].get('entries', [])
        if finance:
            report.append("【财经要闻】")
            report.append("")
            
            for i, item in enumerate(finance[:8], 1):
                title = item['title'][:70]
                source = extract_source_from_url(item['url'])
                report.append(f"{i}. [{source}] {title}")
            
            report.append("")
            report.append("-" * 60)
            report.append("")
    
    # ==================== 娱乐 ====================
    
    # 13. 豆瓣热门电影
    if 'douban' in data.get('newsnow', {}):
        douban = data['newsnow']['douban'].get('items', [])
        if douban:
            report.append("【豆瓣热门电影】")
            report.append("")
            
            for i, item in enumerate(douban[:5], 1):
                title = item['title']
                rating = item.get('extra', '')
                if rating:
                    report.append(f"{i}. {title} ({rating})")
                else:
                    report.append(f"{i}. {title}")
            
            report.append("")
            report.append("-" * 60)
            report.append("")
    
    # 14. Epic免费游戏
    if 'epic_free' in data['api']:
        epic = data['api']['epic_free']['data']
        report.append("【Epic免费游戏】")
        report.append("")
        
        for item in epic:
            report.append(f"🎮 {item['title']}")
            report.append(f"   原价: {item['original_price_desc']}")
            report.append(f"   截止: {item['free_end']}")
            report.append("")
        
        report.append("-" * 60)
        report.append("")
    
    # ==================== 统计信息 ====================
    
    report.append("【统计信息】")
    report.append("")
    report.append(f"📊 数据源: {data['meta']['api_sources_count']} API + {data['meta']['rss_categories_count']} RSS分类 + {data['meta']['newsnow_sources_count']} NewsNow")
    report.append(f"📰 总新闻数: {data['meta']['total_items']}条")
    report.append(f"⏱️  耗时: {data['meta']['elapsed_seconds']}秒")
    report.append(f"💾 缓存: {'启用' if data['meta']['use_cache'] else '禁用'}")
    report.append("")
    report.append("=" * 60)
    report.append(f"🦊 由 Fox 自动生成 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 60)
    
    # 返回日报文本
    return "\n".join(report)


def main():
    """主函数"""
    try:
        report = generate_daily_news()
        print("\n" + report)
        
        # 保存到文件
        output_file = Path(__file__).parent / "daily_news_report.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 日报已保存到: {output_file}")
        
    except Exception as e:
        print(f"\n❌ 生成日报失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
