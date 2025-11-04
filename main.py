import os
import sys

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seans.settings')
    
    from django.core.management import execute_from_command_line
    
    # Replit PORT değişkenini kullan
    port = int(os.environ.get("PORT", 8000))
    
    # İlk çalıştırmada migrate ve collectstatic
    if not os.path.exists('db.sqlite3'):
        print("Veritabanı oluşturuluyor...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
    if not os.path.exists('staticfiles'):
        print("Static dosyalar toplanıyor...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    print(f"Sunucu başlatılıyor: 0.0.0.0:{port}")
    execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])

