#!/usr/bin/env python3
"""
Скрипт для автоматической рассылки уведомлений в Telegram боты
Проверяет пользователей с истекающими подписками и триалами
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import requests

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def get_user_subscription_info(remnawave_uuid):
    """Получить информацию о подписке пользователя из RemnaWave API"""
    try:
        api_url = os.getenv("API_URL")
        admin_token = os.getenv("ADMIN_TOKEN")
        
        if not api_url or not admin_token:
            return None
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{api_url}/api/users/{remnawave_uuid}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            user_data = data.get('response', {})
            return user_data
        return None
    except Exception as e:
        print(f"Error getting user info for {remnawave_uuid}: {e}")
        return None

def parse_iso_datetime(iso_string):
    """Парсинг ISO datetime строки"""
    if not iso_string:
        return None
    try:
        # Убираем микросекунды если есть
        if '.' in iso_string:
            iso_string = iso_string.split('.')[0] + 'Z'
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    except:
        return None

def send_telegram_message(bot_token, chat_id, text, photo_file=None):
    """Отправить сообщение в Telegram"""
    try:
        if photo_file:
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            caption = text[:1024] if len(text) > 1024 else text
            files = {'photo': photo_file}
            data = {
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": "HTML"
            }
            response = requests.post(url, files=files, data=data, timeout=30)
        else:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return True, result.get('result', {}).get('message_id')
        else:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('description', f'HTTP {response.status_code}')
            return False, error_msg
    except Exception as e:
        return False, str(e)

def send_auto_broadcasts():
    """Отправить автоматические рассылки"""
    from flask import Flask
    from modules.core import init_app, get_db
    from modules.models.user import User
    from modules.models.auto_broadcast import AutoBroadcastMessage
    
    app = Flask(__name__)
    init_app(app)
    
    with app.app_context():
        db = get_db()
        
        # Получаем настройки автоматических рассылок
        subscription_msg = AutoBroadcastMessage.query.filter_by(
            message_type='subscription_expiring_3days'
        ).first()
        
        trial_msg = AutoBroadcastMessage.query.filter_by(
            message_type='trial_expiring'
        ).first()
        
        # Получаем токены ботов
        old_bot_token = os.getenv("CLIENT_BOT_TOKEN")
        new_bot_token = os.getenv("CLIENT_BOT_V2_TOKEN") or os.getenv("CLIENT_BOT_TOKEN")
        
        if not old_bot_token and not new_bot_token:
            print("❌ Bot tokens not configured")
            return False
        
        # Текущая дата
        now = datetime.now(timezone.utc)
        three_days_later = now + timedelta(days=3)
        
        # Получаем всех пользователей с telegram_id и remnawave_uuid
        users = User.query.filter(
            User.telegram_id != None,
            User.telegram_id != '',
            User.remnawave_uuid != None,
            User.remnawave_uuid != ''
        ).all()
        
        subscription_sent = 0
        subscription_failed = 0
        trial_sent = 0
        trial_failed = 0
        
        print(f"Проверяем {len(users)} пользователей...")
        
        for user in users:
            try:
                # Получаем информацию о подписке
                user_info = get_user_subscription_info(user.remnawave_uuid)
                if not user_info:
                    continue
                
                expire_at_str = user_info.get('expireAt')
                if not expire_at_str:
                    continue
                
                expire_at = parse_iso_datetime(expire_at_str)
                if not expire_at:
                    continue
                
                # Проверяем, истекает ли подписка через 3 дня
                days_until_expiry = (expire_at - now).days
                
                # Проверяем подписку, истекающую через 3 дня
                # Отправляем за 3 дня до окончания
                is_subscription_expiring = (
                    days_until_expiry == 3 and 
                    expire_at > now and 
                    expire_at <= three_days_later
                )
                
                # Проверяем триал, который заканчивается сегодня или завтра
                # Триал обычно 3 дня, поэтому если осталось 0-1 день - это триал
                is_trial_expiring = (
                    days_until_expiry <= 1 and
                    expire_at > now and
                    expire_at <= (now + timedelta(days=1))
                )
                
                # Отправляем уведомление о подписке
                if is_subscription_expiring and subscription_msg and subscription_msg.enabled:
                    message_text = subscription_msg.message_text
                    bot_type = subscription_msg.bot_type
                    
                    # Выбираем токен бота
                    bot_token = None
                    if bot_type == 'old' or bot_type == 'both':
                        bot_token = old_bot_token
                    elif bot_type == 'new':
                        bot_token = new_bot_token
                    
                    if bot_token:
                        success, result = send_telegram_message(bot_token, user.telegram_id, message_text)
                        if success:
                            subscription_sent += 1
                            print(f"✅ Отправлено уведомление о подписке пользователю {user.email} (ID: {user.telegram_id})")
                        else:
                            subscription_failed += 1
                            print(f"❌ Ошибка отправки подписки пользователю {user.email}: {result}")
                
                # Отправляем уведомление о триале
                if is_trial_expiring and trial_msg and trial_msg.enabled:
                    message_text = trial_msg.message_text
                    bot_type = trial_msg.bot_type
                    
                    # Выбираем токен бота
                    bot_token = None
                    if bot_type == 'old' or bot_type == 'both':
                        bot_token = old_bot_token
                    elif bot_type == 'new':
                        bot_token = new_bot_token
                    
                    if bot_token:
                        success, result = send_telegram_message(bot_token, user.telegram_id, message_text)
                        if success:
                            trial_sent += 1
                            print(f"✅ Отправлено уведомление о триале пользователю {user.email} (ID: {user.telegram_id})")
                        else:
                            trial_failed += 1
                            print(f"❌ Ошибка отправки триала пользователю {user.email}: {result}")
            
            except Exception as e:
                print(f"❌ Ошибка обработки пользователя {user.email}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print()
        print("=" * 80)
        print("✅ АВТОМАТИЧЕСКАЯ РАССЫЛКА ЗАВЕРШЕНА")
        print(f"   Подписка: отправлено {subscription_sent}, ошибок {subscription_failed}")
        print(f"   Триал: отправлено {trial_sent}, ошибок {trial_failed}")
        print("=" * 80)
        
        return True

if __name__ == '__main__':
    try:
        send_auto_broadcasts()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

