#!/usr/bin/env python3
"""
Скрипт для проверки полноты миграции с app.py на модульную систему
Сравнивает все эндпоинты и функции
"""

import re
import os
from collections import defaultdict

def extract_routes_from_file(filepath):
    """Извлекает все роуты из файла"""
    routes = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Ищем все @app.route декораторы
            pattern = r"@app\.route\(['\"]([^'\"]+)['\"][^)]*\)"
            matches = re.findall(pattern, content)
            routes.extend(matches)
            
            # Также ищем через другие декораторы
            pattern2 = r"@.*\.route\(['\"]([^'\"]+)['\"][^)]*\)"
            matches2 = re.findall(pattern2, content)
            routes.extend(matches2)
    except Exception as e:
        print(f"Ошибка при чтении {filepath}: {e}")
    return list(set(routes))  # Убираем дубликаты

def extract_routes_from_directory(directory):
    """Извлекает все роуты из всех файлов в директории"""
    routes = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                file_routes = extract_routes_from_file(filepath)
                routes.extend(file_routes)
    return list(set(routes))

def normalize_route(route):
    """Нормализует роут для сравнения"""
    # Убираем параметры типа <int:id>, <uuid>, <path:path>
    route = re.sub(r'<[^>]+>', '<param>', route)
    # Убираем trailing slash
    route = route.rstrip('/')
    return route

def compare_routes(old_routes, new_routes):
    """Сравнивает два списка роутов"""
    old_normalized = {normalize_route(r): r for r in old_routes}
    new_normalized = {normalize_route(r): r for r in new_routes}
    
    missing = []
    added = []
    
    for old_norm, old_orig in old_normalized.items():
        if old_norm not in new_normalized:
            missing.append(old_orig)
    
    for new_norm, new_orig in new_normalized.items():
        if new_norm not in old_normalized:
            added.append(new_orig)
    
    return missing, added

def main():
    print("=" * 80)
    print("ПРОВЕРКА ПОЛНОТЫ МИГРАЦИИ: app.py -> модульная система")
    print("=" * 80)
    print()
    
    # Извлекаем роуты из app.py
    print("📖 Чтение app.py...")
    old_routes = extract_routes_from_file('/opt/admin/app.py')
    print(f"   Найдено эндпоинтов в app.py: {len(old_routes)}")
    
    # Извлекаем роуты из модульной системы
    print("📖 Чтение модульной системы...")
    new_routes = extract_routes_from_directory('/opt/admin/modules/api')
    # Также проверяем app.py
    main_routes = extract_routes_from_file('/opt/admin/app.py')
    new_routes.extend(main_routes)
    new_routes = list(set(new_routes))
    print(f"   Найдено эндпоинтов в модульной системе: {len(new_routes)}")
    print()
    
    # Сравниваем
    print("🔍 Сравнение эндпоинтов...")
    missing, added = compare_routes(old_routes, new_routes)
    
    print()
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 80)
    print()
    
    if missing:
        print(f"❌ ОТСУТСТВУЮЩИЕ ЭНДПОИНТЫ ({len(missing)}):")
        print("   (Эти эндпоинты есть в app.py, но отсутствуют в модульной системе)")
        print()
        for route in sorted(missing):
            print(f"   - {route}")
        print()
    else:
        print("✅ Все эндпоинты из app.py присутствуют в модульной системе!")
        print()
    
    if added:
        print(f"✅ НОВЫЕ ЭНДПОИНТЫ ({len(added)}):")
        print("   (Эти эндпоинты добавлены в модульной системе)")
        print()
        for route in sorted(added):
            print(f"   + {route}")
        print()
    
    # Группируем по категориям
    print("=" * 80)
    print("СТАТИСТИКА ПО КАТЕГОРИЯМ")
    print("=" * 80)
    print()
    
    categories = defaultdict(list)
    for route in old_routes:
        if route.startswith('/api/admin/'):
            categories['Admin'].append(route)
        elif route.startswith('/api/client/'):
            categories['Client'].append(route)
        elif route.startswith('/api/public/'):
            categories['Public'].append(route)
        elif route.startswith('/api/bot/'):
            categories['Bot'].append(route)
        elif route.startswith('/api/webhook/'):
            categories['Webhook'].append(route)
        elif route.startswith('/miniapp/'):
            categories['MiniApp'].append(route)
        elif route.startswith('/api/support'):
            categories['Support'].append(route)
        else:
            categories['Other'].append(route)
    
    for cat, routes in sorted(categories.items()):
        print(f"   {cat}: {len(routes)} эндпоинтов")
    
    print()
    print("=" * 80)
    print("ПРОВЕРКА ЗАВЕРШЕНА")
    print("=" * 80)
    
    # Сохраняем результаты
    with open('/opt/admin/migration_check_results.txt', 'w', encoding='utf-8') as f:
        f.write("ПРОВЕРКА ПОЛНОТЫ МИГРАЦИИ\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Эндпоинтов в app.py: {len(old_routes)}\n")
        f.write(f"Эндпоинтов в модульной системе: {len(new_routes)}\n\n")
        
        if missing:
            f.write(f"ОТСУТСТВУЮЩИЕ ЭНДПОИНТЫ ({len(missing)}):\n")
            for route in sorted(missing):
                f.write(f"  - {route}\n")
            f.write("\n")
        
        if added:
            f.write(f"НОВЫЕ ЭНДПОИНТЫ ({len(added)}):\n")
            for route in sorted(added):
                f.write(f"  + {route}\n")
            f.write("\n")
    
    print(f"📄 Результаты сохранены в: /opt/admin/migration_check_results.txt")
    
    return len(missing) == 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

