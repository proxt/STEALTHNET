#!/usr/bin/env python3
"""
StealthNET - Система диагностики проекта
Простая как АК-47
"""

import os
import sys
import json
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_ok(text):
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.RESET} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {text}")

def check_files():
    """Проверка наличия основных файлов"""
    print_header("ПРОВЕРКА ФАЙЛОВ")

    critical_files = [
        ('main.py', 'Основной файл приложения'),
        ('app.py', 'Оригинальный монолит (backup)'),
        ('client_bot.py', 'Telegram бот'),
        ('.env', 'Конфигурация'),
        ('requirements.txt', 'Зависимости API'),
        ('client_bot_requirements.txt', 'Зависимости бота'),
        ('stealthnet.db', 'База данных'),
    ]

    ok_count = 0
    for file, desc in critical_files:
        path = f"/opt/admin/{file}"
        if os.path.exists(path):
            size = os.path.getsize(path)
            size_str = f"{size:,} байт" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
            print_ok(f"{desc}: {file} ({size_str})")
            ok_count += 1
        else:
            print_error(f"{desc}: {file} НЕ НАЙДЕН")

    return ok_count == len(critical_files)

def check_modules():
    """Проверка модулей"""
    print_header("ПРОВЕРКА МОДУЛЕЙ")

    modules_dir = "/opt/admin/modules"
    if not os.path.exists(modules_dir):
        print_error("Директория modules/ не найдена!")
        return False

    # Основные модули
    core_modules = [
        'core.py', 'auth.py', 'user.py', 'payment.py',
        'promo.py', 'tariff.py', 'system.py', 'referral.py'
    ]

    ok_count = 0
    for module in core_modules:
        path = f"{modules_dir}/{module}"
        if os.path.exists(path):
            print_ok(f"Модуль: {module}")
            ok_count += 1
        else:
            print_error(f"Модуль: {module} НЕ НАЙДЕН")

    # Эндпоинты
    endpoints_dir = f"{modules_dir}/endpoints"
    if os.path.exists(endpoints_dir):
        endpoint_files = [f for f in os.listdir(endpoints_dir) if f.endswith('.py')]
        print_ok(f"Эндпоинты: {len(endpoint_files)} файлов")
    else:
        print_error("Директория endpoints/ не найдена!")
        return False

    return ok_count == len(core_modules)

def check_app_loading():
    """Проверка загрузки приложения"""
    print_header("ПРОВЕРКА ЗАГРУЗКИ ПРИЛОЖЕНИЯ")

    try:
        sys.path.insert(0, '/opt/admin')
        from app import app
        print_ok("app.py загружен успешно")

        # Подсчет эндпоинтов
        rules = [r for r in app.url_map.iter_rules() if r.endpoint != 'static']
        print_ok(f"Эндпоинтов зарегистрировано: {len(rules)}")

        # Группировка
        categories = {
            'admin': 0, 'client': 0, 'webhook': 0,
            'public': 0, 'miniapp': 0, 'bot': 0, 'other': 0
        }

        for rule in rules:
            path = rule.rule
            if '/api/admin/' in path:
                categories['admin'] += 1
            elif '/api/client/' in path:
                categories['client'] += 1
            elif '/api/webhook/' in path:
                categories['webhook'] += 1
            elif '/api/public/' in path:
                categories['public'] += 1
            elif '/miniapp/' in path:
                categories['miniapp'] += 1
            elif '/api/bot/' in path:
                categories['bot'] += 1
            else:
                categories['other'] += 1

        print_info("Распределение эндпоинтов:")
        for cat, count in categories.items():
            if count > 0:
                print(f"  • {cat.upper()}: {count}")

        return True
    except Exception as e:
        print_error(f"Ошибка загрузки: {e}")
        return False

def check_env():
    """Проверка переменных окружения"""
    print_header("ПРОВЕРКА КОНФИГУРАЦИИ")

    try:
        from dotenv import load_dotenv
        load_dotenv('/opt/admin/.env')

        critical_vars = [
            'JWT_SECRET_KEY',
            'API_URL',
            'ADMIN_TOKEN',
            'CLIENT_BOT_TOKEN',
            'SQLALCHEMY_DATABASE_URI',
            'FERNET_KEY',
        ]

        ok_count = 0
        for var in critical_vars:
            value = os.getenv(var)
            if value:
                # Маскируем секреты
                if 'TOKEN' in var or 'KEY' in var or 'PASSWORD' in var:
                    display = f"{value[:10]}...***"
                else:
                    display = value[:50]
                print_ok(f"{var}: {display}")
                ok_count += 1
            else:
                print_error(f"{var}: НЕ УСТАНОВЛЕН")

        return ok_count == len(critical_vars)
    except Exception as e:
        print_error(f"Ошибка чтения .env: {e}")
        return False

