// 全局工具函数
let currentUser = null;

async function loadCurrentUser() {
    if (currentUser) {
        renderUserInfo(currentUser);
        return currentUser;
    }
    try {
        currentUser = await api.getCurrentUser();
        renderUserInfo(currentUser);
        return currentUser;
    } catch (error) {
        window.location.href = 'login.html';
        throw error;
    }
}

function renderUserInfo(user) {
    if (!user) return;
    
    const userInfo = document.querySelector('.user-info');
    if (userInfo) {
        const usernameEl = userInfo.querySelector('strong');
        const avatarEl = userInfo.querySelector('.user-avatar');
        const welcomeEl = userInfo.querySelector('span');
        
        if (usernameEl) usernameEl.textContent = user.username;
        if (avatarEl) {
            avatarEl.textContent = user.username.charAt(0).toUpperCase();
            avatarEl.style.backgroundColor = getAvatarColor(user.username);
        }
        if (welcomeEl) {
            welcomeEl.innerHTML = welcomeEl.innerHTML.replace(/欢迎,\s*<strong>.*?<\/strong>/, `欢迎, <strong>${user.username}</strong>`);
        }
    }
}

function getAvatarColor(username) {
    const colors = ['#667eea', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16'];
    let hash = 0;
    for (let i = 0; i < username.length; i++) {
        hash = username.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
}

async function handleLogout() {
    if (confirm('确定要退出登录吗？')) {
        try {
            await api.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            currentUser = null;
            window.location.href = 'login.html';
        }
    }
}

function getCurrentUser() {
    return currentUser;
}

// 格式化日期
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 格式化货币
function formatCurrency(amount) {
    if (!amount || amount === 0) return '¥0.00';
    return '¥' + parseFloat(amount).toFixed(2);
}

// 显示警告消息
function showAlert(message, type = 'success') {
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span style="font-size: 16px;">${type === 'success' ? '✓' : type === 'error' ? '✗' : '⚠'}</span>
        <span>${message}</span>
    `;
    
    const container = document.querySelector('.page-content') || document.querySelector('.login-container');
    container.insertBefore(alert, container.firstChild);
    
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 3000);
}

// 防抖函数
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 创建模态框
function createModal(title, content, onConfirm) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    overlay.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h3>${title}</h3>
                <button class="close-btn" onclick="closeModal()">×</button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal()">取消</button>
                <button class="btn btn-primary" id="modal-confirm-btn">确认</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    setTimeout(() => overlay.classList.add('show'), 10);
    
    window.closeModal = function() {
        overlay.classList.remove('show');
        setTimeout(() => overlay.remove(), 300);
    };
    
    // 带防抖的确认按钮处理
    const confirmBtn = overlay.querySelector('#modal-confirm-btn');
    const debouncedConfirm = debounce(async function() {
        confirmBtn.disabled = true;
        confirmBtn.textContent = '保存中...';
        try {
            await onConfirm();
            closeModal();
        } catch (error) {
            alert(error.message);
        } finally {
            confirmBtn.disabled = false;
            confirmBtn.textContent = '确认';
        }
    }, 500);
    
    confirmBtn.addEventListener('click', debouncedConfirm);
}

// 生成随机ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
