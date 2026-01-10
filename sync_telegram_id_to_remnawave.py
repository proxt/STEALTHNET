#!/usr/bin/env python3
"""
Скрипт для синхронизации telegramId в RemnaWave для всех пользователей
Использование: python3 sync_telegram_id_to_remnawave.py [user_id]
Если user_id не указан, синхронизирует всех пользователей с telegram_id
"""

import sys
import os
from dotenv import load_dotenv
import requests

# Загружаем переменные окружения
load_dotenv()

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from modules.core import get_db
from modules.models.user import User

def sync_telegram_id(user_id=None):
    """Синхронизировать telegramId в RemnaWave"""
    with app.app_context():
        db = get_db()
        
        API_URL = os.getenv('API_URL')
        ADMIN_TOKEN = os.getenv('ADMIN_TOKEN')
        
        if not API_URL or not ADMIN_TOKEN:
            print("❌ API_URL или ADMIN_TOKEN не настроены")
            return
        
        if user_id:
            # Синхронизируем конкретного пользователя
            user = User.query.get(user_id)
            if not user:
                print(f"❌ Пользователь с ID {user_id} не найден")
                return
            
            users = [user]
        else:
            # Синхронизируем всех пользователей с telegram_id
            users = User.query.filter(
                User.telegram_id.isnot(None),
                User.remnawave_uuid.isnot(None)
            ).all()
        
        synced = 0
        failed = 0
        
        for user in users:
            if not user.remnawave_uuid:
                print(f"⚠️  Пользователь {user.id} ({user.email}) не имеет remnawave_uuid, пропускаем")
                continue
            
            try:
                headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
                response = requests.patch(
                    f"{API_URL}/api/users",
                    headers=headers,
                    json={"uuid": user.remnawave_uuid, "telegramId": str(user.telegram_id) if user.telegram_id else None},
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"✅ Синхронизирован пользователь {user.id} ({user.email}): telegramId = {user.telegram_id}")
                    synced += 1
                else:
                    print(f"❌ Ошибка для пользователя {user.id} ({user.email}): {response.status_code} - {response.text[:100]}")
                    failed += 1
            except Exception as e:
                print(f"❌ Ошибка для пользователя {user.id} ({user.email}): {e}")
                failed += 1
        
        print(f"\n✅ Синхронизировано: {synced}")
        if failed > 0:
            print(f"❌ Ошибок: {failed}")

if __name__ == '__main__':
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    sync_telegram_id(user_id)