def check_database():
    """Проверка базы данных"""
    print_header("ПРОВЕРКА БАЗЫ ДАННЫХ")

    db_path = "/opt/admin/stealthnet.db"
    if not os.path.exists(db_path):
        print_error("База данных не найдена!")
        return False

    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        print_ok(f"База данных найдена: {os.path.getsize(db_path):,} байт")
        print_info(f"Таблиц в БД: {len(tables)}")

        # Проверяем критические таблицы
        critical_tables = ['user', 'payment', 'tariff', 'promo_code']
        for table_name in critical_tables:
            if any(table_name in t[0].lower() for t in tables):
                cursor.execute(f"SELECT COUNT(*) FROM {[t[0] for t in tables if table_name in t[0].lower()][0]}")
                count = cursor.fetchone()[0]
                print_ok(f"Таблица '{table_name}': {count} записей")
            else:
                print_warning(f"Таблица '{table_name}': не найдена")

        conn.close()
        return True
    except Exception as e:
        print_error(f"Ошибка проверки БД: {e}")
        return False

def check_bot():
    """Проверка бота"""
    print_header("ПРОВЕРКА TELEGRAM БОТА")

    try:
        sys.path.insert(0, '/opt/admin')
        import client_bot
        print_ok("client_bot.py загружен успешно")

        # Проверяем размер
        size = os.path.getsize('/opt/admin/client_bot.py')
        lines = len(open('/opt/admin/client_bot.py').readlines())
        print_info(f"Размер: {size:,} байт, {lines} строк кода")

        return True
    except Exception as e:
        print_error(f"Ошибка загрузки бота: {e}")
        return False

def compare_with_monolith():
    """Сравнение с монолитом"""
    print_header("СРАВНЕНИЕ С МОНОЛИТОМ")

    try:
        # Подсчет роутов в app.py
        with open('/opt/admin/app.py', 'r') as f:
            app_content = f.read()
            monolith_routes = app_content.count('@app.route')

        # Подсчет роутов в модулях
        module_routes = 0
        for root, dirs, files in os.walk('/opt/admin/modules'):
            for file in files:
                if file.endswith('.py'):
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        module_routes += content.count('@app.route')

        print_info(f"Монолит (app.py): {monolith_routes} роутов")
        print_info(f"Модульная система: {module_routes} роутов")

        if module_routes >= monolith_routes:
            print_ok(f"Миграция завершена! (+{module_routes - monolith_routes} новых эндпоинтов)")
        else:
            print_warning(f"Не хватает {monolith_routes - module_routes} эндпоинтов")

        return module_routes >= monolith_routes
    except Exception as e:
        print_error(f"Ошибка сравнения: {e}")
        return False

def generate_report():
    """Генерация итогового отчета"""
    print_header("ИТОГОВЫЙ ОТЧЕТ")

    results = {
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }

    checks = [
        ('Файлы', check_files),
        ('Модули', check_modules),
        ('Загрузка приложения', check_app_loading),
        ('Конфигурация', check_env),
        ('База данных', check_database),
        ('Telegram бот', check_bot),
        ('Сравнение с монолитом', compare_with_monolith),
    ]

    passed = 0
    total = len(checks)

    for name, check_func in checks:
        try:
            result = check_func()
            results['checks'][name] = result
            if result:
                passed += 1
        except Exception as e:
            print_error(f"Критическая ошибка в проверке '{name}': {e}")
            results['checks'][name] = False

    # Итог
    print_header("РЕЗУЛЬТАТ")
    percentage = (passed / total) * 100

    if percentage == 100:
        print_ok(f"Все проверки пройдены! ({passed}/{total})")
        print_ok("Система полностью готова к работе!")
    elif percentage >= 80:
        print_warning(f"Большинство проверок пройдено ({passed}/{total})")
        print_info("Система работоспособна, но требует внимания")
    else:
        print_error(f"Много проблем! ({passed}/{total})")
        print_error("Требуется срочное вмешательство")

    # Сохраняем отчет
    results['passed'] = passed
    results['total'] = total
    results['percentage'] = percentage

    report_path = '/opt/admin/diagnostics_report.json'
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)

    print_info(f"\nОтчет сохранен: {report_path}")

    return percentage == 100

if __name__ == '__main__':
    print(f"{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         StealthNET - Система диагностики                  ║")
    print("║              Простая как АК-47                            ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

    success = generate_report()
    sys.exit(0 if success else 1)
