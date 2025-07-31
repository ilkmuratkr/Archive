# Archive.zip İndirici

Bu uygulama, domain listesindeki her domain için `/Archive.zip` dosyasını indirir. Önce HTTPS, sonra HTTP protokolünü dener.

## Özellikler

- ✅ **Modüler Yapı**: Her modül bağımsız ve özel işlevlere sahip
- ✅ **Eşzamanlı İndirme**: 10 worker ile hızlı indirme
- ✅ **Akıllı URL Testi**: Önce HTTPS, sonra HTTP dener
- ✅ **Organize Dosyalama**: Her domain için ayrı klasör
- ✅ **Detaylı Loglama**: Tüm işlemler loglanır
- ✅ **Progress Bar**: Gerçek zamanlı ilerleme gösterimi
- ✅ **Hata Yönetimi**: Kapsamlı hata yakalama ve raporlama

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

### Temel Kullanım
```bash
python src/main.py domains.txt
```

### Gelişmiş Kullanım
```bash
# 20 worker ile çalıştır
python src/main.py domains.txt --workers 20

# 60 saniye timeout ile çalıştır
python src/main.py domains.txt --timeout 60

# Hem worker hem timeout ayarla
python src/main.py domains.txt --workers 15 --timeout 45
```

## Proje Yapısı

```
Archive/
├── src/
│   ├── downloaders/
│   │   └── archive_downloader.py    # Ana indirme modülü
│   ├── utils/
│   │   ├── file_manager.py          # Dosya yönetimi
│   │   └── url_validator.py         # URL doğrulama
│   └── main.py                      # Ana uygulama
├── data/
│   ├── domains/                     # Domain listeleri
│   └── downloads/                   # İndirilen dosyalar
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