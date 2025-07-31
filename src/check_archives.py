#!/usr/bin/env python3
"""
Archive.zip Varlık Kontrolcüsü

Bu uygulama, domain listesindeki her domain için /Archive.zip dosyasının varlığını kontrol eder.
İndirme yapmaz, sadece hangi sitelerde Archive.zip olduğunu tespit eder.
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path
from colorama import init, Fore, Style

from utils.archive_checker import ArchiveChecker
from utils.file_manager import FileManager

# Colorama'yı başlat
init()

# Logging yapılandırması
def setup_logging():
    """Logging yapılandırmasını ayarlar"""
    # Logs klasörünü oluştur
    Path("logs").mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/archive_checker.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def print_banner():
    """Uygulama banner'ını yazdırır"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                Archive.zip Varlık Kontrolcüsü v1.0                ║
║                                                                  ║
║  • Domain listesinde Archive.zip varlığını kontrol eder         ║
║  • Önce HTTPS, sonra HTTP dener                                 ║
║  • İndirme yapmaz, sadece kontrol eder                          ║
║  • Sonuçları txt dosyasına kaydeder                             ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_stats(stats: dict):
    """İstatistikleri yazdırır"""
    print(f"\n{Fore.GREEN}══════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📊 KONTROL İSTATİSTİKLERİ{Style.RESET_ALL}")
    print(f"{Fore.GREEN}══════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    
    if "error" in stats:
        print(f"{Fore.RED}❌ Hata: {stats['error']}{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}📁 Toplam Domain: {stats['total_domains']}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Archive.zip Bulunan: {stats['found_archives']}{Style.RESET_ALL}")
    print(f"{Fore.RED}❌ Archive.zip Bulunamayan: {stats['not_found']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📈 Bulunma Oranı: {stats['success_rate']:.1f}%{Style.RESET_ALL}")
    
    if stats['found_archives'] > 0:
        print(f"\n{Fore.GREEN}🎉 Sonuçlar 'data/results/available_archives.txt' dosyasına kaydedildi{Style.RESET_ALL}")

async def main():
    """Ana uygulama fonksiyonu"""
    parser = argparse.ArgumentParser(description='Archive.zip Varlık Kontrolcüsü')
    parser.add_argument(
        'domain_file',
        help='Domain listesi dosyası (data/domains/ klasöründe)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=10,
        help='Eşzamanlı worker sayısı (varsayılan: 10)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Kontrol zaman aşımı saniye (varsayılan: 10)'
    )
    parser.add_argument(
        '--output',
        default='available_archives.txt',
        help='Çıktı dosyası adı (varsayılan: available_archives.txt)'
    )
    
    args = parser.parse_args()
    
    # Banner'ı yazdır
    print_banner()
    
    # Logging'i ayarla
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Domain dosyasının varlığını kontrol et
    domain_file_path = Path("data/domains") / args.domain_file
    if not domain_file_path.exists():
        print(f"{Fore.RED}❌ Domain dosyası bulunamadı: {domain_file_path}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Lütfen domain listesini 'data/domains/' klasörüne koyun{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}📋 Domain dosyası: {args.domain_file}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔧 Worker sayısı: {args.workers}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}⏱️  Zaman aşımı: {args.timeout} saniye{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📄 Çıktı dosyası: {args.output}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}══════════════════════════════════════════════════════════════{Style.RESET_ALL}\n")
    
    try:
        # File manager'ı başlat
        file_manager = FileManager()
        
        # Domain listesini oku
        domains = await file_manager.read_domain_list(args.domain_file)
        
        if not domains:
            print(f"{Fore.RED}❌ Domain listesi boş veya okunamadı{Style.RESET_ALL}")
            return
        
        # Kontrolcü'yü başlat
        async with ArchiveChecker(
            max_workers=args.workers,
            timeout=args.timeout
        ) as checker:
            
            # Tüm domain'leri kontrol et
            results = await checker.check_all_domains(domains)
            
            # Sonuçları kaydet
            await checker.save_results(results, args.output)
            
            # İstatistikleri hesapla
            stats = checker.get_stats(len(domains), len(results))
            
            # İstatistikleri yazdır
            print_stats(stats)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Kullanıcı tarafından durduruldu{Style.RESET_ALL}")
        logger.info("Kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Beklenmeyen hata: {e}{Style.RESET_ALL}")
        logger.error(f"Beklenmeyen hata: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 