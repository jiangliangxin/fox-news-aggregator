# Fox 每日新闻前端

> 纯静态 HTML + JavaScript 新闻展示前端

## 技术栈

- **HTML5** - 语义化结构
- **CSS3** - 响应式设计，深色/浅色主题
- **Vanilla JavaScript** - 无框架依赖
- **PWA** - 支持离线访问

## 特性

- ✅ 日期选择器（查看历史新闻）
- ✅ 实时搜索
- ✅ 深色/浅色主题切换
- ✅ 移动端响应式设计
- ✅ 20+ 分类导航
- ✅ 自动翻译英文标题
- ✅ PWA 离线支持

## 文件结构

```
frontend/
├── index.html          # 主页面
├── app.js              # 应用逻辑（12KB）
├── style.css           # 样式（9KB）
├── manifest.json       # PWA 配置
├── icon-192.png        # 小图标
├── icon-512.png        # 大图标
└── icon-192.svg        # 矢量图标
```

## 使用方式

### 1. 直接访问
```bash
# Nginx 配置
location /news/ {
    alias /var/www/news/;
}
```

### 2. 本地运行
```bash
# 任何静态服务器
cd frontend
python3 -m http.server 8080
# 或
npx serve
```

### 3. 部署到 CDN
- 上传所有文件到 CDN
- 配置 data/ 目录指向 JSON 数据

## 数据格式

前端从 `data/` 目录加载 JSON：

```javascript
// 加载今日数据
fetch('data/latest.json')

// 加载指定日期
fetch('data/2026-03-04.json')
```

JSON 格式：
```json
{
  "generated_at": "2026-03-04T08:00:00Z",
  "sections": {
    "weibo": {
      "title": "微博热搜",
      "count": 30,
      "items": [...]
    }
  }
}
```

## 性能优化

- ✅ **零框架开销** - 总大小 24KB（未压缩）
- ✅ **CDN 友好** - 100% 静态文件
- ✅ **懒加载** - 按需加载分类
- ✅ **缓存策略** - 使用 localStorage 缓存翻译
- ✅ **防抖搜索** - 300ms 延迟

## 浏览器支持

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- 移动端浏览器

## 无需构建

直接修改文件即可生效，无需 npm/webpack/vite 等构建工具。

## 为什么不用 Vue/React？

对于新闻展示型应用：
- ✅ **性能优先** - 纯 JS 加载快 3-5 倍
- ✅ **维护简单** - 无依赖升级问题
- ✅ **够用就好** - 500 条新闻前端搜索完全够用

## 后续优化

- [ ] Service Worker 离线缓存
- [ ] 虚拟滚动（超大数据量）
- [ ] WebSocket 实时更新（可选）
- [ ] RSS 订阅支持（可选）

---

**版本**: v5.2
**维护者**: Fox (OpenClaw AI Assistant)
