#!/usr/bin/env python3
"""添加桌位状态、备注功能、手势操作"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 在 CSS 中添加新样式
new_css = """
        .table-time {
            font-size: 12px;
            color: #ff6b6b;
            margin-top: 5px;
            font-weight: 600;
        }
        .table-time.warning { color: #ff6b6b; animation: blink 1s infinite; }
        @keyframes blink { 0%, 50%, 100% { opacity: 1; } 25%, 75% { opacity: 0.5; } }
        .item-note {
            font-size: 13px;
            color: #999;
            margin-top: 3px;
            font-style: italic;
        }
        .btn-note {
            background: #f0f0f0;
            color: #666;
            padding: 5px 12px;
            font-size: 13px;
            border-radius: 15px;
        }
        .swipe-hint {
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            z-index: 1000;
            animation: fadeOut 2s forwards;
        }
        @keyframes fadeOut { 0% { opacity: 1; } 80% { opacity: 1; } 100% { opacity: 0; } }
"""

# 找到 .hidden 样式前插入
html = html.replace('        .hidden { display: none; }', new_css + '        .hidden { display: none; }')

# 2. 修改 tables 数据结构，添加 startTime
html = html.replace(
    "let tables = {};",
    "let tables = {}; // {1: {items: [], total: 0, startTime: timestamp, note: ''}}"
)

# 3. 添加辅助函数
helper_functions = """
        // 计算用餐时长
        function getDiningTime(startTime) {
            if (!startTime) return '';
            const minutes = Math.floor((Date.now() - startTime) / 60000);
            if (minutes < 1) return '刚坐下';
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            if (hours > 0) return `${hours}小时${mins}分`;
            return `${mins}分钟`;
        }

        // 检查是否需要翻台提醒
        function needsTurnover(startTime) {
            if (!startTime) return false;
            const minutes = Math.floor((Date.now() - startTime) / 60000);
            return minutes >= 60; // 超过1小时
        }

        // 添加备注
        function addNote(itemName) {
            const note = prompt('添加备注（如：不要辣、多放孜然）');
            if (note !== null) {
                const table = tables[currentTable];
                const item = table.items.find(i => i.name === itemName);
                if (item) {
                    item.note = note || '';
                    saveData();
                    renderMenu();
                    updateOrderSummary();
                }
            }
        }

        // 手势操作
        let touchStartX = 0, touchStartY = 0, longPressTimer = null;
        
        function setupGestures(element, itemName, price) {
            element.addEventListener('touchstart', (e) => {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
                longPressTimer = setTimeout(() => {
                    changeQuantity(itemName, price, 5);
                    if (navigator.vibrate) navigator.vibrate(50);
                    showHint('已添加 5 个');
                }, 800);
            });
            
            element.addEventListener('touchmove', () => clearTimeout(longPressTimer));
            
            element.addEventListener('touchend', (e) => {
                clearTimeout(longPressTimer);
                const touchEndX = e.changedTouches[0].clientX;
                const deltaX = touchEndX - touchStartX;
                const deltaY = Math.abs(e.changedTouches[0].clientY - touchStartY);
                
                if (deltaX < -100 && deltaY < 50) {
                    const table = tables[currentTable];
                    const item = table.items.find(i => i.name === itemName);
                    if (item && confirm(`删除 ${itemName}？`)) {
                        table.items = table.items.filter(i => i.name !== itemName);
                        table.total = table.items.reduce((sum, i) => sum + i.price * i.quantity, 0);
                        saveData();
                        renderMenu();
                        updateOrderSummary();
                        showHint('已删除');
                    }
                }
            });
        }

        function showHint(text) {
            const hint = document.createElement('div');
            hint.className = 'swipe-hint';
            hint.textContent = text;
            document.body.appendChild(hint);
            setTimeout(() => hint.remove(), 2000);
        }
"""

# 在 init() 函数前插入
html = html.replace('        // 初始化\n        function init()', helper_functions + '\n        // 初始化\n        function init()')

# 4. 修改 renderTableGrid 显示用餐时长
old_render_table = """                card.innerHTML = `
                    <div class="table-number">${i}号桌</div>
                    <div class="table-amount">${occupied ? '¥' + table.total : '空桌'}</div>
                `;"""

new_render_table = """                const timeStr = occupied ? getDiningTime(table.startTime) : '';
                const needWarn = needsTurnover(table.startTime);
                card.innerHTML = `
                    <div class="table-number">${i}号桌</div>
                    <div class="table-amount">${occupied ? '¥' + table.total : '空桌'}</div>
                    ${timeStr ? `<div class="table-time${needWarn ? ' warning' : ''}">⏱️ ${timeStr}</div>` : ''}
                `;"""

html = html.replace(old_render_table, new_render_table)

# 5. 修改 openTable 记录开始时间
old_open_table = """            if (!tables[tableNum]) {
                tables[tableNum] = {items: [], total: 0};
            }"""

new_open_table = """            if (!tables[tableNum]) {
                tables[tableNum] = {items: [], total: 0, startTime: Date.now()};
            } else if (!tables[tableNum].startTime) {
                tables[tableNum].startTime = Date.now();
            }"""

html = html.replace(old_open_table, new_open_table)

# 6. 修改 renderMenu 添加备注按钮和手势
old_menu_item = """                    itemDiv.innerHTML = `
                        <div class="item-info">
                            <div class="item-name">${item.name}</div>
                            <div class="item-price">¥${item.price}</div>
                        </div>
                        <div class="item-controls">
                            <button class="btn btn-minus" onclick="changeQuantity('${item.name}', ${item.price}, -1)">-</button>
                            <div class="quantity">${quantity}</div>
                            <button class="btn btn-plus" onclick="changeQuantity('${item.name}', ${item.price}, 1)">+</button>
                        </div>
                    `;"""

new_menu_item = """                    const tableItem = table.items.find(i => i.name === item.name);
                    const note = tableItem?.note || '';
                    itemDiv.innerHTML = `
                        <div class="item-info">
                            <div class="item-name">${item.name}</div>
                            <div class="item-price">¥${item.price}</div>
                            ${note ? `<div class="item-note">📝 ${note}</div>` : ''}
                        </div>
                        <div class="item-controls">
                            ${quantity > 0 ? `<button class="btn btn-note" onclick="addNote('${item.name}')">备注</button>` : ''}
                            <button class="btn btn-minus" onclick="changeQuantity('${item.name}', ${item.price}, -1)">-</button>
                            <div class="quantity">${quantity}</div>
                            <button class="btn btn-plus" onclick="changeQuantity('${item.name}', ${item.price}, 1)">+</button>
                        </div>
                    `;
                    if (quantity > 0) setupGestures(itemDiv, item.name, item.price);"""

html = html.replace(old_menu_item, new_menu_item)

# 7. 修改 updateOrderSummary 显示备注
old_summary = """                    html += `
                        <div class="summary-item">
                            <span>${item.name} × ${item.quantity}</span>
                            <span>¥${item.price * item.quantity}</span>
                        </div>
                    `;"""

new_summary = """                    html += `
                        <div class="summary-item">
                            <div>
                                <div>${item.name} × ${item.quantity}</div>
                                ${item.note ? `<div class="item-note">📝 ${item.note}</div>` : ''}
                            </div>
                            <span>¥${item.price * item.quantity}</span>
                        </div>
                    `;"""

html = html.replace(old_summary, new_summary)

# 8. 修改 checkout 清除开始时间
old_checkout_clear = """            tables[currentTable] = {items: [], total: 0};"""
new_checkout_clear = """            tables[currentTable] = {items: [], total: 0, startTime: null};"""
html = html.replace(old_checkout_clear, new_checkout_clear)

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ 功能已添加：桌位状态、备注功能、手势操作")
