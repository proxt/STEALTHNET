#!/usr/bin/env python3
"""
Тестирование логики работы с базами данных
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_database_logic():
    """Тестирование логики выбора базы данных"""
    
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ЛОГИКИ БАЗ ДАННЫХ")
    print("=" * 80)
    print()
    
    # Проверяем наличие SQLite баз
    instance_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'stealthnet.db')
    root_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stealthnet.db')
    
    print("📁 Проверка SQLite баз:")
    print(f"   instance/stealthnet.db: {'✅ существует' if os.path.exists(instance_db) else '❌ не найдена'}")
    print(f"   stealthnet.db (корень): {'✅ существует' if os.path.exists(root_db) else '❌ не найдена'}")
    print()
    
    # Проверяем настройки PostgreSQL
    database_url = os.getenv("DATABASE_URL")
    db_type = os.getenv("DB_TYPE", "").lower()
    
    print("📁 Проверка настроек PostgreSQL:")
    if database_url:
        print(f"   DATABASE_URL: {'✅ установлен' if database_url else '❌ не установлен'}")
        # Проверяем доступность PostgreSQL
        try:
            from sqlalchemy import create_engine, text
            test_engine = create_engine(database_url, connect_args={"connect_timeout": 2})
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("   PostgreSQL: ✅ доступен")
            use_postgresql = True
        except Exception as e:
            print(f"   PostgreSQL: ❌ недоступен ({str(e)[:100]})")
            use_postgresql = False
    elif db_type in ["postgresql", "postgres"]:
        print(f"   DB_TYPE: {db_type}")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "stealthnet")
        db_user = os.getenv("DB_USER", "stealthnet")
        db_password = os.getenv("DB_PASSWORD", "")
        
        if db_password:
            test_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            test_url = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
        
        try:
            from sqlalchemy import create_engine, text
            test_engine = create_engine(test_url, connect_args={"connect_timeout": 2})
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"   PostgreSQL: ✅ доступен ({db_host}:{db_port}/{db_name})")
            use_postgresql = True
        except Exception as e:
            print(f"   PostgreSQL: ❌ недоступен ({str(e)[:100]})")
            use_postgresql = False
    else:
        print("   PostgreSQL: ⚠️  не настроен")
        use_postgresql = False
    
    print()
    print("=" * 80)
    print("ЛОГИКА РАБОТЫ:")
    print("=" * 80)
    
    # Определяем SQLite базу
    sqlite_path = None
    if os.path.exists(instance_db):
        sqlite_path = instance_db
        print(f"✅ Найдена SQLite база: instance/stealthnet.db")
    elif os.path.exists(root_db):
        sqlite_path = root_db
        print(f"✅ Найдена SQLite база: stealthnet.db (корень)")
    else:
        print("❌ SQLite база не найдена")
    
    print()
    
    # Логика выбора базы данных
    if use_postgresql:
        print("✅ Используется PostgreSQL")
        if sqlite_path:
            print("   → Будет выполнена миграция из SQLite в PostgreSQL")
        else:
            print("   → Будет создана новая база данных в PostgreSQL")
    else:
        print("✅ Используется SQLite")
        if sqlite_path:
            print(f"   → Будет использована существующая база: {sqlite_path}")
        else:
            print("   → Будет создана новая база: stealthnet.db")
    
    print()
    print("=" * 80)
    
    return use_postgresql, sqlite_path

if __name__ == '__main__':
    test_database_logic()

