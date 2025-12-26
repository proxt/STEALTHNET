#!/bin/bash
# Скрипт для запуска приложения с автоматическими миграциями

set -e

echo "=========================================="
echo "  Запуск StealthNET API с миграциями"
echo "=========================================="
echo ""

# Определяем путь к базе данных
DB_PATH="instance/stealthnet.db"

# Проверяем наличие базы данных
if [ -f "$DB_PATH" ]; then
    echo "✅ База данных найдена: $DB_PATH"
    echo "🔄 Выполнение миграций..."
    echo ""
    
    # Запускаем все миграции
    # Сначала migrate_all.py (основные миграции)
    if [ -f "migration/migrate_all.py" ]; then
        echo "📦 Выполнение migrate_all.py..."
        python3 migration/migrate_all.py "$DB_PATH" || {
            echo "❌ Ошибка при выполнении migrate_all.py"
            exit 1
        }
        echo ""
    fi
    
    # Затем выполняем дополнительные миграции в правильном порядке
    # Порядок важен для зависимостей между миграциями
    
    if [ -f "migration/migrate_add_active_languages_currencies.py" ]; then
        echo "📦 Выполнение migrate_add_active_languages_currencies.py..."
        python3 migration/migrate_add_active_languages_currencies.py || {
            echo "⚠️  Предупреждение: ошибка при выполнении migrate_add_active_languages_currencies.py (возможно уже выполнено)"
        }
        echo ""
    fi
    
    if [ -f "migration/migrate_add_bonus_days.py" ]; then
        echo "📦 Выполнение migrate_add_bonus_days.py..."
        python3 migration/migrate_add_bonus_days.py || {
            echo "⚠️  Предупреждение: ошибка при выполнении migrate_add_bonus_days.py (возможно уже выполнено)"
        }
        echo ""
    fi
    
    if [ -f "migration/migrate_add_bot_config.py" ]; then
        echo "📦 Выполнение migrate_add_bot_config.py..."
        python3 migration/migrate_add_bot_config.py || {
            echo "⚠️  Предупреждение: ошибка при выполнении migrate_add_bot_config.py (возможно уже выполнено)"
        }
        echo ""
    fi
    
    if [ -f "migration/migrate_add_hwid_device_limit.py" ]; then
        echo "📦 Выполнение migrate_add_hwid_device_limit.py..."
        python3 migration/migrate_add_hwid_device_limit.py || {
            echo "⚠️  Предупреждение: ошибка при выполнении migrate_add_hwid_device_limit.py (возможно уже выполнено)"
        }
        echo ""
    fi
    
    if [ -f "migration/migrate_add_quick_download.py" ]; then
        echo "📦 Выполнение migrate_add_quick_download.py..."
        python3 migration/migrate_add_quick_download.py || {
            echo "⚠️  Предупреждение: ошибка при выполнении migrate_add_quick_download.py (возможно уже выполнено)"
        }
        echo ""
    fi
    
    if [ -f "migration/migrate_add_theme_colors.py" ]; then
        echo "📦 Выполнение migrate_add_theme_colors.py..."
        python3 migration/migrate_add_theme_colors.py || {
            echo "⚠️  Предупреждение: ошибка при выполнении migrate_add_theme_colors.py (возможно уже выполнено)"
        }
        echo ""
    fi
    
    echo "✅ Миграции завершены"
    echo ""
else
    echo "ℹ️  База данных не найдена: $DB_PATH"
    echo "ℹ️  База данных будет создана автоматически при первом запуске"
    echo ""
fi

# Запускаем приложение
echo "🚀 Запуск приложения..."
echo ""
exec python3 app.py


