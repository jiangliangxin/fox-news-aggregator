#!/usr/bin/env python3
"""
日报 JSON 导出器
为新闻网页提供数据
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def export_news_json(news_data: Dict[str, List[Any]], output_dir: Path = None):
    """
    导出新闻数据为 JSON 格式
    
    Args:
        news_data: 分类新闻数据
        output_dir: 输出目录
    """
    if output_dir is None:
        output_dir = Path("/var/www/news/data")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 构建JSON结构
    json_data = {
        "date": today,
        "generated_at": datetime.now().isoformat(),
        "sections": {}
    }
    
    for group_name, items in news_data.items():
        if not items:
            continue
            
        section = {
            "name": group_name,
            "count": len(items),
            "items": []
        }
        
        for item in items[:30]:  # 每个分类最多30条
            item_data = {
                "title": item.title,
                "url": item.url or "",
            }
            
            # 添加热度值
            if hasattr(item, 'hot_value') and item.hot_value:
                item_data["hot"] = item.hot_value
                if item.hot_value >= 10000:
                    item_data["hot_text"] = f"{item.hot_value // 10000}万"
                else:
                    item_data["hot_text"] = str(item.hot_value)
            
            # 添加额外信息
            if hasattr(item, 'extra') and item.extra:
                if "rating" in item.extra:
                    item_data["rating"] = item.extra["rating"]
                if "source" in item.extra:
                    item_data["source"] = item.extra["source"]
            
            section["items"].append(item_data)
        
        json_data["sections"][group_name] = section
    
    # 统计信息
    total = sum(len(items) for items in news_data.values())
    json_data["stats"] = {
        "total": total,
        "groups": len(news_data)
    }
    
    # 保存今日数据
    today_file = output_dir / f"{today}.json"
    with open(today_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    # 更新 latest.json（指向最新数据）
    latest_file = output_dir / "latest.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    # 更新索引文件（记录所有历史日期）
    index_file = output_dir / "index.json"
    index_data = {"dates": []}
    
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            index_data = json.load(f)
    
    if today not in index_data["dates"]:
        index_data["dates"].insert(0, today)
        # 只保留最近30天
        index_data["dates"] = index_data["dates"][:30]
    
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    return today_file
