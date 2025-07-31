# Archive.zip İndirici

Bu uygulama, domain listesindeki her domain için `/Archive.zip` dosyasını indirir. Önce HTTPS, sonra HTTP protokolünü dener.

## Özellikler

### İndirme Modülü
- ✅ **Modüler Yapı**: Her modül bağımsız ve özel işlevlere sahip
- ✅ **Eşzamanlı İndirme**: 10 worker ile hızlı indirme
- ✅ **Akıllı URL Testi**: Önce HTTPS, sonra HTTP dener
- ✅ **Organize Dosyalama**: Her domain için ayrı klasör
- ✅ **Detaylı Loglama**: Tüm işlemler loglanır
- ✅ **Progress Bar**: Gerçek zamanlı ilerleme gösterimi
- ✅ **Hata Yönetimi**: Kapsamlı hata yakalama ve raporlama

### Varlık Kontrol Modülü
- ✅ **Hızlı Kontrol**: Sadece HEAD isteği ile varlık kontrolü
- ✅ **Yüksek Performans**: 50+ worker ile çok hızlı kontrol
- ✅ **Sonuç Kaydetme**: Bulunan domain'leri txt dosyasına kaydeder
- ✅ **İstatistik Raporu**: Detaylı kontrol istatistikleri
- ✅ **Özelleştirilebilir**: Worker sayısı ve timeout ayarlanabilir

## Kurulum

### GitHub'dan Kurulum

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/ilkmuratkr/Archive.git
cd Archive
```

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Domain listesini hazırlayın:**
```bash
# data/domains/ klasörüne domain listesi dosyası koyun
echo "example.com" > data/domains/domains.txt
echo "test.com" >> data/domains/domains.txt
```

### Manuel Kurulum

1. **Bağımlılıkları yükleyin:**
```bash
cd Archive
pip install -r requirements.txt
```

2. **Domain listesini hazırlayın:**
```bash
# data/domains/ klasörüne domain listesi dosyası koyun
echo "example.com" > data/domains/domains.txt
echo "test.com" >> data/domains/domains.txt
```

## Kullanım

### 1. Archive.zip İndirme

#### Temel Kullanım
```bash
PYTHONPATH=. python3 src/main.py domains.txt
```

#### Gelişmiş Kullanım
```bash
# 20 worker ile çalıştır
PYTHONPATH=. python3 src/main.py domains.txt --workers 20

# 60 saniye timeout ile çalıştır
PYTHONPATH=. python3 src/main.py domains.txt --timeout 60

# Hem worker hem timeout ayarla
PYTHONPATH=. python3 src/main.py domains.txt --workers 15 --timeout 45
```

### 2. Archive.zip Varlık Kontrolü

#### Temel Kullanım
```bash
PYTHONPATH=. python3 src/check_archives.py domains.txt
```

#### Gelişmiş Kullanım
```bash
# 50 worker ile hızlı kontrol
PYTHONPATH=. python3 src/check_archives.py domains.txt --workers 50

# 5 saniye timeout ile hızlı kontrol
PYTHONPATH=. python3 src/check_archives.py domains.txt --timeout 5

# Özel çıktı dosyası
PYTHONPATH=. python3 src/check_archives.py domains.txt --output my_results.txt
```

## Proje Yapısı

```
Archive/
├── src/
│   ├── downloaders/
│   │   └── archive_downloader.py    # Ana indirme modülü
│   ├── utils/
│   │   ├── file_manager.py          # Dosya yönetimi
│   │   ├── url_validator.py         # URL doğrulama
│   │   └── archive_checker.py       # Varlık kontrol modülü
│   ├── main.py                      # İndirme uygulaması
│   └── check_archives.py            # Varlık kontrol uygulaması
├── data/
│   ├── domains/                     # Domain listeleri
│   ├── downloads/                   # İndirilen dosyalar
│   └── results/                     # Kontrol sonuçları
├── logs/                            # Log dosyaları
├── requirements.txt                  # Python bağımlılıkları
└── README.md                        # Bu dosya
```

## Çıktı Yapısı

İndirilen dosyalar şu yapıda organize edilir:

```
data/downloads/
├── example.com/
│   └── Archive.zip
├── test.com/
│   └── Archive.zip
└── another-site.com/
    └── Archive.zip
