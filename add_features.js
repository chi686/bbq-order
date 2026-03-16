// 新增功能代码片段

// 1. 桌位状态 - 记录开始用餐时间
function openTable(tableNum) {
    currentTable = tableNum;
    if (!tables[tableNum]) {
        tables[tableNum] = {items: [], total: 0, startTime: Date.now()};
    } else if (!tables[tableNum].startTime) {
        tables[tableNum].startTime = Date.now();
    }
    // ... 其他代码
}

// 2. 计算用餐时长
function getDiningTime(startTime) {
    if (!startTime) return '';
    const minutes = Math.floor((Date.now() - startTime) / 60000);
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) return `${hours}h${mins}m`;
    return `${mins}m`;
}

// 3. 备注功能 - 每个菜品可以加备注
function addNote(itemName) {
    const note = prompt('添加备注（如：不要辣、多放孜然）');
    if (note) {
        const table = tables[currentTable];
        const item = table.items.find(i => i.name === itemName);
        if (item) {
            item.note = note;
            saveData();
            renderMenu();
            updateOrderSummary();
        }
    }
}

// 4. 手势操作 - 左滑删除、长按快速加5
let touchStartX = 0;
let touchStartY = 0;
let longPressTimer = null;

function setupGestures(element, itemName, price) {
    element.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        
        // 长按快速加5
        longPressTimer = setTimeout(() => {
            changeQuantity(itemName, price, 5);
            navigator.vibrate && navigator.vibrate(50);
        }, 800);
    });
    
    element.addEventListener('touchmove', (e) => {
        clearTimeout(longPressTimer);
    });
    
    element.addEventListener('touchend', (e) => {
        clearTimeout(longPressTimer);
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;
        
        // 左滑删除（横向滑动超过100px且纵向小于50px）
        if (deltaX < -100 && Math.abs(deltaY) < 50) {
            if (confirm(`删除 ${itemName}？`)) {
                const table = tables[currentTable];
                table.items = table.items.filter(i => i.name !== itemName);
                table.total = table.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
                saveData();
                renderMenu();
                updateOrderSummary();
            }
        }
    });
}
