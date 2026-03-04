#!/usr/bin/env python3
"""
Fox新闻聚合器 - 分析引擎

包含:
- correlation: 关联分析（跨源主题检测）
- alerts: 告警检测（关键词告警）
- entities: 实体追踪（人物/组织/国家）
"""

from .correlation import (
    analyze_correlations,
    get_correlation_summary,
    format_correlation_report,
    clear_correlation_history,
    CorrelationResults,
    EmergingPattern,
    MomentumSignal,
    CrossSourceCorrelation,
)

from .alerts import (
    contains_alert_keyword,
    find_all_alerts,
    calculate_alert_score,
    detect_region,
    classify_news_alert,
    filter_alert_news,
    format_alert_summary,
)

from .entities import (
    extract_entities,
    analyze_entities,
    format_entity_report,
    EntityMention,
)

__all__ = [
    # Correlation
    "analyze_correlations",
    "get_correlation_summary",
    "format_correlation_report",
    "clear_correlation_history",
    "CorrelationResults",
    "EmergingPattern",
    "MomentumSignal",
    "CrossSourceCorrelation",
    
    # Alerts
    "contains_alert_keyword",
    "find_all_alerts",
    "calculate_alert_score",
    "detect_region",
    "classify_news_alert",
    "filter_alert_news",
    "format_alert_summary",
    
    # Entities
    "extract_entities",
    "analyze_entities",
    "format_entity_report",
    "EntityMention",
]
