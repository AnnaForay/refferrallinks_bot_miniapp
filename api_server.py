from flask import Flask, jsonify
from flask_cors import CORS
import asyncio
import os
from database.connection import db
from database.models import get_all_categories

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для Mini App

# Инициализация базы данных
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(db.connect())

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Получить список активных категорий"""
    try:
        categories = loop.run_until_complete(get_all_categories(only_active=True))
        
        result = [
            {
                'id': cat['id'],
                'name': cat['name'],
                'emoji': cat['emoji']
            }
            for cat in categories
        ]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Проверка работоспособности API"""
    return jsonify({'status': 'ok'}), 200

@app.route('/')
def index():
    """Главная страница API"""
    return jsonify({
        'message': 'Referral Links Bot API',
        'version': '1.0',
        'endpoints': ['/api/categories', '/api/health']
    }), 200

if __name__ == '__main__':
    # Для Render нужен порт из переменной окружения
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
