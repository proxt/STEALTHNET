#!/usr/bin/env python3
"""
Детальная проверка миграции - сравнение логики и функций
"""

import re
import os
import ast
from collections import defaultdict

def extract_function_calls(filepath, function_name):
    """Извлекает вызовы функции из файла"""
    calls = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Ищем вызовы функции
            pattern = rf'{function_name}\s*\('
            matches = re.finditer(pattern, content)
            for match in matches:
                # Берем контекст вокруг вызова
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 200)
                context = content[start:end]
                calls.append(context.strip())
    except Exception as e:
        print(f"Ошибка при чтении {filepath}: {e}")
    return calls

def check_imports(filepath):
    """Проверяет импорты в файле"""
    imports = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Ищем импорты
            pattern = r'^(import |from .* import )'
            for line in content.split('\n'):
                match = re.match(pattern, line)
                if match:
                    imports.append(line.strip())
    except Exception as e:
        print(f"Ошибка при чтении {filepath}: {e}")
    return imports

def check_critical_functions():
    """Проверяет критические функции"""
    print("=" * 80)
    print("ПРОВЕРКА КРИТИЧЕСКИХ ФУНКЦИЙ")
    print("=" * 80)
    print()
    
    critical_functions = [
        'create_local_jwt',
        'get_user_from_token',
        'bcrypt.generate_password_hash',
        'decrypt_key',
        'get_remnawave_headers',
        'create_payment',
        'send_email_in_background'
    ]
    
    results = {}
    
    for func in critical_functions:
        print(f"🔍 Проверка: {func}")
        
        # Проверяем в app.py
        app_calls = extract_function_calls('/opt/admin/app.py', func)
        
        # Проверяем в модульной системе
        module_calls = []
        for root, dirs, files in os.walk('/opt/admin/modules'):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    calls = extract_function_calls(filepath, func)
                    if calls:
                        module_calls.extend([(filepath, call) for call in calls])
        
        results[func] = {
            'app.py': len(app_calls),
            'modules': len(module_calls),
            'module_files': [f for f, _ in module_calls]
        }
        
        if len(app_calls) > 0 and len(module_calls) == 0:
            print(f"   ⚠️  Функция используется в app.py, но не найдена в модулях!")
        elif len(app_calls) > 0 and len(module_calls) > 0:
            print(f"   ✅ Найдена в обоих местах")
        else:
            print(f"   ℹ️  Не используется")
        print()
    
    return results

def check_models():
    """Проверяет использование моделей"""
    print("=" * 80)
    print("ПРОВЕРКА МОДЕЛЕЙ")
    print("=" * 80)
    print()
    
    models = [
        'User',
        'Payment',
        'Tariff',
        'PromoCode',
        'Ticket',
        'SystemSetting',
        'BrandingSetting',
        'BotConfig',
        'ReferralSetting',
        'CurrencyRate',
        'PaymentSetting'
    ]
    
    results = {}
    
    for model in models:
        # Проверяем в app.py
        app_usage = extract_function_calls('/opt/admin/app.py', model)
        
        # Проверяем в модульной системе
        module_usage = []
        for root, dirs, files in os.walk('/opt/admin/modules'):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    usage = extract_function_calls(filepath, model)
                    if usage:
                        module_usage.extend([filepath for _ in usage])
        
        results[model] = {
            'app.py': len(app_usage),
            'modules': len(module_usage),
            'module_files': list(set(module_usage))
        }
        
        if len(app_usage) > 0 and len(module_usage) == 0:
            print(f"   ⚠️  {model}: используется в app.py, но не найден в модулях!")
        elif len(app_usage) > 0 and len(module_usage) > 0:
            print(f"   ✅ {model}: найден в обоих местах")
        else:
            print(f"   ℹ️  {model}: не используется")
    
    print()
    return results

def check_env_variables():
    """Проверяет использование переменных окружения"""
    print("=" * 80)
    print("ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("=" * 80)
    print()
    
    env_vars = [
        'API_URL',
        'ADMIN_TOKEN',
        'DEFAULT_SQUAD_ID',
        'YOUR_SERVER_IP',
        'FERNET_KEY',
        'JWT_SECRET_KEY',
        'MAIL_SERVER',
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'CLIENT_BOT_TOKEN',
        'REMNAWAVE_COOKIES'
    ]
    
    results = {}
    
    for var in env_vars:
        # Проверяем в app.py
        app_usage = []
        try:
            with open('/opt/admin/app.py', 'r', encoding='utf-8') as f:
                content = f.read()
                pattern = rf'os\.getenv\(["\']{var}["\']'
                matches = re.findall(pattern, content)
                app_usage = matches
        except:
            pass
        
        # Проверяем в модульной системе
        module_usage = []
        for root, dirs, files in os.walk('/opt/admin/modules'):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            pattern = rf'os\.getenv\(["\']{var}["\']'
                            matches = re.findall(pattern, content)
                            if matches:
                                module_usage.append(filepath)
                    except:
                        pass
        
        results[var] = {
            'app.py': len(app_usage),
            'modules': len(module_usage),
            'module_files': list(set(module_usage))
        }
        
        if len(app_usage) > 0 and len(module_usage) == 0:
            print(f"   ⚠️  {var}: используется в app.py, но не найден в модулях!")
        elif len(app_usage) > 0 and len(module_usage) > 0:
            print(f"   ✅ {var}: найден в обоих местах")
        else:
            print(f"   ℹ️  {var}: не используется")
    
    print()
    return results

def main():
    print("=" * 80)
    print("ДЕТАЛЬНАЯ ПРОВЕРКА МИГРАЦИИ")
    print("=" * 80)
    print()
    
    # Проверяем критические функции
    func_results = check_critical_functions()
    
    # Проверяем модели
    model_results = check_models()
    
    # Проверяем переменные окружения
    env_results = check_env_variables()
    
    # Сохраняем результаты
    with open('/opt/admin/detailed_migration_check_results.txt', 'w', encoding='utf-8') as f:
        f.write("ДЕТАЛЬНАЯ ПРОВЕРКА МИГРАЦИИ\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("КРИТИЧЕСКИЕ ФУНКЦИИ:\n")
        for func, data in func_results.items():
            f.write(f"  {func}: app.py={data['app.py']}, modules={data['modules']}\n")
            if data['module_files']:
                f.write(f"    Файлы: {', '.join(data['module_files'])}\n")
        f.write("\n")
        
        f.write("МОДЕЛИ:\n")
        for model, data in model_results.items():
            f.write(f"  {model}: app.py={data['app.py']}, modules={data['modules']}\n")
            if data['module_files']:
                f.write(f"    Файлы: {', '.join(data['module_files'])}\n")
        f.write("\n")
        
        f.write("ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:\n")
        for var, data in env_results.items():
            f.write(f"  {var}: app.py={data['app.py']}, modules={data['modules']}\n")
            if data['module_files']:
                f.write(f"    Файлы: {', '.join(data['module_files'])}\n")
    
    print("=" * 80)
    print("ПРОВЕРКА ЗАВЕРШЕНА")
    print("=" * 80)
    print(f"📄 Результаты сохранены в: /opt/admin/detailed_migration_check_results.txt")

if __name__ == '__main__':
    main()

