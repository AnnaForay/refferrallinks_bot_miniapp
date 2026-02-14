// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// Данные пользователя
const user = tg.initDataUnsafe?.user;
const userId = user?.id;

// Элементы формы
const form = document.getElementById('categoryForm');
const nameInput = document.getElementById('name');
const emojiInput = document.getElementById('emoji');
const successDiv = document.getElementById('success');
const errorDiv = document.getElementById('error');
const errorText = document.getElementById('errorText');

// Отправка формы
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = form.querySelector('.btn-submit');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Добавление...';
    
    // Валидация
    if (!nameInput.value.trim()) {
        showError('Введи название категории!');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Добавить категорию';
        return;
    }
    
    if (!emojiInput.value.trim()) {
        showError('Выбери эмодзи для категории!');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Добавить категорию';
        return;
    }
    
    // Формируем данные для отправки
    const categoryData = {
        action: 'add_category',
        user_id: userId,
        name: nameInput.value.trim(),
        emoji: emojiInput.value.trim()
    };
    
    try {
        // Отправляем данные в бота через Telegram WebApp API
        tg.sendData(JSON.stringify(categoryData));
        
        // Показываем успех
        showSuccess();
        
        // Закрываем Mini App через 2 секунды
        setTimeout(() => {
            tg.close();
        }, 2000);
    } catch (error) {
        console.error('Ошибка отправки:', error);
        showError('Не удалось добавить категорию. Попробуй снова.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Добавить категорию';
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

// Настройка кнопки "Назад" в Telegram
tg.BackButton.show();
tg.BackButton.onClick(() => {
    tg.close();
});
