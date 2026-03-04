#!/usr/bin/env python3
"""
告警检测模块
自动识别新闻中的告警关键词

学习自: situation-monitor/src/lib/config/keywords.ts
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AlertMatch:
    """告警匹配结果"""
    keyword: str
    category: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    position: int  # 在文本中的位置


# =============================================================================
# 告警关键词配置
# =============================================================================

ALERT_KEYWORDS = {
    # 严重告警（战争、军事冲突）
    "critical": [
        "核战争", "nuclear war", "核武器", "nuclear weapon",
        "宣战", "declare war", "入侵", "invasion",
        "军事政变", "military coup", "内战", "civil war",
    ],
    
    # 高级告警（重大事件）
    "high": [
        "战争", "war", "军事行动", "military operation",
        "导弹", "missile", "空袭", "airstrike", "轰炸", "bombing",
        "恐怖袭击", "terrorist attack", "爆炸", "explosion",
        "人质", "hostage", "撤侨", "evacuation",
        "制裁", "sanctions", "禁运", "embargo",
        "紧急状态", "emergency", "戒严", "martial law",
    ],
    
    # 中级告警（值得关注）
    "medium": [
        "军队", "troops", "军事", "military",
        "冲突", "conflict", "对峙", "standoff",
        "边境", "border", "演习", "exercise",
        "外交官", "diplomat", "大使馆", "embassy",
        "条约", "treaty", "谈判", "negotiation",
        "停火", "ceasefire", "和谈", "peace talk",
        "暗杀", "assassination", "刺杀", "assassinated",
    ],
    
    # 低级告警（一般关注）
    "low": [
        "国防", "defense", "安全", "security",
        "威胁", "threat", "警告", "warning",
        "紧张", "tension", "危机", "crisis",
        "北约", "NATO", "联合国", "UN",
        "情报", "intelligence", "间谍", "spy",
    ],
}

# 严重程度权重
SEVERITY_WEIGHTS = {
    "critical": 100,
    "high": 50,
    "medium": 20,
    "low": 10,
}

# 区域关键词
REGION_KEYWORDS = {
    "东亚": ["中国", "China", "日本", "Japan", "韩国", "Korea", "台湾", "Taiwan", "朝鲜", "North Korea"],
    "中东": ["中东", "Middle East", "伊朗", "Iran", "以色列", "Israel", "沙特", "Saudi", "叙利亚", "Syria"],
    "欧洲": ["欧洲", "Europe", "欧盟", "EU", "北约", "NATO", "乌克兰", "Ukraine", "俄罗斯", "Russia"],
    "美洲": ["美国", "US", "USA", "美洲", "America", "拉美", "Latin America"],
    "非洲": ["非洲", "Africa"],
    "南亚": ["印度", "India", "巴基斯坦", "Pakistan", "阿富汗", "Afghanistan"],
}


def contains_alert_keyword(text: str) -> Optional[AlertMatch]:
    """
    检查文本是否包含告警关键词
    
    Args:
        text: 要检查的文本
    
    Returns:
        第一个匹配的AlertMatch，如果没有则返回None
    """
    text_lower = text.lower()
    
    # 按严重程度检查
    for severity, keywords in ALERT_KEYWORDS.items():
        for keyword in keywords:
            # 不区分大小写搜索
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            match = pattern.search(text)
            if match:
                return AlertMatch(
                    keyword=keyword,
                    category="alert",
                    severity=severity,
                    position=match.start(),
                )
    
    return None


def find_all_alerts(text: str) -> List[AlertMatch]:
    """
    找出文本中所有告警关键词
    
    Args:
        text: 要检查的文本
    
    Returns:
        所有匹配的AlertMatch列表
    """
    matches = []
    text_lower = text.lower()
    found_keywords = set()
    
    for severity, keywords in ALERT_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in found_keywords:
                continue
            
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            match = pattern.search(text)
            if match:
                found_keywords.add(keyword.lower())
                matches.append(AlertMatch(
                    keyword=keyword,
                    category="alert",
                    severity=severity,
                    position=match.start(),
                ))
    
    return sorted(matches, key=lambda x: SEVERITY_WEIGHTS.get(x.severity, 0), reverse=True)


def calculate_alert_score(text: str) -> int:
    """
    计算文本的告警分数
    
    Args:
        text: 要计算的文本
    
    Returns:
        告警分数（越高越严重）
    """
    matches = find_all_alerts(text)
    score = sum(SEVERITY_WEIGHTS.get(m.severity, 0) for m in matches)
    return score


def detect_region(text: str) -> Optional[str]:
    """
    检测文本中的区域
    
    Args:
        text: 要检查的文本
    
    Returns:
        检测到的区域名称，如果没有则返回None
    """
    text_lower = text.lower()
    
    for region, keywords in REGION_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return region
    
    return None


def classify_news_alert(news_item: Dict) -> Dict:
    """
    分类新闻的告警级别
    
    Args:
        news_item: 新闻项（需要有title字段）
    
    Returns:
        包含告警信息的字典
    """
    title = news_item.get("title", "")
    
    alert = contains_alert_keyword(title)
    all_alerts = find_all_alerts(title)
    score = calculate_alert_score(title)
    region = detect_region(title)
    
    return {
        "is_alert": alert is not None,
        "alert_keyword": alert.keyword if alert else None,
        "alert_severity": alert.severity if alert else None,
        "alert_score": score,
        "all_alerts": [{"keyword": m.keyword, "severity": m.severity} for m in all_alerts],
        "region": region,
    }


def filter_alert_news(news_list: List[Dict], min_severity: str = "medium") -> List[Dict]:
    """
    筛选出包含告警的新闻
    
    Args:
        news_list: 新闻列表
        min_severity: 最低严重程度
    
    Returns:
        包含告警的新闻列表
    """
    severity_order = ["low", "medium", "high", "critical"]
    min_index = severity_order.index(min_severity) if min_severity in severity_order else 0
    
    alert_news = []
    for news in news_list:
        classification = classify_news_alert(news)
        if classification["is_alert"]:
            severity = classification["alert_severity"]
            severity_index = severity_order.index(severity) if severity in severity_order else 0
            if severity_index >= min_index:
                news["alert_info"] = classification
                alert_news.append(news)
    
    # 按严重程度排序
    alert_news.sort(
        key=lambda x: SEVERITY_WEIGHTS.get(x.get("alert_info", {}).get("alert_severity", "low"), 0),
        reverse=True,
    )
    
    return alert_news


def format_alert_summary(news_list: List[Dict], max_items: int = 10) -> str:
    """
    格式化告警摘要
    
    Args:
        news_list: 新闻列表
        max_items: 最大显示数量
    
    Returns:
        格式化的告警摘要文本
    """
    alert_news = filter_alert_news(news_list, min_severity="medium")
    
    if not alert_news:
        return ""
    
    lines = ["【⚠️ 告警新闻】"]
    
    for i, news in enumerate(alert_news[:max_items], 1):
        alert_info = news.get("alert_info", {})
        severity = alert_info.get("alert_severity", "medium")
        keyword = alert_info.get("alert_keyword", "")
        
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "⚪",
        }
        emoji = severity_emoji.get(severity, "⚪")
        
        title = news.get("title", "")[:60]
        lines.append(f"{emoji} [{keyword}] {title}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    print("=== 告警检测测试 ===\n")
    
    test_news = [
        {"title": "俄军对乌克兰发动大规模导弹袭击，基辅拉响防空警报"},
        {"title": "美联储宣布加息25个基点，市场反应平淡"},
        {"title": "中东局势紧张，伊朗警告将采取军事行动"},
        {"title": "某科技公司发布新款手机，售价创新高"},
        {"title": "联合国安理会召开紧急会议讨论核武器问题"},
        {"title": "北约宣布在东欧举行大规模军事演习"},
    ]
    
    print(format_alert_summary(test_news))
    
    print("\n" + "="*40)
    print("\n单条新闻分析:")
    test_title = "俄军对乌克兰发动大规模导弹袭击，基辅拉响防空警报"
    classification = classify_news_alert({"title": test_title})
    print(f"标题: {test_title}")
    print(f"告警分数: {classification['alert_score']}")
    print(f"严重程度: {classification['alert_severity']}")
    print(f"所有告警: {classification['all_alerts']}")
    print(f"区域: {classification['region']}")
