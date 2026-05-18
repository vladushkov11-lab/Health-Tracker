// API Configuration
const API_GATEWAY_URL = 'http://localhost:8001/api/v1';
const API_GATEWAY_APP_URL = 'http://localhost:8001/app';

// State
let currentUser = null;
let mainChart = null;
let authChecked = false;

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
        loadStats();
    }
}

function setupEventListeners() {
    document.getElementById('logout-btn').addEventListener('click', logout);
    document.getElementById('days-select').addEventListener('change', () => loadStats());
}

function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = '/login';
}

async function loadStats() {
    const days = document.getElementById('days-select').value;
    
    try {
        const response = await fetch(`${API_GATEWAY_APP_URL}/stats/detail?days=${days}`, {
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
        renderInsights(data.stats);
    } catch (error) {
        console.error('Error loading stats:', error);
        if (error.message.includes('401')) {
            window.location.href = '/login';
        }
        alert(error.message);
    }
}

function renderChart(chartData) {
    const ctx = document.getElementById('main-chart').getContext('2d');
    
    if (mainChart) {
        mainChart.destroy();
    }
    
    mainChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Шаги',
                    data: chartData.datasets.steps,
                    borderColor: 'rgb(99, 102, 241)',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4
                },
                {
                    label: 'Калории',
                    data: chartData.datasets.calories,
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4
                },
                {
                    label: 'Дистанция (км)',
                    data: chartData.datasets.distance,
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left'
                }
            }
        }
    });
}

function renderInsights(stats) {
    const insightsList = document.getElementById('insights-list');
    
    if (stats.insights && stats.insights.length > 0) {
        insightsList.innerHTML = stats.insights.map(insight => `<li>${insight}</li>`).join('');
    } else {
        insightsList.innerHTML = '<li>Нет данных для анализа</li>';
    }
}