#!/usr/bin/env python3
"""
实体追踪模块
追踪新闻中人物、组织的出现频率

学习自: situation-monitor/src/lib/analysis/main-character.ts
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class EntityMention:
    """实体提及"""
    name: str
    count: int
    sources: List[str]
    headlines: List[Dict]
    category: str  # 'person', 'organization', 'country'


# =============================================================================
# 预定义实体（人物）
# =============================================================================

PERSON_PATTERNS = [
    # 中国
    (r"习近平", "习近平"),
    (r"李强", "李强"),
    (r"王毅", "王毅"),
    
    # 美国
    (r"Trump|特朗普", "特朗普"),
    (r"Biden|拜登", "拜登"),
    (r"Musk|马斯克", "马斯克"),
    (r"Zuckerberg|扎克伯格", "扎克伯格"),
    (r"Bezos|贝索斯", "贝索斯"),
    (r"Altman|奥特曼", "Sam Altman"),
    (r"Huang|黄仁勋", "黄仁勋"),
    (r"Powell|鲍威尔", "鲍威尔"),
    (r"Yellen|耶伦", "耶伦"),
    (r"Harris|哈里斯", "哈里斯"),
    
    # 俄罗斯/乌克兰
    (r"Putin|普京", "普京"),
    (r"Zelensky|泽连斯基", "泽连斯基"),
    
    # 中东
    (r"Netanyahu|内塔尼亚胡", "内塔尼亚胡"),
    
    # 科技大佬
    (r"Tim Cook|库克", "库克"),
    (r"Nadella|纳德拉", "纳德拉"),
    (r"Pichai|皮查伊", "皮查伊"),
    (r" Buffett|巴菲特", "巴菲特"),
]

# =============================================================================
# 预定义实体（组织）
# =============================================================================

ORG_PATTERNS = [
    # 科技公司
    (r"OpenAI", "OpenAI"),
    (r"Google|谷歌", "Google"),
    (r"Apple|苹果", "Apple"),
    (r"Microsoft|微软", "Microsoft"),
    (r"Meta|Facebook", "Meta"),
    (r"Amazon|亚马逊", "Amazon"),
    (r"Nvidia|英伟达", "Nvidia"),
    (r"Tesla|特斯拉", "Tesla"),
    (r"ByteDance|字节跳动", "字节跳动"),
    (r"Tencent|腾讯", "腾讯"),
    (r"Alibaba|阿里巴巴", "阿里巴巴"),
    (r"Huawei|华为", "华为"),
    (r"Anthropic", "Anthropic"),
    
    # 金融机构
    (r"Federal Reserve|美联储", "美联储"),
    (r"SEC", "SEC"),
    (r"IMF", "IMF"),
    (r"World Bank|世界银行", "世界银行"),
    
    # 国际组织
    (r"UN|联合国", "联合国"),
    (r"NATO|北约", "北约"),
    (r"WTO|世贸组织", "WTO"),
    (r"WHO|世卫组织", "WHO"),
    (r"OPEC", "OPEC"),
]

# =============================================================================
# 预定义实体（国家/地区）
# =============================================================================

COUNTRY_PATTERNS = [
    (r"中国|China|北京|Beijing", "中国"),
    (r"美国|US|USA|美国|Washington|华盛顿", "美国"),
    (r"俄罗斯|Russia|莫斯科|Moscow", "俄罗斯"),
    (r"乌克兰|Ukraine|基辅|Kyiv", "乌克兰"),
    (r"台湾|Taiwan|台北|Taipei", "台湾"),
    (r"日本|Japan|东京|Tokyo", "日本"),
    (r"韩国|Korea|首尔|Seoul", "韩国"),
    (r"朝鲜|North Korea|平壤", "朝鲜"),
    (r"伊朗|Iran|德黑兰|Tehran", "伊朗"),
    (r"以色列|Israel|耶路撒冷|Jerusalem", "以色列"),
    (r"印度|India|新德里|New Delhi", "印度"),
    (r"德国|Germany|柏林|Berlin", "德国"),
    (r"英国|UK|Britain|伦敦|London", "英国"),
    (r"法国|France|巴黎|Paris", "法国"),
]


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    从文本中提取实体
    
    Args:
        text: 要分析的文本
    
    Returns:
        {"persons": [...], "orgs": [...], "countries": [...]}
    """
    persons = []
    orgs = []
    countries = []
    
    # 提取人物
    for pattern, name in PERSON_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            persons.append(name)
    
    # 提取组织
    for pattern, name in ORG_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            orgs.append(name)
    
    # 提取国家
    for pattern, name in COUNTRY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            countries.append(name)
    
    return {
        "persons": list(set(persons)),
        "orgs": list(set(orgs)),
        "countries": list(set(countries)),
    }


