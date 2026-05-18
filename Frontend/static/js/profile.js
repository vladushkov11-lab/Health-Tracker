// API Configuration
const API_GATEWAY_URL = 'http://localhost:8001/api/v1';
const API_GATEWAY_APP_URL = 'http://localhost:8001/app';

// State
let currentUser = null;
let userStats = null;
let authChecked = false;

// DOM Elements
const profileForm = document.getElementById('profile-form');
const healthProfileForm = document.getElementById('health-profile-form');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkAuthAndLoad();  // Ждём авторизации перед загрузкой
});

// Проверка авторизации через API
async function checkAuth() {
    if (authChecked) return true;
    authChecked = true;
    
    try {
        const response = await fetch(`${API_GATEWAY_URL}/me`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            window.location.href = '/login';
            return false;
        }
        
        const userData = await response.json();
        if (userData.status === 'error' || !userData.user_id) {
            window.location.href = '/login';
            return false;
        }
        
        currentUser = userData;
        localStorage.setItem('currentUser', JSON.stringify(userData));
        document.getElementById('profile-user-name').textContent = userData?.first_name || 'Пользователь';
        return true;
    } catch (error) {
        console.error('Auth check error:', error);
        window.location.href = '/login';
        return false;
    }
}

// Проверяем авторизацию и загружаем данные
async function checkAuthAndLoad() {
    const isAuthenticated = await checkAuth();
    if (isAuthenticated) {
        loadProfile();
        loadStats();
    }
}

function setupEventListeners() {
    // Navigation
    document.getElementById('profile-logout-btn').addEventListener('click', logout);
    document.getElementById('refresh-stats-btn').addEventListener('click', loadStats);
    document.getElementById('delete-account-btn').addEventListener('click', deleteAccount);

    // Forms
    profileForm.addEventListener('submit', handleProfileUpdate);
    healthProfileForm.addEventListener('submit', handleHealthProfileUpdate);
}

function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = '/login';
}

