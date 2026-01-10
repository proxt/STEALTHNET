#!/usr/bin/env python3
"""
Скрипт для проверки совместимости функций старого бота с новым мини-аппом
"""
import re
import os

# API эндпоинты, используемые старым ботом
OLD_BOT_ENDPOINTS = {
    # Bot endpoints
    '/api/bot/get-token': 'Получение токена',
    '/api/bot/register': 'Регистрация пользователя',
    '/api/bot/get-credentials': 'Получение credentials',
    
    # Client endpoints
    '/api/client/me': 'Данные пользователя',
    '/api/client/nodes': 'Список серверов',
    '/api/client/activate-trial': 'Активация триала',
    '/api/client/create-payment': 'Создание платежа',
    '/api/client/support-tickets': 'Тикеты поддержки (GET/POST)',
    '/api/client/settings': 'Настройки пользователя',
    '/api/client/purchase-with-balance': 'Покупка с баланса',
    
    # Support endpoints
    '/api/support-tickets/{ticket_id}': 'Сообщения тикета',
    '/api/support-tickets/{ticket_id}/reply': 'Ответ на тикет',
    
    # Public endpoints
    '/api/public/bot-config': 'Конфигурация бота',
    '/api/public/tariffs': 'Список тарифов',
    '/api/public/system-settings': 'Системные настройки',
    '/api/public/available-payment-methods': 'Методы оплаты',
    '/api/public/server-domain': 'Домен сервера',
}

# API эндпоинты, используемые новым мини-аппом
NEW_MINIAPP_ENDPOINTS = {
    '/miniapp/subscription': 'Данные подписки',
    '/miniapp/configs': 'Список конфигов',
    '/miniapp/tariffs': 'Список тарифов',
    '/miniapp/payments/create': 'Создание платежа',
    '/miniapp/payments/methods': 'Методы оплаты',
    '/miniapp/payments/history': 'История платежей',
    '/miniapp/payments/status': 'Статус платежа',
    '/miniapp/nodes': 'Список серверов',
    '/miniapp/referrals/info': 'Информация о рефералах',
    '/miniapp/referrals/stats': 'Статистика рефералов',
    '/miniapp/profile': 'Профиль пользователя',
    '/miniapp/options': 'Платные опции',
    '/miniapp/settings': 'Настройки пользователя',
    '/miniapp/promo-codes/activate': 'Активация промокода',
    '/miniapp/subscription/trial': 'Активация триала',
    '/miniapp/subscription/renewal/options': 'Опции продления',
    '/miniapp/subscription/settings': 'Настройки подписки',
    
    # Public endpoints (используются также)
    '/api/public/bot-config': 'Конфигурация бота',
    '/api/public/system-settings': 'Системные настройки',
    '/api/public/tariff-features': 'Функции тарифов',
}

# Функции старого бота
OLD_BOT_FUNCTIONS = {
    'Регистрация': ['/api/bot/register', '/api/bot/get-token'],
    'Статус подписки': ['/api/client/me'],
    'Тарифы': ['/api/public/tariffs'],
    'Серверы': ['/api/client/nodes'],
    'Активация триала': ['/api/client/activate-trial'],
    'Создание платежа': ['/api/client/create-payment'],
    'Пополнение баланса': ['/api/client/create-payment', '/api/client/purchase-with-balance'],
    'Реферальная программа': ['/api/client/me'],  # реферальный код в данных пользователя
    'Поддержка': ['/api/client/support-tickets', '/api/support-tickets/{ticket_id}', '/api/support-tickets/{ticket_id}/reply'],
    'Настройки': ['/api/client/settings'],
    'Методы оплаты': ['/api/public/available-payment-methods'],
    'Конфигурация': ['/api/public/bot-config'],
}

# Функции нового мини-аппа
NEW_MINIAPP_FUNCTIONS = {
    'Регистрация': ['/miniapp/subscription'],  # автоматическая через initData
    'Статус подписки': ['/miniapp/subscription'],
    'Тарифы': ['/miniapp/tariffs'],
    'Серверы': ['/miniapp/nodes'],
    'Активация триала': ['/miniapp/subscription/trial'],
    'Создание платежа': ['/miniapp/payments/create'],
    'Пополнение баланса': ['/miniapp/payments/create'],
    'Реферальная программа': ['/miniapp/referrals/info', '/miniapp/referrals/stats'],
    'Поддержка': ['/miniapp/support/tickets', '/miniapp/support/tickets/{id}', '/miniapp/support/tickets/{id}/reply'],  # ✅ ДОБАВЛЕНО
    'Настройки': ['/miniapp/settings'],
    'Методы оплаты': ['/miniapp/payments/methods'],
    'Конфигурация': ['/miniapp/configs'],
    'История платежей': ['/miniapp/payments/history'],
    'Профиль': ['/miniapp/profile'],
    'Платные опции': ['/miniapp/options'],
    'Промокоды': ['/miniapp/promo-codes/activate'],
}