def analyze_entities(news_list: List[Dict], top_n: int = 10) -> Dict[str, List[EntityMention]]:
    """
    分析新闻中的实体出现频率
    
    Args:
        news_list: 新闻列表
        top_n: 返回前N个实体
    
    Returns:
        {"persons": [...], "orgs": [...], "countries": [...]}
    """
    # 统计
    person_counts: Dict[str, int] = defaultdict(int)
    person_sources: Dict[str, set] = defaultdict(set)
    person_headlines: Dict[str, List[Dict]] = defaultdict(list)
    
    org_counts: Dict[str, int] = defaultdict(int)
    org_sources: Dict[str, set] = defaultdict(set)
    org_headlines: Dict[str, List[Dict]] = defaultdict(list)
    
    country_counts: Dict[str, int] = defaultdict(int)
    country_sources: Dict[str, set] = defaultdict(set)
    country_headlines: Dict[str, List[Dict]] = defaultdict(list)
    
    # 分析每条新闻
    for news in news_list:
        title = news.get("title", "")
        source = news.get("source", "Unknown")
        link = news.get("url", news.get("link", ""))
        
        entities = extract_entities(title)
        
        for person in entities["persons"]:
            person_counts[person] += 1
            person_sources[person].add(source)
            if len(person_headlines[person]) < 3:
                person_headlines[person].append({"title": title, "source": source, "link": link})
        
        for org in entities["orgs"]:
            org_counts[org] += 1
            org_sources[org].add(source)
            if len(org_headlines[org]) < 3:
                org_headlines[org].append({"title": title, "source": source, "link": link})
        
        for country in entities["countries"]:
            country_counts[country] += 1
            country_sources[country].add(source)
            if len(country_headlines[country]) < 3:
                country_headlines[country].append({"title": title, "source": source, "link": link})
    
    # 构建结果
    def build_mentions(counts, sources, headlines, category) -> List[EntityMention]:
        mentions = []
        for name, count in counts.items():
            mentions.append(EntityMention(
                name=name,
                count=count,
                sources=list(sources[name]),
                headlines=headlines[name],
                category=category,
            ))
        mentions.sort(key=lambda x: x.count, reverse=True)
        return mentions[:top_n]
    
    return {
        "persons": build_mentions(person_counts, person_sources, person_headlines, "person"),
        "orgs": build_mentions(org_counts, org_sources, org_headlines, "organization"),
        "countries": build_mentions(country_counts, country_sources, country_headlines, "country"),
    }


def format_entity_report(entities: Dict[str, List[EntityMention]], max_per_category: int = 5) -> str:
    """
    格式化实体报告
    
    Args:
        entities: analyze_entities的返回结果
        max_per_category: 每个类别最大显示数量
    
    Returns:
        格式化的报告文本
    """
    lines = []
    
    if entities["persons"]:
        lines.append("【👤 热门人物】")
        for p in entities["persons"][:max_per_category]:
            lines.append(f"  {p.name}: {p.count}次 ({len(p.sources)}源)")
        lines.append("")
    
    if entities["orgs"]:
        lines.append("【🏢 热门组织】")
        for o in entities["orgs"][:max_per_category]:
            lines.append(f"  {o.name}: {o.count}次 ({len(o.sources)}源)")
        lines.append("")
    
    if entities["countries"]:
        lines.append("【🌍 热门国家/地区】")
        for c in entities["countries"][:max_per_category]:
            lines.append(f"  {c.name}: {c.count}次 ({len(c.sources)}源)")
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    print("=== 实体追踪测试 ===\n")
    
    test_news = [
        {"title": "特朗普宣布将对华加征关税", "source": "Reuters"},
        {"title": "习近平会见美国商务部长", "source": "新华社"},
        {"title": "OpenAI发布GPT-5，奥特曼称将改变世界", "source": "TechCrunch"},
        {"title": "马斯克宣布特斯拉将在上海建新工厂", "source": "Bloomberg"},
        {"title": "美联储鲍威尔暗示可能降息", "source": "CNBC"},
        {"title": "普京视察俄军前线，乌克兰局势紧张", "source": "BBC"},
        {"title": "黄仁勋：英伟达芯片需求创历史新高", "source": "Ars Technica"},
        {"title": "字节跳动计划IPO，估值超2000亿美元", "source": "华尔街日报"},
        {"title": "北约秘书长访华，讨论乌克兰问题", "source": "CNN"},
        {"title": "苹果发布新款iPhone，库克称是最大升级", "source": "The Verge"},
    ]
    
    entities = analyze_entities(test_news)
    print(format_entity_report(entities))
