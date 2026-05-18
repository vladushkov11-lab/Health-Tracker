// API Configuration
const API_GATEWAY_URL = 'http://localhost:8001/api/v1';
const API_GATEWAY_APP_URL = 'http://localhost:8001/app';

// State
let currentUser = null;
let allMetrics = [];
let authChecked = false;

// DOM Elements
const modal = document.getElementById('modal');
const metricForm = document.getElementById('metric-form');

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
            // Неавторизован - перенаправляем на login
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
        loadMetrics();
    }
}

function setupEventListeners() {
    // Logout
    document.getElementById('logout-btn').addEventListener('click', logout);

    // Modal
    document.getElementById('add-metric-btn').addEventListener('click', () => openModal());
    document.getElementById('close-modal').addEventListener('click', closeModal);
    document.getElementById('cancel-btn').addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Form
    metricForm.addEventListener('submit', handleMetricSubmit);
}

function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = '/login';
}

// Metrics Functions
async function loadMetrics() {
    try {
        const response = await fetch(`${API_GATEWAY_APP_URL}/get_metrics`, {
            credentials: 'include'
        });

        if (!response.ok) {
            // Если 401 - перенаправляем на login
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            throw new Error('Ошибка загрузки метрик');
        }

        allMetrics = await response.json();
        renderMetrics();
        updateStats();
    } catch (error) {
        console.error('Error loading metrics:', error);
        if (error.message.includes('401')) {
            window.location.href = '/login';
        }
        allMetrics = [];
        renderMetrics();
    }
}

function renderMetrics() {
    const tbody = document.getElementById('metrics-body');
    const noMetrics = document.getElementById('no-metrics');
    
    tbody.innerHTML = '';

    if (allMetrics.length === 0) {
        noMetrics.style.display = 'block';
        return;
    }

    noMetrics.style.display = 'none';

    allMetrics.forEach(metric => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatDate(metric.date_of_metrics)}</td>
            <td>${metric.steps.toLocaleString()}</td>
            <td>${metric.calories.toLocaleString()}</td>
            <td>${metric.distance} км</td>
            <td>${metric.sleep_hours} ч</td>
            <td>${getMoodEmoji(metric.mood)}</td>
            <td>
                <button class="action-btn edit" onclick="editMetric(${metric.id})">✏️</button>
                <button class="action-btn delete" onclick="deleteMetric(${metric.id})">🗑️</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateStats() {
    if (allMetrics.length === 0) {
        document.getElementById('total-steps').textContent = '0';
        document.getElementById('total-calories').textContent = '0';
        document.getElementById('total-distance').textContent = '0';
        document.getElementById('avg-sleep').textContent = '0';
        return;
    }

    const totalSteps = allMetrics.reduce((sum, m) => sum + m.steps, 0);
    const totalCalories = allMetrics.reduce((sum, m) => sum + m.calories, 0);
    const totalDistance = allMetrics.reduce((sum, m) => sum + m.distance, 0);
    const avgSleep = allMetrics.reduce((sum, m) => sum + m.sleep_hours, 0) / allMetrics.length;

    document.getElementById('total-steps').textContent = totalSteps.toLocaleString();
    document.getElementById('total-calories').textContent = totalCalories.toLocaleString();
    document.getElementById('total-distance').textContent = totalDistance.toFixed(1);
    document.getElementById('avg-sleep').textContent = avgSleep.toFixed(1);
}

async function handleMetricSubmit(e) {
    e.preventDefault();

    const metricData = {
        date_of_metrics: document.getElementById('metric-date').value,
        steps: parseInt(document.getElementById('metric-steps').value),
        calories: parseInt(document.getElementById('metric-calories').value),
        distance: parseFloat(document.getElementById('metric-distance').value),
        sleep_hours: parseInt(document.getElementById('metric-sleep-hours').value),
        sleep_score: parseInt(document.getElementById('metric-sleep-score').value),
        calories_intake: parseInt(document.getElementById('metric-calories-intake').value),
        water_ml: parseInt(document.getElementById('metric-water').value),
        mood: parseInt(document.getElementById('metric-mood').value),
        stress_level: parseInt(document.getElementById('metric-stress').value)
    };

    const metricId = document.getElementById('metric-id').value;
    const url = metricId 
        ? `${API_GATEWAY_APP_URL}/update_metrics?metric_id=${metricId}`
        : `${API_GATEWAY_APP_URL}/create_metrics`;
    
    const method = metricId ? 'PATCH' : 'POST';

    try {
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(metricData)
        });

        if (!response.ok) {
            // Если 401 - перенаправляем на login
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка сохранения метрик');
        }

        closeModal();
        metricForm.reset();
        document.getElementById('metric-id').value = '';
        loadMetrics();
    } catch (error) {
        if (error.message.includes('401')) {
            window.location.href = '/login';
            return;
        }
        alert(error.message);
    }
}

async function deleteMetric(metricId) {
    if (!confirm('Вы уверены, что хотите удалить эту запись?')) return;

    try {
        const response = await fetch(`${API_GATEWAY_APP_URL}/delete_metrics?metric_id=${metricId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (!response.ok) {
            // Если 401 - перенаправляем на login
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка удаления');
        }

        loadMetrics();
    } catch (error) {
        if (error.message.includes('401')) {
            window.location.href = '/login';
            return;
        }
        alert(error.message);
    }
}

// Modal Functions
function openModal(metric = null) {
    if (metric) {
        document.getElementById('modal-title').textContent = 'Редактировать метрики';
        document.getElementById('metric-id').value = metric.id;
        document.getElementById('metric-date').value = metric.date_of_metrics;
        document.getElementById('metric-steps').value = metric.steps;
        document.getElementById('metric-calories').value = metric.calories;
        document.getElementById('metric-distance').value = metric.distance;
        document.getElementById('metric-sleep-hours').value = metric.sleep_hours;
        document.getElementById('metric-sleep-score').value = metric.sleep_score;
        document.getElementById('metric-calories-intake').value = metric.calories_intake;
        document.getElementById('metric-water').value = metric.water_ml;
        document.getElementById('metric-mood').value = metric.mood;
        document.getElementById('metric-stress').value = metric.stress_level;
    } else {
        document.getElementById('modal-title').textContent = 'Добавить метрики';
        document.getElementById('metric-id').value = '';
        document.getElementById('metric-date').value = new Date().toISOString().split('T')[0];
    }
    modal.classList.add('active');
}

function closeModal() {
    modal.classList.remove('active');
    metricForm.reset();
}

// Global Functions
window.editMetric = function(metricId) {
    const metric = allMetrics.find(m => m.id === metricId);
    if (metric) {
        openModal(metric);
    }
};

window.deleteMetric = deleteMetric;

// Helper Functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

function getMoodEmoji(mood) {
    const emojis = ['😢', '😕', '😐', '🙂', '😊', '😁'];
    const index = Math.min(Math.max(mood - 1, 0), 5);
    return emojis[index];
}