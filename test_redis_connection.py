#!/usr/bin/env python3
"""
Скрипт для проверки подключения к Redis из приложения
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_redis_connection():
    """Проверить подключение к Redis"""
    print("=" * 80)
    print("🔍 ПРОВЕРКА ПОДКЛЮЧЕНИЯ К REDIS")
    print("=" * 80)
    print()
    
    # Проверка 1: Прямое подключение через redis-py
    print("1️⃣  Проверка прямого подключения через redis-py...")
    try:
        import redis
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_db = int(os.getenv("REDIS_DB", 0))
        redis_password = os.getenv("REDIS_PASSWORD", None)
        
        # Подключаемся с паролем только если он указан и Redis требует его
        # Пробуем подключиться сначала без пароля, потом с паролем
        r = None
        connection_method = None
        
        try:
            # Пробуем без пароля
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=None,
                decode_responses=True,
                socket_connect_timeout=5
            )
            result = r.ping()
            if result:
                connection_method = "без пароля"
        except redis.AuthenticationError:
            # Если требуется пароль, пробуем с паролем
            if redis_password:
                try:
                    r = redis.Redis(
                        host=redis_host,
                        port=redis_port,
                        db=redis_db,
                        password=redis_password,
                        decode_responses=True,
                        socket_connect_timeout=5
                    )
                    result = r.ping()
                    if result:
                        connection_method = "с паролем"
                except Exception as e:
                    print(f"   ❌ Ошибка подключения с паролем: {e}")
                    return False
            else:
                print("   ❌ Redis требует пароль, но REDIS_PASSWORD не указан в .env")
                return False
        except Exception as e:
            print(f"   ❌ Ошибка подключения: {e}")
            return False
        
        if r and connection_method:
            print(f"   ✅ Redis доступен: {redis_host}:{redis_port} (DB {redis_db}) - подключение {connection_method}")
        else:
            print("   ❌ Redis не отвечает на ping")
            return False
        
        # Тест записи/чтения
        test_key = "test_connection_key"
        test_value = "test_value_123"
        r.set(test_key, test_value, ex=10)
        retrieved = r.get(test_key)
        
        if retrieved == test_value:
            print("   ✅ Запись и чтение работают корректно")
            r.delete(test_key)
        else:
            print(f"   ❌ Ошибка: записали '{test_value}', получили '{retrieved}'")
            return False
        
        # Информация о Redis
        info = r.info('server')
        print(f"   ℹ️  Версия Redis: {info.get('redis_version', 'unknown')}")
        print(f"   ℹ️  Используемая память: {info.get('used_memory_human', 'unknown')}")
        
    except ImportError:
        print("   ❌ Модуль redis не установлен")
        print("   💡 Установите: pip install redis")
        return False
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
        return False
    
    print()
    
    # Проверка 2: Подключение через Flask-Caching
    print("2️⃣  Проверка подключения через Flask-Caching...")
    try:
        from flask import Flask
        from modules.core import init_app, get_cache
        
        app = Flask(__name__)
        init_app(app)
        
        with app.app_context():
            cache = get_cache()
            
            # Проверяем тип кэша
            cache_type = app.config.get('CACHE_TYPE', 'null')
            print(f"   ℹ️  Тип кэша: {cache_type}")
            
            if cache_type == 'RedisCache':
                # Тест записи/чтения через Flask-Caching
                test_key = "flask_cache_test"
                test_value = "flask_test_value_456"
                
                cache.set(test_key, test_value, timeout=10)
                retrieved = cache.get(test_key)
                
                if retrieved == test_value:
                    print("   ✅ Flask-Caching работает корректно с Redis")
                    cache.delete(test_key)
                else:
                    print(f"   ❌ Ошибка Flask-Caching: записали '{test_value}', получили '{retrieved}'")
                    return False
            elif cache_type == 'FileSystemCache':
                print("   ⚠️  Используется FileSystemCache вместо Redis")
                print("   💡 Проверьте CACHE_TYPE в .env (должно быть 'redis')")
            else:
                print("   ⚠️  Кэширование отключено (null cache)")
                print("   💡 Установите CACHE_TYPE=redis в .env")
        
    except Exception as e:
        print(f"   ❌ Ошибка Flask-Caching: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 80)
    print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
    print("=" * 80)
    return True

if __name__ == '__main__':
    success = test_redis_connection()
    sys.exit(0 if success else 1)

