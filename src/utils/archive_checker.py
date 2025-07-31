import asyncio
import aiohttp
import logging
from typing import List, Optional, Tuple
from asyncio_throttle import Throttler
from tqdm import tqdm
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)

class ArchiveChecker:
    """Archive.zip dosyalarının varlığını kontrol eden sınıf"""
    
    def __init__(self, max_workers: int = 10, timeout: int = 10):
        self.max_workers = max_workers
        self.timeout = timeout
        self.throttler = Throttler(rate_limit=max_workers, period=1)
        self.session = None
        self.available_archives = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def check_archive_exists(self, domain: str) -> Tuple[bool, str, Optional[str]]:
        """
        Domain'de Archive.zip dosyasının varlığını kontrol eder
        
        Args:
            domain: Kontrol edilecek domain
            
        Returns:
            Tuple[bool, str, Optional[str]]: (mevcut mu, URL, hata mesajı)
        """
        urls_to_test = [
            f"https://{domain}/Archive.zip",
            f"http://{domain}/Archive.zip"
        ]
        
        for url in urls_to_test:
            try:
                async with self.throttler:
                    async with self.session.head(url, allow_redirects=True) as response:
                        if response.status == 200:
                            logger.info(f"✅ Archive.zip bulundu: {domain} - {url}")
                            return True, url, None
                        else:
                            logger.debug(f"❌ Archive.zip yok: {domain} - HTTP {response.status}")
                            
            except asyncio.TimeoutError:
                logger.debug(f"⏱️ Zaman aşımı: {domain}")
            except Exception as e:
                logger.debug(f"❌ Hata: {domain} - {str(e)}")
        
        return False, "", f"Archive.zip bulunamadı: {domain}"
    
    async def check_all_domains(self, domains: List[str]) -> List[Tuple[str, str]]:
        """
        Tüm domain'lerde Archive.zip varlığını kontrol eder
        
        Args:
            domains: Kontrol edilecek domain listesi
            
        Returns:
            List[Tuple[str, str]]: [(domain, url)] - Archive.zip bulunan domain'ler
        """
        logger.info(f"Toplam {len(domains)} domain kontrol edilecek")
        
        # Semaphore ile eşzamanlı işlem sayısını sınırla
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def check_with_semaphore(domain):
            async with semaphore:
                return await self.check_archive_exists(domain)
        
        # Tüm domain'leri kontrol et
        tasks = [check_with_semaphore(domain) for domain in domains]
        
        # Progress bar ile ilerlemeyi göster
        found_archives = []
        not_found_count = 0
        
        with tqdm(total=len(domains), desc="Kontrol ediliyor", unit="domain") as pbar:
            for task in asyncio.as_completed(tasks):
                exists, url, error = await task
                
                if exists:
                    found_archives.append((url.split('/')[2], url))  # domain, url
                    pbar.set_postfix({"Bulunan": len(found_archives), "Bulunamayan": not_found_count})
                else:
                    not_found_count += 1
                    pbar.set_postfix({"Bulunan": len(found_archives), "Bulunamayan": not_found_count})
                
                pbar.update(1)
        
        logger.info(f"Kontrol tamamlandı: {len(found_archives)}/{len(domains)} domain'de Archive.zip bulundu")
        return found_archives
    
    async def save_results(self, results: List[Tuple[str, str]], output_file: str = "available_archives.txt"):
        """
        Sonuçları dosyaya kaydeder
        
        Args:
            results: [(domain, url)] listesi
            output_file: Çıktı dosyası adı
        """
        output_path = Path("data/results") / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        try:
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write("# Archive.zip Bulunan Domain'ler\n")
                await f.write(f"# Toplam: {len(results)} domain\n")
                await f.write("# Format: domain - url\n\n")
                
                for domain, url in results:
                    await f.write(f"{domain} - {url}\n")
            
            logger.info(f"Sonuçlar kaydedildi: {output_path}")
            
        except Exception as e:
            logger.error(f"Sonuç kaydetme hatası: {e}")
    
    def get_stats(self, total_domains: int, found_count: int) -> dict:
        """
        İstatistikleri döndürür
        
        Args:
            total_domains: Toplam domain sayısı
            found_count: Bulunan domain sayısı
            
        Returns:
            dict: İstatistikler
        """
        return {
            "total_domains": total_domains,
            "found_archives": found_count,
            "not_found": total_domains - found_count,
            "success_rate": (found_count / total_domains * 100) if total_domains > 0 else 0
        } 