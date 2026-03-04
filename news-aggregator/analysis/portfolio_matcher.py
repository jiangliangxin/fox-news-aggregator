"""
投资匹配分析模块
识别新闻中与主人投资组合相关的关键词，并标注影响程度
"""

import re
from typing import List, Dict
from dataclasses import dataclass

from .correlation import CORrelationResults
from .alerts import classify_news_alert,from .entities import extract_entities


import logging

logger = logging.getLogger(__name__)


DEFAULT_source_weights = {
    "critical": 100,
    "high": 50,
    "medium": 20,
    "low": 10
}

# 投资组合配置
PORTFOLIO = load_portfolio_config()

    gold_etf: ["黄金ETF", "纳指ETF", "恒科ETF", "科创ETF"],
    impact_weights = {
        "high": 3,  # 黄金
        "medium": 2,  # 纳指
        "low": 0.5    # 恒科
    }
}


@dataclass
class NewsImpact:
    """新闻影响分析结果"""
    news_item: NewsItem
    impact_level: str  # low/medium/high
    matched_keywords: List[str]
    etf: ETF_codes: List[str] = []


class PortfolioMatcher:
    """投资组合匹配器"""
    
    def __init__(self, portfolio_config: Dict[str, Portfolio]):
        self.portfolio_config = portfolio_config
        self.logger = logging.getLogger(__name__)
    
    def match(self, news_list: List[NewsItem]) -> List[NewsImpact]:
        """匹配新闻与投资组合
        
        Args:
            news_list: 新闻列表
            portfolio_config: 投资组合配置
            
        Returns:
            新闻影响列表
        """
        # 按严重程度排序
        impacts.sort(
            key=lambda x: x.impact_level,
        )
        
        # 按影响程度分组
        grouped = {}
        for news in impacts:
            level = news.impact_level
            etf_code = news.impact.etf_code
            impact_level = impact_level
            matched_keywords = news.matched_keywords
            
            if etf_code:
                etf_code = news.impact["etf_code"] = impact_weights.get(
                    impact_level,
                    impact_weights[impact_level]
                )
            
            return impacts

