// API Configuration
const API_GATEWAY_URL = 'http://localhost:8001/api/v1';
const API_GATEWAY_APP_URL = 'http://localhost:8001/app';

// State
let currentUser = null;
let metricChart = null;
let authChecked = false;

// Get metric type from URL
const urlPath = window.location.pathname;
const metricType = urlPath.split('/').pop();

const metricTitles = {
    'steps': '👣 Статистика по шагам',
    'calories': '🔥 Статистика по калориям',
    'distance': '📏 Статистика по дистанции',
    'sleep': '😴 Статистика по сну',
    'mood': '😊 Статистика по настроению',
    'stress': '😰 Статистика по стрессу',
    'water': '💧 Статистика по воде',
    'calories_intake': '🍽️ Статистика по калориям в пище'
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    
    const title = metricTitles[metricType] || `Статистика по ${metricType}`;
    document.getElementById('metric-title').textContent = title;
    
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
        document.getElementById('user-name').textContent = userData?.first_name || 'Пользователь';
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
        loadMetricStats();
    }
}

function setupEventListeners() {
    document.getElementById('logout-btn').addEventListener('click', logout);
    document.getElementById('days-select').addEventListener('change', () => loadMetricStats());
}

function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = '/login';
}

async function loadMetricStats() {
    const days = document.getElementById('days-select').value;
    
    try {
        const response = await fetch(`${API_GATEWAY_APP_URL}/stats/metric/${metricType}?days=${days}`, {
            credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            throw new Error('Ошибка загрузки статистики');
        }

        const data = await response.json();
        renderChart(data.chart_data);
        renderStats(data.metric_stats);
    } catch (error) {
        console.error('Error loading metric stats:', error);
        if (error.message.includes('401')) {
            window.location.href = '/login';
        }
        alert(error.message);
    }
}

function renderChart(chartData) {
    const ctx = document.getElementById('metric-chart').getContext('2d');
    
    if (metricChart) {
        metricChart.destroy();
    }
    
    const metricName = metricTitles[metricType]?.split(' ')[1] || metricType;
    
    metricChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: metricName,
                data: chartData.values,
                borderColor: 'rgb(99, 102, 241)',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function renderStats(stats) {
    const statsContainer = document.getElementById('metric-stats');
    
    const trendIcons = {
        'up': '📈',
        'down': '📉',
        'stable': '➡️'
    };
    
    const trendText = {
        'up': 'Рост',
        'down': 'Падение',
        'stable': 'Стабильно'
    };
    
    statsContainer.innerHTML = `
        <div class="stat-item">
            <div class="stat-label">Всего записей</div>
            <div class="stat-value">${stats.count}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Минимум</div>
            <div class="stat-value">${stats.min}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Максимум</div>
            <div class="stat-value">${stats.max}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Среднее</div>
            <div class="stat-value">${stats.average}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Всего</div>
            <div class="stat-value">${stats.total}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Последнее значение</div>
            <div class="stat-value">${stats.last_value || 0}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Тренд</div>
            <div class="stat-value">${trendIcons[stats.trend] || ''} ${trendText[stats.trend] || '-'}</div>
        </div>
    `;
}