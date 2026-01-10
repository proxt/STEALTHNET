#!/usr/bin/env python3
"""
Скрипт для сброса пароля пользователя
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

def reset_password(email, new_password):
    """Сбросить пароль пользователя"""
    from flask import Flask
    from modules.core import init_app, get_db, get_bcrypt
    
    app = Flask(__name__)
    init_app(app)
    
    with app.app_context():
        # Импортируем модели после инициализации приложения
        from modules.models.user import User
        
        db = get_db()
        bcrypt = get_bcrypt()
        
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"❌ Пользователь с email {email} не найден")
            return False
        
        # Хешируем новый пароль
        password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password_hash = password_hash
        user.is_verified = True  # Убедимся, что пользователь верифицирован
        
        db.session.commit()
        
        print(f"✅ Пароль для {email} успешно изменен")
        print(f"   Новый пароль: {new_password}")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Использование: python3 reset_user_password.py <email> <новый_пароль>")
        print("Пример: python3 reset_user_password.py admin@stealthnet.app mypassword123")
        sys.exit(1)
    
    email = sys.argv[1]
    new_password = sys.argv[2]
    
    success = reset_password(email, new_password)
    sys.exit(0 if success else 1)

