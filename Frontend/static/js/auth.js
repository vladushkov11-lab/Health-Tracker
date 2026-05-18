// API Configuration
const API_GATEWAY_URL = 'http://localhost:8001/api/v1';

// DOM Elements
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // Auth Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            if (tab) {
                switchAuthTab(tab);
            }
        });
    });

    // Forms
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
}

function switchAuthTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.toggle('active', form.id === `${tab}-form`);
    });
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    errorEl.textContent = '';

    try {
        const response = await fetch(`${API_GATEWAY_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка входа');
        }

        // Get user info
        const userResponse = await fetch(`${API_GATEWAY_URL}/me`, {
            credentials: 'include'
        });
        
        const userData = await userResponse.json();
        if (userData.status !== 'error' && userData.user_id) {
            localStorage.setItem('currentUser', JSON.stringify(userData));
        }

        // Перенаправление на дашборд
        window.location.href = '/';
    } catch (error) {
        console.error('Login error:', error);
        errorEl.textContent = error.message || 'Не удалось подключиться к серверу';
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const errorEl = document.getElementById('register-error');
    errorEl.textContent = '';

    const userData = {
        email: document.getElementById('register-email').value,
        password: document.getElementById('register-password').value,
        password_check: document.getElementById('register-password-check').value,
        first_name: document.getElementById('register-firstname').value,
        last_name: document.getElementById('register-lastname').value,
        phone_number: document.getElementById('register-phone').value
    };

    try {
        const response = await fetch(`${API_GATEWAY_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка регистрации');
        }

        alert('Регистрация успешна! Теперь вы можете войти.');
        window.location.href = '/login';
    } catch (error) {
        console.error('Register error:', error);
        errorEl.textContent = error.message || 'Не удалось подключиться к серверу';
    }
}