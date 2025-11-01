# PythonAnywhere Deployment Rehberi

## Adım 1: PythonAnywhere Hesabı Oluşturma
1. https://www.pythonanywhere.com/ adresine gidin
2. "Beginner" (ücretsiz) hesap oluşturun
3. E-posta doğrulaması yapın

## Adım 2: Projeyi GitHub'a Yükleme (Önerilen)

### GitHub'da Repo Oluşturma:
```bash
# Git başlat (eğer yoksa)
git init

# Tüm dosyaları ekle
git add .

# İlk commit
git commit -m "Initial commit - Seans Takip Sistemi"

# GitHub'da yeni repo oluştur, sonra:
git remote add origin https://github.com/KULLANICI_ADI/seans.git
git branch -M main
git push -u origin main
```

## Adım 3: PythonAnywhere'de Proje Kurulumu

### 3.1. Konsolda Projeyi Klonlama:
```bash
# Konsol sekmesine git
cd ~
git clone https://github.com/KULLANICI_ADI/seans.git
cd seans
```

### 3.2. Virtual Environment Oluşturma:
```bash
# PythonAnywhere'de Python 3.10 kullanıyoruz
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3. Veritabanı Kurulumu:
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3.4. Static Dosyaları Toplama:
```bash
python manage.py collectstatic --noinput
```

## Adım 4: Web App Yapılandırması

### 4.1. Web Sekmesine Git:
1. Dashboard'da **Web** sekmesine tıklayın
2. **Add a new web app** butonuna tıklayın
3. Domain seçin (kullanıcıadınız.pythonanywhere.com)
4. **Manual configuration** seçin
5. Python versiyonu: **Python 3.10**

### 4.2. WSGI Dosyasını Düzenle:
**Web sekmesinde** → **WSGI configuration file** linkine tıklayın

Mevcut içeriği şununla değiştirin:

```python
import os
import sys

path = '/home/KULLANICI_ADI/seans'  # KULLANICI_ADI yerine kendi kullanıcı adınızı yazın
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'seans.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 4.3. Settings.py Güncellemesi:

**Files sekmesinde** → `seans/seans/settings.py` dosyasını açın

Şu değişiklikleri yapın:

```python
# DEBUG ayarı
DEBUG = False  # Production için

# ALLOWED_HOSTS
ALLOWED_HOSTS = ['KULLANICI_ADI.pythonanywhere.com', '*.pythonanywhere.com']

# Veritabanı yolu (PythonAnywhere için)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/KULLANICI_ADI/seans/db.sqlite3',
    }
}

# Static files
STATIC_ROOT = '/home/KULLANICI_ADI/seans/staticfiles'
STATIC_URL = '/static/'
```

### 4.4. Static Files ve Media Ayarları:

**Web sekmesinde** **Static files** bölümünde:
- URL: `/static/`
- Directory: `/home/KULLANICI_ADI/seans/staticfiles`

## Adım 5: Web App'i Aktif Etme

1. **Web sekmesine** dönün
2. **Reload** butonuna tıklayın
3. Birkaç saniye bekleyin
4. Tarayıcıda `https://KULLANICI_ADI.pythonanywhere.com` adresini açın

## Adım 6: İlk Kullanım

1. Admin paneli: `https://KULLANICI_ADI.pythonanywhere.com/admin/`
2. Ana sayfa: `https://KULLANICI_ADI.pythonanywhere.com/`
3. Login: `https://KULLANICI_ADI.pythonanywhere.com/login/`

## Sorun Giderme

### Hata: "DisallowedHost"
- `ALLOWED_HOSTS` içinde domain'inizin olduğundan emin olun

### Static dosyalar yüklenmiyor:
```bash
python manage.py collectstatic --noinput
# Web sekmesinde Reload yapın
```

### Veritabanı hatası:
```bash
python manage.py migrate
```

### Kod değişiklikleri yansımıyor:
- **Web sekmesinde** **Reload** butonuna tıklayın
- Bazen konsoldan: `touch /var/www/KULLANICI_ADI_pythonanywhere_com_wsgi.py` komutu gerekebilir

## Güncelleme Prosedürü

Projeyi güncellemek için:

```bash
cd ~/seans
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Sonra **Web sekmesinde** **Reload** yapın.

## Önemli Notlar

1. **Ücretsiz hesap limitleri:**
   - Sadece kendi IP'nizden admin panele erişebilirsiniz
   - Web app 3 ay içinde kullanılmazsa silinir

2. **Güvenlik:**
   - `DEBUG = False` olduğundan emin olun
   - Secret key'i değiştirmeyi düşünün (environment variable kullanın)

3. **Veritabanı:**
   - Ücretsiz hesaplarda SQLite kullanılır
   - Production için MySQL veya PostgreSQL önerilir (ücretli plan)

4. **Domain:**
   - Ücretsiz hesapta: `kullaniciadi.pythonanywhere.com`
   - Özel domain için ücretli plan gerekir

