// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

const API_URL = 'https://refferrallinks-bot-miniapp.onrender.com';

// Данные пользователя
const user = tg.initDataUnsafe?.user;
const userId = user?.id;
const initData = tg.initData;

// Элементы формы
const form = document.getElementById('linkForm');
const categorySelect = document.getElementById('category');
const nameInput = document.getElementById('name');
const urlInput = document.getElementById('url');
const descriptionInput = document.getElementById('description');
const successDiv = document.getElementById('success');
const errorDiv = document.getElementById('error');
const errorText = document.getElementById('errorText');

// Загрузка категорий при открытии
async function loadCategories() {
    try {
        // Запрос к Flask API за категориями
        const response = await fetch(`${API_URL}/api/categories`);
        const categories = await response.json();
        
        categorySelect.innerHTML = '';
        
        // Добавляем категории из API
        if (categories && categories.length > 0) {
            categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = `${cat.emoji} ${cat.name}`;
                categorySelect.appendChild(option);
            });
        }
        
        // ВСЕГДА добавляем "Затрудняюсь в выборе"
        const undecidedOption = document.createElement('option');
        undecidedOption.value = 0;
        undecidedOption.textContent = '❓ Затрудняюсь в выборе';
        categorySelect.appendChild(undecidedOption);
        
    } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
        
        // Если не удалось загрузить, показываем только "Затрудняюсь"
        categorySelect.innerHTML = '';
        const undecidedOption = document.createElement('option');
        undecidedOption.value = 0;
        undecidedOption.textContent = '❓ Затрудняюсь в выборе';
        categorySelect.appendChild(undecidedOption);
    }
}

// Функция получения категорий через WebApp
async function fetchCategoriesFromBot() {
    try {
        // Используем CloudStorage для временного хранения или запрос через initData
        // Простой вариант: отправляем запрос боту через специальную команду
        
        // Пока возвращаем пустой массив - категории загрузятся при первом использовании
        // После того как бот настроим, здесь будет реальный запрос
        
        return [];
        
    } catch (error) {
        console.error('Ошибка запроса категорий:', error);
        return [];
    }
}

// Отправка формы
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = form.querySelector('.btn-submit');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Отправка...';
    
    // Валидация
    if (!categorySelect.value) {
        showError('Выбери категорию!');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Отправить на модерацию';
        return;
    }
    
    if (!nameInput.value.trim()) {
        showError('Введи название ссылки!');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Отправить на модерацию';
        return;
    }
    
    if (!urlInput.value.trim().startsWith('http')) {
        showError('URL должен начинаться с http:// или https://');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Отправить на модерацию';
        return;
    }
    
    // Формируем данные для отправки
    const linkData = {
        action: 'submit_link',
        user_id: userId,
        category_id: parseInt(categorySelect.value) || 0,
        name: nameInput.value.trim(),
        url: urlInput.value.trim(),
        description: descriptionInput.value.trim() || null
    };
    
    try {
        // Отправляем данные в бота через Telegram WebApp API
        tg.sendData(JSON.stringify(linkData));
        
        // Показываем успех
        showSuccess();
        
        // Закрываем Mini App через 2 секунды
        setTimeout(() => {
            tg.close();
        }, 2000);
    } catch (error) {
        console.error('Ошибка отправки:', error);
        showError('Не удалось отправить ссылку. Попробуй снова.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Отправить на модерацию';
    }
});

function showSuccess() {
    form.style.display = 'none';
    successDiv.style.display = 'block';
}

function showError(message) {
    errorText.textContent = message;
    errorDiv.style.display = 'block';
    
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Загружаем категории при загрузке страницы
loadCategories();

// Настройка кнопки "Назад" в Telegram
tg.BackButton.show();
tg.BackButton.onClick(() => {
    tg.close();
});