// Profile Functions
async function loadProfile() {
    try {
        // Load account info
        const userResponse = await fetch(`${API_GATEWAY_URL}/me`, {
            credentials: 'include'
        });
        
        if (!userResponse.ok) {
            if (userResponse.status === 401) {
                window.location.href = '/login';
                return;
            }
            throw new Error('Ошибка загрузки профиля');
        }
        
        const userData = await userResponse.json();
        if (userData.status !== 'error') {
            currentUser = userData;
            document.getElementById('profile-firstname').value = userData.first_name || '';
            document.getElementById('profile-lastname').value = userData.last_name || '';
            document.getElementById('profile-email').value = userData.email || '';
            document.getElementById('profile-phone').value = userData.phone_number || '';
        }

        // Load health profile
        const profileResponse = await fetch(`${API_GATEWAY_APP_URL}/get_profile`, {
            credentials: 'include'
        });

        if (profileResponse.ok) {
            const profileData = await profileResponse.json();
            document.getElementById('profile-height').value = profileData.height || '';
            document.getElementById('profile-weight').value = profileData.weight || '';
            document.getElementById('profile-target-weight').value = profileData.target_weight || '';
            document.getElementById('profile-daily-step-goal').value = profileData.daily_step_goal || '';
            document.getElementById('profile-gender').value = profileData.gender || '';
            document.getElementById('profile-birth-date').value = profileData.birth_date || '';
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        if (error.message.includes('401')) {
            window.location.href = '/login';
        }
    }
}

async function handleProfileUpdate(e) {
    e.preventDefault();
    const messageEl = document.getElementById('profile-message');

    const userData = {
        email: document.getElementById('profile-email').value,
        first_name: document.getElementById('profile-firstname').value,
        last_name: document.getElementById('profile-lastname').value,
        phone_number: document.getElementById('profile-phone').value
    };

    try {
        const response = await fetch(`${API_GATEWAY_URL}/update_user`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(userData)
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            throw new Error('Ошибка обновления профиля');
        }

        messageEl.textContent = 'Профиль успешно обновлён!';
        messageEl.className = 'success-message';
        setTimeout(() => messageEl.textContent = '', 3000);
    } catch (error) {
        if (error.message.includes('401')) {
            window.location.href = '/login';
            return;
        }
        messageEl.textContent = error.message;
        messageEl.className = 'error-message';
        setTimeout(() => messageEl.className = 'success-message', 3000);
    }
}

async function handleHealthProfileUpdate(e) {
    e.preventDefault();
    const messageEl = document.getElementById('health-profile-message');

    const profileData = {
        birth_date: document.getElementById('profile-birth-date').value || null,
        height: parseFloat(document.getElementById('profile-height').value) || null,
        weight: parseFloat(document.getElementById('profile-weight').value) || null,
        gender: document.getElementById('profile-gender').value || null,
        target_weight: parseFloat(document.getElementById('profile-target-weight').value) || null,
        daily_step_goal: parseInt(document.getElementById('profile-daily-step-goal').value) || null
    };

    try {
        const response = await fetch(`${API_GATEWAY_APP_URL}/profile_update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(profileData)
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            throw new Error('Ошибка обновления профиля');
        }

        messageEl.textContent = 'Профиль здоровья успешно обновлён!';
        messageEl.className = 'success-message';
        setTimeout(() => messageEl.textContent = '', 3000);
        
        loadStats();
    } catch (error) {
        if (error.message.includes('401')) {
            window.location.href = '/login';
            return;
        }
        messageEl.textContent = error.message;
        messageEl.className = 'error-message';
        setTimeout(() => messageEl.className = 'success-message', 3000);
    }
}

async function deleteAccount() {
    if (!confirm('Вы уверены, что хотите удалить аккаунт? Это действие необратимо!')) {
        return;
    }

    if (!confirm('Последний раз: все данные будут потеряны. Подтвердите удаление.')) {
        return;
    }

    try {
        const response = await fetch(`${API_GATEWAY_URL}/delete_user`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка удаления аккаунта');
        }

        alert('Аккаунт успешно удалён. До новых встреч!');
        logout();
    } catch (error) {
        if (error.message.includes('401')) {
            window.location.href = '/login';
            return;
        }
        alert(error.message);
    }
}

// Statistics Functions
async function loadStats() {
    const statsContent = document.getElementById('stats-content');
    statsContent.innerHTML = '<p class="loading-message">Загрузка статистики...</p>';

    try {
        const response = await fetch(`${API_GATEWAY_APP_URL}/stats`, {
            credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            throw new Error('Ошибка загрузки статистики');
        }

        userStats = await response.json();
        renderStats(userStats);
    } catch (error) {
        console.error('Error loading stats:', error);
        if (error.message.includes('401')) {
            window.location.href = '/login';
            return;
        }
        statsContent.innerHTML = `<p class="error-message">Ошибка загрузки статистики: ${error.message}</p>`;
    }
}

function renderStats(stats) {
    const statsContent = document.getElementById('stats-content');

    if (stats.total_metrics === 0) {
        statsContent.innerHTML = `
            <p class="empty-message">Нет данных для отображения. Добавьте метрики, чтобы увидеть статистику.</p>
        `;
        return;
    }

    let html = `
        <div class="stats-grid-detailed">
            <div class="stat-item">
                <div class="stat-label">Средние шаги</div>
                <div class="stat-value">${Math.round(stats.averages?.steps || 0)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Средние калории</div>
                <div class="stat-value">${Math.round(stats.averages?.calories || 0)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Средний сон (ч)</div>
                <div class="stat-value">${(stats.averages?.sleep_hours || 0).toFixed(1)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Среднее настроение</div>
                <div class="stat-value">${(stats.averages?.mood || 0).toFixed(1)}</div>
            </div>
        </div>
    `;

    // Trends
    if (stats.trends && Object.keys(stats.trends).length > 0) {
        html += `
            <h4 style="margin-top: 20px; margin-bottom: 10px;">📈 Тренды</h4>
            <div class="trends-list">
        `;
        
        for (const [field, trend] of Object.entries(stats.trends)) {
            const icon = trend.direction === 'up' ? '📈' : trend.direction === 'down' ? '📉' : '➡️';
            const className = `trend-${trend.direction}`;
            const fieldName = {
                steps: 'Шаги',
                calories: 'Калории',
                distance: 'Дистанция',
                sleep_hours: 'Сон',
                mood: 'Настроение',
                stress_level: 'Стресс'
            }[field] || field;
            
            html += `
                <div class="trend-item">
                    <span class="trend-name">${fieldName}</span>
                    <span class="trend-value ${className}">${icon} ${trend.slope > 0 ? '+' : ''}${trend.slope}</span>
                </div>
            `;
        }
        html += `</div>`;
    }

    // User Profile (BMI, etc.)
    if (stats.user_profile && Object.keys(stats.user_profile).length > 0) {
        const profile = stats.user_profile;
        html += `
            <h4 style="margin-top: 20px; margin-bottom: 10px;">💪 Ваш профиль</h4>
            <div class="stats-grid-detailed">
        `;
        
        if (profile.bmi) {
            html += `
                <div class="stat-item">
                    <div class="stat-label">BMI</div>
                    <div class="stat-value">${profile.bmi}</div>
                </div>
            `;
        }
        if (profile.weight && profile.target_weight) {
            html += `
                <div class="stat-item">
                    <div class="stat-label">Прогресс веса</div>
                    <div class="stat-value">${profile.weight_progress?.percentage || 0}%</div>
                </div>
            `;
        }
        if (profile.step_goal_achievement) {
            html += `
                <div class="stat-item">
                    <div class="stat-label">Цель по шагам</div>
                    <div class="stat-value">${profile.step_goal_achievement.percentage}%</div>
                </div>
            `;
        }
        if (profile.bmr) {
            html += `
                <div class="stat-item">
                    <div class="stat-label">BMR</div>
                    <div class="stat-value">${Math.round(profile.bmr)}</div>
                </div>
            `;
        }
        html += `</div>`;
    }

    // Insights
    if (stats.insights && stats.insights.length > 0) {
        html += `
            <div class="insights-box">
                <h4>💡 Рекомендации</h4>
                <ul class="insights-list">
        `;
        stats.insights.forEach(insight => {
            html += `<li>${insight}</li>`;
        });
        html += `</ul></div>`;
    }

    statsContent.innerHTML = html;
}