```

## Özellikler Detayı

### URL Test Sırası
1. `https://domain.com/Archive.zip` - İlk deneme
2. `http://domain.com/Archive.zip` - İkinci deneme
3. Başarısız olursa sonraki domain'e geçer

### Worker Sistemi
- Varsayılan: 10 eşzamanlı worker
- Her worker bağımsız domain işler
- Throttling ile sunucu yükü kontrol edilir

### Hata Yönetimi
- Zaman aşımı kontrolü
- HTTP hata kodları kontrolü
- Ağ bağlantı hataları yakalama
- Detaylı hata logları

### Loglama
- Tüm işlemler `logs/archive_downloader.log` dosyasına kaydedilir
- Başarılı/başarısız indirmeler ayrı ayrı loglanır
- Gerçek zamanlı progress bar

## Örnek Çıktı

### İndirme Modülü
```
╔══════════════════════════════════════════════════════════════╗
║                    Archive.zip İndirici v1.0                    ║
║                                                                  ║
║  • Domain listesinden Archive.zip dosyalarını indirir          ║
║  • Önce HTTPS, sonra HTTP dener                                 ║
║  • 10 eşzamanlı worker ile hızlı indirme                       ║
║  • Her domain için ayrı klasör oluşturur                       ║
╚══════════════════════════════════════════════════════════════╝

📋 Domain dosyası: domains.txt
🔧 Worker sayısı: 10
⏱️  Zaman aşımı: 30 saniye
══════════════════════════════════════════════════════════════

İndiriliyor: 100%|██████████| 50/50 [02:30<00:00,  3.33domain/s]

══════════════════════════════════════════════════════════════
📊 İNDİRME İSTATİSTİKLERİ
══════════════════════════════════════════════════════════════
📁 Toplam Domain: 50
✅ Başarılı İndirme: 35
❌ Başarısız İndirme: 15
📈 Başarı Oranı: 70.0%

🎉 İndirilen dosyalar 'data/downloads/' klasöründe bulunabilir
```

### Varlık Kontrol Modülü
```
╔══════════════════════════════════════════════════════════════╗
║                Archive.zip Varlık Kontrolcüsü v1.0                ║
║                                                                  ║
║  • Domain listesinde Archive.zip varlığını kontrol eder         ║
║  • Önce HTTPS, sonra HTTP dener                                 ║
║  • İndirme yapmaz, sadece kontrol eder                          ║
║  • Sonuçları txt dosyasına kaydeder                             ║
╚══════════════════════════════════════════════════════════════╝

📋 Domain dosyası: domains.txt
🔧 Worker sayısı: 50
⏱️  Zaman aşımı: 5 saniye
📄 Çıktı dosyası: available_archives.txt
══════════════════════════════════════════════════════════════

Kontrol ediliyor: 100%|██████████| 1000/1000 [00:45<00:00, 22.22domain/s]

══════════════════════════════════════════════════════════════
📊 KONTROL İSTATİSTİKLERİ
══════════════════════════════════════════════════════════════
📁 Toplam Domain: 1000
✅ Archive.zip Bulunan: 150
❌ Archive.zip Bulunamayan: 850
📈 Bulunma Oranı: 15.0%

🎉 Sonuçlar 'data/results/available_archives.txt' dosyasına kaydedildi
```

## Geliştirme

### Yeni Özellik Ekleme
1. İlgili modülü düzenleyin
2. Test edin
3. Dokümantasyonu güncelleyin

### Modül Yapısı
- `archive_downloader.py`: Ana indirme mantığı
- `file_manager.py`: Dosya işlemleri
- `url_validator.py`: URL test işlemleri
- `main.py`: Kullanıcı arayüzü

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. 