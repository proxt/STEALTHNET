#!/usr/bin/env python3
"""
Скрипт для восстановления encrypted_password для существующих пользователей из бота
Если у пользователя есть password_hash, но нет encrypted_password, 
и email начинается с "tg_", генерируем новый пароль и сохраняем его
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

def fix_encrypted_passwords(app=None):
    """
    Восстановить encrypted_password для пользователей из бота
    
    Args:
        app: Flask приложение (опционально, если None - создаст временное)
    
    Returns:
        bool: True если успешно
    """
    from flask import Flask
    from modules.core import init_app, get_db, get_fernet
    import secrets
    
    use_temp_app = app is None
    if use_temp_app:
        app = Flask(__name__)
        init_app(app)
    
    with app.app_context():
        from modules.models.user import User
        
        db = get_db()
        fernet = get_fernet()
        
        if not fernet:
            print("❌ FERNET_KEY не настроен, невозможно зашифровать пароли")
            return False
        
        # Находим пользователей из бота (email начинается с "tg_")
        # у которых есть password_hash, но нет encrypted_password
        users = User.query.filter(
            User.email.like('tg_%@telegram.local'),
            User.password_hash != None,
            User.password_hash != '',
            (User.encrypted_password == None) | (User.encrypted_password == '')
        ).all()
        
        if not users:
            print("✅ Нет пользователей, требующих исправления")
            return True
        
        print(f"Найдено {len(users)} пользователей для исправления")
        
        fixed_count = 0
        for user in users:
            try:
                # Генерируем новый пароль (12 символов)
                new_password = secrets.token_urlsafe(12)
                
                # Хешируем пароль (если еще не хеширован)
                from modules.core import get_bcrypt
                bcrypt = get_bcrypt()
                if not user.password_hash or user.password_hash == '':
                    user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
                
                # Шифруем пароль для старого бота
                user.encrypted_password = fernet.encrypt(new_password.encode()).decode()
                
                db.session.commit()
                fixed_count += 1
                print(f"✅ Исправлен пользователь {user.email} (ID: {user.id})")
            except Exception as e:
                print(f"❌ Ошибка при исправлении пользователя {user.email}: {e}")
                db.session.rollback()
        
        print(f"\n✅ Исправлено {fixed_count} из {len(users)} пользователей")
        return True

if __name__ == '__main__':
    try:
        fix_encrypted_passwords()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


