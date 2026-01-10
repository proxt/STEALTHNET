#!/usr/bin/env python3
"""
Тестовый скрипт для проверки всех вебхуков платежных систем
"""

import requests
import json
from datetime import datetime

# Базовый URL API
BASE_URL = "http://localhost:5000/api"

def test_webhook_endpoints():
    """Тестирование всех вебхуков платежных систем"""

    webhook_endpoints = [
        "/webhook/heleket",
        "/webhook/telegram-stars",
        "/webhook/yookassa",
        "/webhook/crystalpay",
        "/webhook/platega",
        "/webhook/mulenpay",
        "/webhook/urlpay",
        "/webhook/btcpayserver",
        "/webhook/tribute",
        "/webhook/robokassa",
        "/webhook/freekassa",
        "/webhook/monobank"
    ]

    print(f"Тестирование вебхуков платежных систем ({datetime.now()})")
    print("=" * 60)

    results = []

    for endpoint in webhook_endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"Тестирование: {endpoint}")

        try:
            # Отправляем тестовый POST запрос
            test_data = {
                "test": "webhook_test",
                "timestamp": datetime.now().isoformat()
            }

            response = requests.post(url, json=test_data, timeout=10)

            result = {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": response.status_code in [200, 401, 403],  # Успешные или ошибки авторизации
                "response": response.text[:200]  # Первые 200 символов ответа
            }

            results.append(result)

            if response.status_code in [200, 401, 403]:
                print(f"  ✅ Успех: {response.status_code}")
            else:
                print(f"  ❌ Ошибка: {response.status_code}")

        except Exception as e:
            result = {
                "endpoint": endpoint,
                "status_code": 0,
                "success": False,
                "error": str(e)
            }

            results.append(result)
            print(f"  ❌ Исключение: {e}")

        print()

    # Сохраняем результаты в файл
    with open("webhook_test_results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Выводим сводку
    successful = sum(1 for r in results if r["success"])
    total = len(results)

    print("=" * 60)
    print(f"Сводка тестирования:")
    print(f"  Успешных: {successful}/{total}")
    print(f"  Неуспешных: {total - successful}/{total}")
    print(f"Результаты сохранены в: webhook_test_results.json")

if __name__ == "__main__":
    test_webhook_endpoints()