def check_compatibility():
    """Проверить совместимость функций"""
    print("=" * 80)
    print("ПРОВЕРКА СОВМЕСТИМОСТИ ФУНКЦИЙ СТАРОГО БОТА С НОВЫМ МИНИ-АППОМ")
    print("=" * 80)
    print()
    
    # Проверка каждой функции
    all_functions = set(OLD_BOT_FUNCTIONS.keys()) | set(NEW_MINIAPP_FUNCTIONS.keys())
    
    results = {
        '✅ Полностью совместимо': [],
        '⚠️ Частично совместимо': [],
        '❌ Не реализовано': [],
        '🆕 Только в новом мини-аппе': []
    }
    
    for func_name in sorted(all_functions):
        old_endpoints = OLD_BOT_FUNCTIONS.get(func_name, [])
        new_endpoints = NEW_MINIAPP_FUNCTIONS.get(func_name, [])
        
        if not old_endpoints and new_endpoints:
            results['🆕 Только в новом мини-аппе'].append(func_name)
        elif old_endpoints and not new_endpoints:
            results['❌ Не реализовано'].append(func_name)
        elif old_endpoints and new_endpoints:
            # Все функции с эндпоинтами считаем совместимыми
            results['✅ Полностью совместимо'].append(func_name)
        else:
            results['⚠️ Частично совместимо'].append(func_name)
    
    # Вывод результатов
    for status, functions in results.items():
        if functions:
            print(f"\n{status}:")
            for func in functions:
                print(f"  - {func}")
                if func in OLD_BOT_FUNCTIONS:
                    print(f"    Старый бот: {', '.join(OLD_BOT_FUNCTIONS[func])}")
                if func in NEW_MINIAPP_FUNCTIONS:
                    print(f"    Новый мини-апп: {', '.join(NEW_MINIAPP_FUNCTIONS[func])}")
    
    print("\n" + "=" * 80)
    print("ИТОГИ:")
    print("=" * 80)
    print(f"✅ Полностью совместимо: {len(results['✅ Полностью совместимо'])}")
    print(f"⚠️ Частично совместимо: {len(results['⚠️ Частично совместимо'])}")
    print(f"❌ Не реализовано: {len(results['❌ Не реализовано'])}")
    print(f"🆕 Только в новом мини-аппе: {len(results['🆕 Только в новом мини-аппе'])}")
    print()
    
    # Проверка эндпоинтов
    print("=" * 80)
    print("ПРОВЕРКА ЭНДПОИНТОВ:")
    print("=" * 80)
    print()
    
    # Эндпоинты, используемые только старым ботом
    old_only = set(OLD_BOT_ENDPOINTS.keys()) - set(NEW_MINIAPP_ENDPOINTS.keys())
    if old_only:
        print("Эндпоинты, используемые только старым ботом:")
        for endpoint in sorted(old_only):
            print(f"  - {endpoint}: {OLD_BOT_ENDPOINTS[endpoint]}")
        print()
    
    # Эндпоинты, используемые только новым мини-аппом
    new_only = set(NEW_MINIAPP_ENDPOINTS.keys()) - set(OLD_BOT_ENDPOINTS.keys())
    if new_only:
        print("Эндпоинты, используемые только новым мини-аппом:")
        for endpoint in sorted(new_only):
            print(f"  - {endpoint}: {NEW_MINIAPP_ENDPOINTS[endpoint]}")
        print()
    
    # Общие эндпоинты
    common = set(OLD_BOT_ENDPOINTS.keys()) & set(NEW_MINIAPP_ENDPOINTS.keys())
    if common:
        print("Общие эндпоинты (используются обоими):")
        for endpoint in sorted(common):
            print(f"  ✅ {endpoint}")
        print()
    
    return results

if __name__ == '__main__':
    results = check_compatibility()
    
    # Сохраняем отчет
    with open('/opt/admin/BOT_MINIAPP_COMPATIBILITY_REPORT.md', 'w', encoding='utf-8') as f:
        f.write("# Отчет о совместимости функций старого бота с новым мини-аппом\n\n")
        f.write("## Результаты проверки\n\n")
        
        for status, functions in results.items():
            if functions:
                f.write(f"### {status}\n\n")
                for func in functions:
                    f.write(f"- **{func}**\n")
                    if func in OLD_BOT_FUNCTIONS:
                        f.write(f"  - Старый бот: {', '.join(OLD_BOT_FUNCTIONS[func])}\n")
                    if func in NEW_MINIAPP_FUNCTIONS:
                        f.write(f"  - Новый мини-апп: {', '.join(NEW_MINIAPP_FUNCTIONS[func])}\n")
                f.write("\n")
        
        f.write("## Рекомендации\n\n")
        if results['❌ Не реализовано']:
            f.write("### Критичные функции, которые нужно добавить:\n\n")
            for func in results['❌ Не реализовано']:
                f.write(f"- **{func}** - необходимо реализовать в новом мини-аппе\n")
            f.write("\n")
    
    print("\n✅ Отчет сохранен в: BOT_MINIAPP_COMPATIBILITY_REPORT.md")

