// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// Данные пользователя
const user = tg.initDataUnsafe?.user;
const userId = user?.id;

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
        // Запрашиваем категории через initData (безопасно)
        const categories = await fetchCategories();
        
        categorySelect.innerHTML = '<option value="">Выбери категорию</option>';
        
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = `${cat.emoji} ${cat.name}`;
            categorySelect.appendChild(option);
        });
    } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
        showError('Не удалось загрузить категории. Попробуй позже.');
    }
}

// Функция получения категорий из бота
async function fetchCategories() {
    // Здесь будет запрос к боту через Telegram Bot API
    // Пока что возвращаем тестовые данные
    // После настройки бэкенда заменишь на реальный запрос
    
    return [
        { id: 1, emoji: '💰', name: 'Финансы' },
        { id: 2, emoji: '🎮', name: 'Игры' },
        { id: 3, emoji: '🛍️', name: 'Шоппинг' }
    ];
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
        category_id: parseInt(categorySelect.value),
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

// Настройка главной кнопки (необязательно, можно использовать обычную кнопку формы)
tg.MainButton.setText('Отправить на модерацию');
tg.MainButton.onClick(() => {
    form.requestSubmit();
});
