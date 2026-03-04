"""
投资组合配置
记录主人的投资偏好，用于个性化推荐
"""

# 主人投资偏好
PORTfolios = {
    "黄金ETF": {
        "code": "518880",
        "name": "黄金ETF",
        "keywords": ["美元", "通胀", "CPI", "美联储", "地缘", "避险", "金价", "黄金"],
        "impact": "high"
    },
    "纳指ETF": {
        "code": "513100",
        "name": "纳指ETF",
        "keywords": ["美联储", "降息", "科技股", "AI", "纳指", "纳斯达克"],
        "impact": "high"
    },
    "恒科ETF": {
        "code": "513180",
        "name": "恒科ETF",
        "keywords": ["港股", "中概股", "互联网监管", "腾讯", "阿里"],
        "impact": "medium"
    },
    "科创ETF": {
        "code": "科创ETF",
        "keywords": ["中芯国际", "芯片", "半导体", "国产替代"],
        "impact": "medium"
    }
}

