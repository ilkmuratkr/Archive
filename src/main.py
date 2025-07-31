#!/usr/bin/env python3
"""
Archive.zip İndirici

Bu uygulama, domain listesindeki her domain için /Archive.zip dosyasını indirir.
Önce HTTPS, sonra HTTP protokolünü dener.
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path
from colorama import init, Fore, Style

from downloaders.archive_downloader import ArchiveDownloader

# Colorama'yı başlat
init()

# Logging yapılandırması
def setup_logging():
    """Logging yapılandırmasını ayarlar"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/archive_downloader.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def print_banner():
    """Uygulama banner'ını yazdırır"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    Archive.zip İndirici v1.0                    ║
║                                                                  ║
║  • Domain listesinden Archive.zip dosyalarını indirir          ║
║  • Önce HTTPS, sonra HTTP dener                                 ║
║  • 10 eşzamanlı worker ile hızlı indirme                       ║
║  • Her domain için ayrı klasör oluşturur                       ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_stats(stats: dict):
    """İstatistikleri yazdırır"""
    print(f"\n{Fore.GREEN}══════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📊 İNDİRME İSTATİSTİKLERİ{Style.RESET_ALL}")
    print(f"{Fore.GREEN}══════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    
    if "error" in stats:
        print(f"{Fore.RED}❌ Hata: {stats['error']}{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}📁 Toplam Domain: {stats['total_domains']}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Başarılı İndirme: {stats['successful_downloads']}{Style.RESET_ALL}")
    print(f"{Fore.RED}❌ Başarısız İndirme: {stats['failed_downloads']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📈 Başarı Oranı: {stats['success_rate']:.1f}%{Style.RESET_ALL}")
    
    if stats['successful_downloads'] > 0:
        print(f"\n{Fore.GREEN}🎉 İndirilen dosyalar 'data/downloads/' klasöründe bulunabilir{Style.RESET_ALL}")

async def main():
    """Ana uygulama fonksiyonu"""
    parser = argparse.ArgumentParser(description='Archive.zip İndirici')
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
        default=30,
        help='İndirme zaman aşımı saniye (varsayılan: 30)'
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
    print(f"{Fore.GREEN}══════════════════════════════════════════════════════════════{Style.RESET_ALL}\n")
    
    try:
        # İndirici'yi başlat
        async with ArchiveDownloader(
            max_workers=args.workers,
            timeout=args.timeout
        ) as downloader:
            
            # İndirme işlemini başlat
            stats = await downloader.download_all_archives(args.domain_file)
            
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