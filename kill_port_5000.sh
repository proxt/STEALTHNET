#!/bin/bash
# Быстрое освобождение порта 5000 (без подтверждения)

echo "🔍 Поиск процессов на порту 5000..."

# Находим все процессы на порту 5000
PIDS=$(lsof -ti:5000 2>/dev/null)

if [ -z "$PIDS" ]; then
    # Альтернативный способ
    PIDS=$(fuser 5000/tcp 2>/dev/null | awk '{print $1}')
fi

if [ -z "$PIDS" ]; then
    # Через netstat/ss
    PIDS=$(netstat -tlnp 2>/dev/null | grep :5000 | awk '{print $7}' | cut -d'/' -f1 | sort -u)
fi

if [ -z "$PIDS" ]; then
    PIDS=$(ss -tlnp 2>/dev/null | grep :5000 | awk '{print $6}' | cut -d',' -f2 | cut -d'=' -f2 | sort -u)
fi

if [ -n "$PIDS" ]; then
    echo "📌 Найдены процессы: $PIDS"
    for PID in $PIDS; do
        if ps -p $PID > /dev/null 2>&1; then
            echo "   Остановка процесса $PID..."
            ps -p $PID -o pid,cmd | tail -1
            kill $PID 2>/dev/null
        fi
    done
    
    sleep 2
    
    # Принудительное завершение, если процесс не остановился
    for PID in $PIDS; do
        if ps -p $PID > /dev/null 2>&1; then
            echo "   Принудительное завершение процесса $PID..."
            kill -9 $PID 2>/dev/null
        fi
    done
    
    sleep 1
    
    # Финальная проверка
    REMAINING=$(lsof -ti:5000 2>/dev/null)
    if [ -n "$REMAINING" ]; then
        echo "⚠️  Некоторые процессы все еще работают: $REMAINING"
        echo "   Попробуйте: sudo fuser -k 5000/tcp"
    else
        echo "✅ Порт 5000 освобожден"
    fi
else
    echo "✅ Порт 5000 уже свободен"
fi

