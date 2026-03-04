/**
 * Fox每日新闻 v5.2
 */

class NewsApp {
    constructor() {
        this.data = null;
        this.currentSection = null;
        this.transCache = new Map();
        
        this.els = {
            stats: document.getElementById('stats'),
            nav: document.getElementById('nav'),
            content: document.getElementById('content'),
            searchInput: document.getElementById('searchInput'),
            datePicker: document.getElementById('datePicker'),
            themeToggle: document.getElementById('themeToggle'),
            backTop: document.getElementById('backTop'),
            updateTime: document.getElementById('updateTime'),
            menuToggle: document.getElementById('menuToggle'),
            overlay: document.getElementById('overlay')
        };
        
        this.init();
    }
    
    init() {
        this.initTheme();
        this.bindEvents();
        this.loadToday();
    }
    
    initTheme() {
        if (localStorage.getItem('theme') === 'dark') {
            document.body.classList.add('dark');
        }
    }
    
    toggleTheme() {
        const isDark = document.body.classList.toggle('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }
    
    bindEvents() {
        this.els.themeToggle?.addEventListener('click', () => this.toggleTheme());
        this.els.datePicker?.addEventListener('change', (e) => this.loadDate(e.target.value));
        
        // 移动端菜单
        this.els.menuToggle?.addEventListener('click', () => this.toggleMenu());
        this.els.overlay?.addEventListener('click', () => this.closeMenu());
        
        let searchTimer;
        this.els.searchInput?.addEventListener('input', (e) => {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => this.search(e.target.value), 300);
        });
        
        this.els.backTop?.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        let scrollTimer;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimer);
            scrollTimer = setTimeout(() => {
                this.els.backTop?.classList.toggle('visible', window.scrollY > 300);
            }, 50);
        }, { passive: true });
        
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT') return;
            if (e.key === '/' || e.key === 's') {
                e.preventDefault();
                this.els.searchInput?.focus();
            }
            if (e.key === 'Escape') {
                this.closeMenu();
            }
        });
    }
    
    toggleMenu() {
        const sidebar = document.querySelector('.sidebar');
        const isOpen = sidebar?.classList.toggle('open');
        this.els.menuToggle?.classList.toggle('active', isOpen);
        this.els.overlay?.classList.toggle('visible', isOpen);
        document.body.style.overflow = isOpen ? 'hidden' : '';
    }
    
    closeMenu() {
        const sidebar = document.querySelector('.sidebar');
        sidebar?.classList.remove('open');
        this.els.menuToggle?.classList.remove('active');
        this.els.overlay?.classList.remove('visible');
        document.body.style.overflow = '';
    }
    
    async loadToday() {
        const today = new Date().toISOString().split('T')[0];
        if (this.els.datePicker) {
            this.els.datePicker.value = today;
            this.els.datePicker.max = today;
        }
        await this.loadDate(today);
    }
    
    async loadDate(date) {
        this.showSkeleton();
        
        try {
            const res = await fetch(`data/${date}.json?t=${Date.now()}`);
            if (!res.ok) throw new Error('No data');
            this.data = await res.json();
            this.render();
        } catch (e) {
            this.showError(date);
        }
    }
    
    render() {
        if (!this.data) return;
        
        const total = Object.values(this.data.sections).reduce((s, sec) => s + sec.count, 0);
        const count = Object.keys(this.data.sections).length;
        if (this.els.stats) {
            this.els.stats.textContent = `${count}个分类 · ${total}条`;
        }
        
        if (this.els.updateTime && this.data.generated_at) {
            this.els.updateTime.textContent = `更新于 ${new Date(this.data.generated_at).toLocaleString('zh-CN')}`;
        }
        
        this.renderNav();
        
        const firstId = Object.keys(this.data.sections)[0];
        if (firstId) this.showSection(firstId);
    }
    
    renderNav() {
        const sections = this.data.sections;
        const order = ['daily', 'weibo', 'zhihu', 'bilibili', 'douyin', 'toutiao',
                       'tech_cn', 'tech_intl', 'ai_models', 'ai_opensource', 'ai_research',
                       'ai_tools', 'ai_news', 'finance', 'science', 'intl_intel',
                       'thepaper', 'v2ex', 'douban', 'epic'];
        
        const sorted = Object.keys(sections).sort((a, b) => {
            const ia = order.indexOf(a);
            const ib = order.indexOf(b);
            if (ia === -1 && ib === -1) return 0;
            if (ia === -1) return 1;
            if (ib === -1) return -1;
            return ia - ib;
        });
        
        this.els.nav.innerHTML = sorted.map(id => {
            const section = sections[id];
            return `
                <button class="nav-item" data-id="${id}">
                    <span>${section.name}</span>
                    <span class="nav-count">${section.count}</span>
                </button>
            `;
        }).join('');
        
        this.els.nav.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                this.showSection(item.dataset.id);
                this.closeMenu(); // 移动端点击后关闭菜单
            });
        });
    }
    
    showSection(sectionId) {
        const section = this.data.sections[sectionId];
        if (!section) return;
        
        this.currentSection = sectionId;
        
        this.els.nav.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.id === sectionId);
        });
        
        if (!section.items.length) {
            this.els.content.innerHTML = '<div class="empty"><p>暂无内容</p></div>';
            return;
        }
        
        this.els.content.innerHTML = `
            <div class="section-header">
                <h2 class="section-title">${section.name}<span class="section-count">${section.count}条</span></h2>
            </div>
            <div class="news-list">
                ${section.items.map((item, i) => this.renderItem(item, i)).join('')}
            </div>
        `;
        
        requestIdleCallback(() => this.translateItems(), { timeout: 500 });
    }
    
    renderItem(item, index) {
        const url = this.getUrl(item);
        const isEng = this.isEnglish(item.title);
        const isTop = index < 3;
        const rankClass = isTop ? 'top' : '';
        const rankText = isTop ? (index + 1) : '';
        
        let html = '<div class="news-item">';
        
        // 标题行
        html += '<div class="title-row">';
        html += `<span class="rank ${rankClass}">${rankText}</span>`;
        html += `<a class="title" href="${url}" target="_blank" rel="noopener">${this.escapeHtml(item.title)}<span class="ext">↗</span></a>`;
        html += '</div>';
        
        // 翻译（如果需要）
        if (isEng) {
            html += '<div class="trans">翻译中...</div>';
        }
        
        // 元信息
        if (item.hot_text || item.rating || item.price) {
            html += '<div class="meta">';
            if (item.hot_text) html += `<span class="hot">${item.hot_text}</span>`;
            if (item.rating) html += `<span>${item.rating}分</span>`;
            if (item.price) html += `<span>${item.price}</span>`;
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    }
    
    async translateItems() {
        const items = document.querySelectorAll('.news-item');
        const pending = [];
        
        // 收集需要翻译的项目
        for (const item of items) {
            const titleEl = item.querySelector('.title');
            const transEl = item.querySelector('.trans');
            
            if (!titleEl || !transEl) continue;
            
            let title = titleEl.textContent.replace('↗', '').trim();
            
            if (!this.isEnglish(title)) {
                transEl.remove();
                continue;
            }
            
            if (this.transCache.has(title)) {
                transEl.textContent = this.transCache.get(title);
                continue;
            }
            
            pending.push({ item, title, transEl });
        }
        
        // 并行翻译（最多3个并发）
        const batchSize = 3;
        for (let i = 0; i < pending.length; i += batchSize) {
            const batch = pending.slice(i, i + batchSize);
            await Promise.all(batch.map(p => this.translateOne(p.title, p.transEl)));
            if (i + batchSize < pending.length) {
                await new Promise(r => setTimeout(r, 100)); // 批次间短暂延迟
            }
        }
    }
    
    async translateOne(title, transEl) {
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 3000);
            
            const res = await fetch(
                `https://api.mymemory.translated.net/get?q=${encodeURIComponent(title)}&langpair=en|zh-CN`,
                { signal: controller.signal }
            );
            clearTimeout(timeout);
            
            const data = await res.json();
            
            if (data.responseStatus === 200 && data.responseData?.translatedText) {
                const text = data.responseData.translatedText;
                this.transCache.set(title, text);
                transEl.textContent = text;
            } else {
                transEl.remove();
            }
        } catch (e) {
            transEl.remove();
        }
    }
    
    isEnglish(text) {
        const en = (text.match(/[a-zA-Z]/g) || []).length;
        const zh = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
        return en > zh * 1.5 && en > 15;
    }
    
    search(q) {
        if (!this.data) return;
        
        if (!q.trim()) {
            if (this.currentSection) this.showSection(this.currentSection);
            return;
        }
        
        const query = q.toLowerCase();
        const results = [];
        
        for (const section of Object.values(this.data.sections)) {
            for (const item of section.items) {
                if (item.title.toLowerCase().includes(query)) {
                    results.push(item);
                }
            }
        }
        
        this.els.nav.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        if (!results.length) {
            this.els.content.innerHTML = '<div class="empty"><p>未找到</p></div>';
            return;
        }
        
        this.els.content.innerHTML = `
            <div class="section-header">
                <h2 class="section-title">搜索结果<span class="section-count">${results.length}条</span></h2>
            </div>
            <div class="news-list">
                ${results.slice(0, 100).map((item, i) => this.renderItem(item, i)).join('')}
            </div>
        `;
    }
    
    getUrl(item) {
        return item.url || item.searchUrl || `https://www.bing.com/search?q=${encodeURIComponent(item.title)}`;
    }
    
    escapeHtml(text) {
        return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
    
    escapeAttr(text) {
        return text.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }
    
    showSkeleton() {
        this.els.content.innerHTML = `
            <div class="section-header">
                <h2 class="section-title">加载中...</h2>
            </div>
            <div class="skeleton">
                ${Array(10).fill('<div class="skeleton-item"></div>').join('')}
            </div>
        `;
    }
    
    showError(date) {
        const today = new Date().toISOString().split('T')[0];
        const msg = date === today ? '今日日报尚未生成' : `${date} 暂无数据`;
        this.els.content.innerHTML = `<div class="empty"><p>${msg}</p></div>`;
    }
}

const app = new NewsApp();
