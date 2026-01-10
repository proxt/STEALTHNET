"""Gunicorn конфигурация для инициализации базы данных в worker процессах"""

def on_starting(server):
    """Вызывается при старте master процесса"""
    print("🚀 [gunicorn] Master процесс запущен")

def when_ready(server):
    """Вызывается когда master процесс готов к работе"""
    print("✅ [gunicorn] Master процесс готов")

def pre_fork(server, worker):
    """Вызывается перед форком worker процесса"""
    print(f"🔧 [gunicorn] Подготовка worker процесса {worker.age}")

def post_fork(server, worker):
    """Вызывается после форка worker процесса - здесь инициализируем БД"""
    import os
    print(f"🚀 [gunicorn] Worker процесс {worker.age} запущен, инициализация БД...")
    print(f"🔍 [gunicorn] Worker {worker.age}: Текущая директория: {os.getcwd()}")
    try:
        # Импортируем app и init_database в worker процессе
        from app import app, init_database
        print(f"🔍 [gunicorn] Worker {worker.age}: app импортирован")
        
        with app.app_context():
            print(f"🔍 [gunicorn] Worker {worker.age}: app_context создан, вызываю init_database()")
            init_database()
            print(f"✅ [gunicorn] Worker {worker.age}: База данных инициализирована")
            
            # Проверяем, что БД создалась
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if db_path and os.path.exists(db_path):
                db_size = os.path.getsize(db_path)
                print(f"✅ [gunicorn] Worker {worker.age}: БД найдена: {db_path}, размер: {db_size} байт")
            else:
                print(f"⚠️ [gunicorn] Worker {worker.age}: БД НЕ найдена: {db_path}")
    except Exception as e:
        print(f"❌ [gunicorn] Worker {worker.age}: Ошибка инициализации БД: {e}")
        import traceback
        traceback.print_exc()

def worker_int(worker):
    """Вызывается при получении SIGINT/SIGQUIT worker процессом"""
    print(f"🛑 [gunicorn] Worker {worker.age} получил сигнал остановки")

def worker_abort(worker):
    """Вызывается при получении SIGABRT worker процессом"""
    print(f"⚠️ [gunicorn] Worker {worker.age} получил сигнал аварийной остановки")
