#!/usr/bin/env python3
"""
关联分析引擎
跨新闻源检测主题热度，识别"正在发酵"的新闻

学习自: situation-monitor/src/lib/analysis/correlation.ts
"""

import re
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class EmergingPattern:
    """新兴模式 - 出现次数较多的主题"""
    id: str
    name: str
    category: str
    count: int
    level: str  # 'high', 'elevated', 'emerging'
    sources: List[str]
    headlines: List[Dict]


@dataclass
class MomentumSignal:
    """动量信号 - 快速上升的主题"""
    id: str
    name: str
    category: str
    current: int
    delta: int  # 与上次相比的变化
    momentum: str  # 'surging', 'rising', 'stable'
    headlines: List[Dict]


@dataclass
class CrossSourceCorrelation:
    """跨源关联 - 多个来源报道同一主题"""
    id: str
    name: str
    category: str
    source_count: int
    sources: List[str]
    level: str
    headlines: List[Dict]


@dataclass
class CorrelationResults:
    """关联分析结果"""
    emerging_patterns: List[EmergingPattern] = field(default_factory=list)
    momentum_signals: List[MomentumSignal] = field(default_factory=list)
    cross_source_correlations: List[CrossSourceCorrelation] = field(default_factory=list)


# =============================================================================
# 预定义的关联主题（正则匹配）
# =============================================================================

CORRELATION_TOPICS = [
    # 经济
    {"id": "tariffs", "patterns": [r"关税|tariff|贸易战|trade war"], "category": "经济"},
    {"id": "fed-rates", "patterns": [r"美联储|Federal Reserve|利率|interest rate|降息|加息"], "category": "经济"},
    {"id": "inflation", "patterns": [r"通胀|inflation|CPI|物价"], "category": "经济"},
    {"id": "layoffs", "patterns": [r"裁员|layoff|失业|job cut"], "category": "经济"},
    {"id": "housing", "patterns": [r"房价|housing|房地产|real estate"], "category": "经济"},
    
    # 地缘政治
    {"id": "china-us", "patterns": [r"中美|中美关系|China US|Beijing Washington"], "category": "地缘"},
    {"id": "china-taiwan", "patterns": [r"台湾|Taiwan|台海"], "category": "地缘"},
    {"id": "russia-ukraine", "patterns": [r"乌克兰|Ukraine|俄乌|泽连斯基|Zelensky|普京|Putin"], "category": "冲突"},
    {"id": "israel-gaza", "patterns": [r"加沙|Gaza|以色列|Israel|哈马斯|Hamas"], "category": "冲突"},
    {"id": "iran", "patterns": [r"伊朗|Iran|德黑兰|Tehran"], "category": "地缘"},
    {"id": "north-korea", "patterns": [r"朝鲜|North Korea|金正恩"], "category": "地缘"},
    
    # 科技
    {"id": "ai-regulation", "patterns": [r"AI监管|AI regulation|人工智能.*法律|AI.*安全"], "category": "科技"},
    {"id": "chatgpt", "patterns": [r"ChatGPT|GPT|OpenAI|大模型|LLM"], "category": "科技"},
    {"id": "autonomous", "patterns": [r"自动驾驶|autonomous|无人驾驶|self-driving"], "category": "科技"},
    {"id": "chip", "patterns": [r"芯片|chip|半导体|semiconductor|英伟达|Nvidia"], "category": "科技"},
    
    # 金融
    {"id": "crypto", "patterns": [r"比特币|Bitcoin|加密货币|crypto|以太坊|Ethereum"], "category": "金融"},
    {"id": "stock-market", "patterns": [r"股市|stock market|A股|港股|美股|道琼斯|纳指"], "category": "金融"},
    
    # 健康
    {"id": "pandemic", "patterns": [r"疫情|pandemic|病毒|virus|流感|flu"], "category": "健康"},
    
    # 能源
    {"id": "oil", "patterns": [r"油价|oil price|原油|crude|OPEC"], "category": "能源"},
    {"id": "ev", "patterns": [r"电动车|EV|electric vehicle|新能源车|特斯拉|Tesla|比亚迪"], "category": "能源"},
]


