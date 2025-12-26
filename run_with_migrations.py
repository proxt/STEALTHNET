#!/usr/bin/env python3
"""
Скрипт для запуска приложения с автоматическими миграциями.
Проверяет наличие БД и выполняет все миграции перед запуском app.py
"""

import os
import sys
import subprocess
from pathlib import Path

def find_database():
    """Находит путь к базе данных в стандартных местах"""
    possible_paths = [
        Path("instance/stealthnet.db"),
        Path("stealthnet.db"),
        Path("/var/www/stealthnet-api/instance/stealthnet.db"),
        Path("/var/www/stealthnet-api/stealthnet.db"),
    ]
    
    # Пробуем прочитать путь из .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        db_uri = os.getenv('SQLALCHEMY_DATABASE_URI', '')
        if db_uri and db_uri.startswith('sqlite:///'):
            db_path = Path(db_uri.replace('sqlite:///', ''))
            if db_path.exists():
                return db_path
    except:
        pass
    
    # Ищем в стандартных путях
    for db_path in possible_paths:
        if db_path.exists():
            return db_path
    
    return None

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("  Запуск StealthNET API")
        print("=" * 60)
        print()
        
        # Ищем базу данных
        db_path = find_database()
        
        # Проверяем наличие базы данных
        if db_path and db_path.exists():
            print(f"✅ База данных найдена: {db_path}")
            print("🔄 Выполнение миграций...")
            print()
            
            # Список миграций в правильном порядке
            migrations = [
                ("migration/migrate_all.py", True),  # (путь, требует db_path)
                ("migration/migrate_add_active_languages_currencies.py", False),
                ("migration/migrate_add_bonus_days.py", False),
                ("migration/migrate_add_bot_config.py", False),
                ("migration/migrate_add_hwid_device_limit.py", False),
                ("migration/migrate_add_quick_download.py", False),
                ("migration/migrate_add_theme_colors.py", False),
            ]
            
            # Выполняем миграции
            for migration, needs_db_path in migrations:
                migration_path = Path(migration)
                if migration_path.exists():
                    print(f"📦 Выполнение {migration}...")
                    try:
                        if needs_db_path:
                            result = subprocess.run(
                                [sys.executable, str(migration_path), str(db_path)],
                                check=False,
                                timeout=300
                            )
                        else:
                            result = subprocess.run(
                                [sys.executable, str(migration_path)],
                                check=False,
                                timeout=300
                            )
                        
                        if result.returncode == 0:
                            print(f"   ✅ {migration} выполнен успешно")
                        else:
                            print(f"   ⚠️  {migration} завершился с кодом {result.returncode} (возможно уже выполнено)")
                    except subprocess.TimeoutExpired:
                        print(f"   ❌ Таймаут при выполнении {migration}")
                    except Exception as e:
                        print(f"   ⚠️  Ошибка: {e}")
                    print()
                else:
                    print(f"   ⚠️  Файл миграции не найден: {migration}")
            
            print("✅ Миграции завершены")
            print()
        else:
            print("ℹ️  База данных не найдена")
            print("ℹ️  База данных будет создана автоматически при первом запуске app.py")
            print()
        
        # Запускаем приложение
        print("🚀 Запуск приложения app.py...")
        print("=" * 60)
        print()
        
        # Проверяем, что app.py существует
        app_path = Path("app.py")
        if not app_path.exists():
            # Пробуем найти в рабочей директории
            app_path = Path("/app/app.py")
            if not app_path.exists():
                print(f"❌ Ошибка: app.py не найден")
                print(f"   Текущая директория: {os.getcwd()}")
                print(f"   Проверяемые пути: app.py, /app/app.py")
                sys.exit(1)
        
        # Заменяем текущий процесс на app.py
        # os.execv заменяет текущий процесс полностью, поэтому код после него не выполнится
        # Используем относительный путь для app.py, если он в текущей директории
        if app_path.name == "app.py" and Path("app.py").exists():
            app_to_run = "app.py"
        else:
            app_to_run = str(app_path)
        
        print(f"📝 Запуск: {sys.executable} {app_to_run}")
        print()
        
        try:
            # os.execv заменяет текущий процесс
            os.execv(sys.executable, [sys.executable, app_to_run])
        except OSError as e:
            print(f"❌ Ошибка при запуске app.py: {e}")
            print(f"   Попытка альтернативного запуска...")
            # Альтернативный способ - через subprocess (но это создаст дочерний процесс)
            import subprocess
            sys.exit(subprocess.call([sys.executable, app_to_run]))
        
    except KeyboardInterrupt:
        print("\n⚠️  Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Критическая ошибка в run_with_migrations.py: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
