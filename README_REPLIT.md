# Replit Deployment Rehberi - Seans Takip Sistemi

## Adım 1: Replit'te Proje Oluşturma

### 1.1. Replit Hesabı
1. https://replit.com/ adresine gidin
2. Ücretsiz hesap oluşturun (Sign Up)
3. Giriş yapın

### 1.2. Yeni Repl Oluşturma
1. Ana sayfada **"+ Create"** butonuna tıklayın
2. **"Import from GitHub"** sekmesine gidin
3. GitHub URL'i girin: `https://github.com/SakaBurak/seans`
4. **"Import from GitHub"** butonuna tıklayın
5. Repl adı: `seans` (otomatik doldurulacak)
6. **"Import"** butonuna tıklayın

**VEYA**

1. **"+ Create"** → **"Template"** seçin
2. **"Python"** → **"Python"** seçin
3. Repo'yu manuel olarak yükleyin (Files → Upload)

## Adım 2: Proje Yapılandırması

### 2.1. Secrets (Gizli Değişkenler) Ayarlama
1. Sol panelde **"Secrets"** (🔒) sekmesine tıklayın
2. Aşağıdaki secret'ları ekleyin:

```
DJANGO_SECRET_KEY = django-insecure-hu($4#^yh8=z(ly7o5rrz*#7$4(l85t9kcdeo15yc%wub(!b)9
```

*(İsteğe bağlı: Daha güvenli bir secret key oluşturabilirsiniz)*

### 2.2. Settings.py Güncelleme
1. `seans/settings.py` dosyasını açın
2. Şu değişiklikleri yapın:

```python
import os

# SECRET_KEY güncellemesi
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-hu($4#^yh8=z(ly7o5rrz*#7$4(l85t9kcdeo15yc%wub(!b)9')

# DEBUG
DEBUG = True  # Replit'te True olabilir, ama production için False yapın

# ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']  # Replit domain'i için

# Database (Replit'te SQLite kullanılabilir)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
```

## Adım 3: Bağımlılıkları Yükleme

### 3.1. Shell'de Komutlar
Replit'in otomatik olarak `requirements.txt` dosyasını algılaması gerekir. Eğer olmazsa:

1. **Shell** sekmesinde:
```bash
pip install -r requirements.txt
```

## Adım 4: Veritabanı Kurulumu

Shell'de şu komutları çalıştırın:

```bash
python manage.py migrate
python manage.py createsuperuser
```

*(Superuser için kullanıcı adı, e-posta ve şifre girin)*

## Adım 5: Static Dosyaları Toplama

```bash
python manage.py collectstatic --noinput
```

## Adım 6: Web Server'ı Başlatma

### 6.1. main.py Dosyası Oluşturma (Opsiyonel)
Replit otomatik olarak `.replit` dosyasındaki `run` komutunu kullanır, ama `main.py` de oluşturabilirsiniz:

**main.py** dosyası oluşturun:

```python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seans.settings')
    
    from django.core.management import execute_from_command_line
    
    port = int(os.environ.get("PORT", 8000))
    
    # Migrate
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    
    # Collectstatic (ilk başlatmada)
    if not os.path.exists('staticfiles'):
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # Run server
    execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])
```

### 6.2. Run Butonu
1. Üst menüdeki **"Run"** (▶️) butonuna tıklayın
2. Sunucu başlayacak ve sağ panelde URL görünecek

## Adım 7: Webview'de Test

1. **Run** butonuna tıkladıktan sonra sağ panelde **Webview** sekmesi açılacak
2. Veya sağ üstte **"Open in new tab"** ile tarayıcıda açabilirsiniz
3. Replit otomatik olarak bir URL sağlar: `https://seans-KULLANICIADI.repl.co`

## Adım 8: Always On (Sürekli Çalışır Mod)

**Ücretsiz hesaplarda:**
- Repl kullanılmazsa 5 dakika sonra durur
- Her istekte yeniden başlar (biraz gecikme olabilir)

**Ücretli hesaplarda:**
- Always On özelliği ile 7/24 çalışır

## Sorun Giderme

### Hata: "No module named 'django'"
```bash
pip install -r requirements.txt
```

### Hata: "DisallowedHost"
`settings.py`'de `ALLOWED_HOSTS = ['*']` olduğundan emin olun

### Static dosyalar yüklenmiyor
```bash
python manage.py collectstatic --noinput
```

### Veritabanı hatası
```bash
python manage.py migrate
```

### Port hatası
`.replit` dosyasında `$PORT` kullanıldığından emin olun (Replit otomatik port atar)

## Güncelleme Prosedürü

Kod değişiklikleri için:

1. Replit'te dosyaları düzenleyin
2. Veya GitHub'dan pull çekin:
```bash
git pull origin main
```
3. **Run** butonuna tekrar tıklayın (otomatik restart)

## GitHub Senkronizasyonu

Replit'te yaptığınız değişiklikleri GitHub'a push etmek için:

```bash
git add .
git commit -m "Değişiklik açıklaması"
git push origin main
```

## Önemli Notlar

1. **Veritabanı**: SQLite dosyası (`db.sqlite3`) Replit'te saklanır
2. **Veri kaybı riski**: Ücretsiz hesaplarda Repl silinirse veriler kaybolabilir
3. **Backup**: Önemli veriler için düzenli backup alın
4. **Güvenlik**: Secret key'i `Secrets` bölümünde saklayın, kodda hardcode etmeyin
5. **Production**: Gerçek production için PythonAnywhere veya Heroku gibi servisler önerilir

## Avantajlar

✅ Çok kolay kurulum  
✅ Otomatik HTTPS  
✅ Ücretsiz başlangıç  
✅ Canlı kod düzenleme  
✅ Kolay paylaşım  
✅ GitHub entegrasyonu  

## Dezavantajlar

⚠️ Ücretsiz hesaplarda kullanılmazsa durur  
⚠️ Ücretsiz hesaplarda kaynak limitleri var  
⚠️ Production için ideal değil (test/geliştirme için uygun)