# =============================================================================
# 历史记录（用于动量分析）
# =============================================================================

# 存储每个时间段的主题计数
# 结构: {minute_timestamp: {topic_id: count}}
_topic_history: Dict[int, Dict[str, int]] = {}

# 历史保留时间（分钟）
HISTORY_RETENTION_MINUTES = 30

# 动量比较窗口（分钟）
MOMENTUM_WINDOW_MINUTES = 10


def _format_topic_name(topic_id: str) -> str:
    """格式化主题ID为显示名称"""
    return topic_id.replace("-", " ").title()


def _get_current_minute() -> int:
    """获取当前分钟时间戳"""
    return int(time.time() // 60)


def _clean_old_history():
    """清理过期历史"""
    current = _get_current_minute()
    for minute in list(_topic_history.keys()):
        if current - minute > HISTORY_RETENTION_MINUTES:
            del _topic_history[minute]


def analyze_correlations(all_news: List[Dict]) -> Optional[CorrelationResults]:
    """
    分析所有新闻的关联性
    
    Args:
        all_news: 新闻列表，每条新闻需要有 title, source 字段
    
    Returns:
        CorrelationResults 或 None
    """
    if not all_news:
        return None
    
    current_minute = _get_current_minute()
    results = CorrelationResults()
    
    # 统计主题出现次数
    topic_counts: Dict[str, int] = defaultdict(int)
    topic_sources: Dict[str, set] = defaultdict(set)
    topic_headlines: Dict[str, List[Dict]] = defaultdict(list)
    
    # 分析每条新闻
    for item in all_news:
        title = item.get("title", "")
        source = item.get("source", "Unknown")
        link = item.get("url", item.get("link", ""))
        
        for topic in CORRELATION_TOPICS:
            topic_id = topic["id"]
            patterns = topic["patterns"]
            category = topic["category"]
            
            # 检查是否匹配任一模式
            matched = False
            for pattern in patterns:
                if re.search(pattern, title, re.IGNORECASE):
                    matched = True
                    break
            
            if matched:
                topic_counts[topic_id] += 1
                topic_sources[topic_id].add(source)
                
                if len(topic_headlines[topic_id]) < 5:
                    topic_headlines[topic_id].append({
                        "title": title,
                        "source": source,
                        "link": link,
                    })
    
    # 更新历史记录
    _topic_history[current_minute] = dict(topic_counts)
    _clean_old_history()
    
    # 获取旧计数（用于动量比较）
    old_minute = current_minute - MOMENTUM_WINDOW_MINUTES
    old_counts = _topic_history.get(old_minute, {})
    
    # 处理每个主题
    for topic in CORRELATION_TOPICS:
        topic_id = topic["id"]
        category = topic["category"]
        
        count = topic_counts.get(topic_id, 0)
        sources = list(topic_sources.get(topic_id, set()))
        headlines = topic_headlines.get(topic_id, [])
        old_count = old_counts.get(topic_id, 0)
        delta = count - old_count
        
        # 1. 新兴模式（3次以上提及）
        if count >= 3:
            if count >= 8:
                level = "high"
            elif count >= 5:
                level = "elevated"
            else:
                level = "emerging"
            
            results.emerging_patterns.append(EmergingPattern(
                id=topic_id,
                name=_format_topic_name(topic_id),
                category=category,
                count=count,
                level=level,
                sources=sources,
                headlines=headlines,
            ))
        
        # 2. 动量信号（快速上升）
        if delta >= 2 or (count >= 3 and delta >= 1):
            if delta >= 4:
                momentum = "surging"
            elif delta >= 2:
                momentum = "rising"
            else:
                momentum = "stable"
            
            results.momentum_signals.append(MomentumSignal(
                id=topic_id,
                name=_format_topic_name(topic_id),
                category=category,
                current=count,
                delta=delta,
                momentum=momentum,
                headlines=headlines,
            ))
        
        # 3. 跨源关联（3个以上来源）
        if len(sources) >= 3:
            if len(sources) >= 5:
                level = "high"
            elif len(sources) >= 4:
                level = "elevated"
            else:
                level = "emerging"
            
            results.cross_source_correlations.append(CrossSourceCorrelation(
                id=topic_id,
                name=_format_topic_name(topic_id),
                category=category,
                source_count=len(sources),
                sources=sources,
                level=level,
                headlines=headlines,
            ))
    
    # 排序
    results.emerging_patterns.sort(key=lambda x: x.count, reverse=True)
    results.momentum_signals.sort(key=lambda x: x.delta, reverse=True)
    results.cross_source_correlations.sort(key=lambda x: x.source_count, reverse=True)
    
    return results


def get_correlation_summary(results: CorrelationResults) -> Dict:
    """获取关联分析摘要"""
    if not results:
        return {"total_signals": 0, "status": "NO DATA"}
    
    total = (
        len(results.emerging_patterns) +
        len(results.momentum_signals) +
        len(results.cross_source_correlations)
    )
    
    return {
        "total_signals": total,
        "emerging": len(results.emerging_patterns),
        "momentum": len(results.momentum_signals),
        "cross_source": len(results.cross_source_correlations),
        "status": f"{total} SIGNALS" if total > 0 else "MONITORING",
    }


def clear_correlation_history():
    """清除历史记录"""
    global _topic_history
    _topic_history = {}


def format_correlation_report(results: CorrelationResults, max_items: int = 5) -> str:
    """格式化关联分析报告"""
    lines = []
    
    if results.emerging_patterns:
        lines.append("【🔥 热门话题】")
        for p in results.emerging_patterns[:max_items]:
            level_emoji = {"high": "🔴", "elevated": "🟠", "emerging": "🟡"}
            emoji = level_emoji.get(p.level, "⚪")
            lines.append(f"{emoji} {p.name} ({p.count}次, {len(p.sources)}源)")
        lines.append("")
    
    if results.momentum_signals:
        lines.append("【📈 快速上升】")
        for s in results.momentum_signals[:max_items]:
            momentum_emoji = {"surging": "🚀", "rising": "📈", "stable": "➡️"}
            emoji = momentum_emoji.get(s.momentum, "➡️")
            lines.append(f"{emoji} {s.name} (+{s.delta})")
        lines.append("")
    
    if results.cross_source_correlations:
        lines.append("【🌐 跨源验证】")
        for c in results.cross_source_correlations[:max_items]:
            lines.append(f"✓ {c.name} ({c.source_count}个来源)")
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    print("=== 关联分析引擎测试 ===\n")
    
    test_news = [
        {"title": "美联储宣布降息25个基点", "source": "Reuters"},
        {"title": "美联储利率决议：维持不变", "source": "Bloomberg"},
        {"title": "通胀数据超预期，美联储或推迟降息", "source": "CNBC"},
        {"title": "乌克兰局势升级，俄军发动新攻势", "source": "BBC"},
        {"title": "俄乌冲突最新：泽连斯基访美", "source": "CNN"},
        {"title": "ChatGPT-5即将发布，OpenAI高管透露细节", "source": "TechCrunch"},
        {"title": "中国芯片产业取得重大突破", "source": "新华社"},
        {"title": "英伟达发布新一代AI芯片", "source": "Ars Technica"},
        {"title": "特斯拉股价大跌，马斯克财富缩水", "source": "Yahoo Finance"},
        {"title": "电动车市场竞争加剧，比亚迪销量创新高", "source": "财新"},
        {"title": "油价飙升，OPEC维持减产决定", "source": "Reuters"},
    ]
    
    results = analyze_correlations(test_news)
    
    if results:
        print(format_correlation_report(results))
        print("\n" + "="*40)
        print(f"摘要: {get_correlation_summary(results)}")
