import asyncio
import aiohttp
import aiofiles
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from asyncio_throttle import Throttler
from tqdm import tqdm
import time

from src.utils.url_validator import URLValidator
from src.utils.file_manager import FileManager

logger = logging.getLogger(__name__)

class ArchiveDownloader:
    """Archive.zip dosyalarını indiren ana sınıf"""
    
    def __init__(self, max_workers: int = 10, timeout: int = 30):
        self.max_workers = max_workers
        self.timeout = timeout
        self.throttler = Throttler(rate_limit=max_workers, period=1)
        self.file_manager = FileManager()
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def download_archive(self, domain: str, url: str) -> Tuple[bool, Optional[str]]:
        """
        Tek bir Archive.zip dosyasını indirir
        
        Args:
            domain: Domain adı
            url: İndirilecek URL
            
        Returns:
            Tuple[bool, Optional[str]]: (başarılı mı, hata mesajı)
        """
        try:
            async with self.throttler:
                # Domain klasörünü oluştur
                domain_dir = self.file_manager.get_domain_download_path(domain)
                archive_path = domain_dir / "Archive.zip"
                
                # Dosya zaten varsa atla
                if archive_path.exists():
                    logger.info(f"Dosya zaten mevcut: {archive_path}")
                    return True, None
                
                # İndirme işlemi
                async with self.session.get(url) as response:
                    if response.status == 200:
                        # Dosyayı kaydet
                        async with aiofiles.open(archive_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                        
                        logger.info(f"Başarıyla indirildi: {domain} - {archive_path}")
                        return True, None
                    else:
                        error_msg = f"HTTP {response.status}"
                        logger.error(f"İndirme hatası: {domain} - {error_msg}")
                        return False, error_msg
                        
        except asyncio.TimeoutError:
            error_msg = "Zaman aşımı"
            logger.error(f"Zaman aşımı: {domain}")
            return False, error_msg
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Beklenmeyen hata: {domain} - {error_msg}")
            return False, error_msg
    
    async def process_domain(self, domain: str) -> Tuple[bool, str, Optional[str]]:
        """
        Tek bir domain'i işler (URL test + indirme)
        
        Args:
            domain: İşlenecek domain
            
        Returns:
            Tuple[bool, str, Optional[str]]: (başarılı mı, URL, hata mesajı)
        """
        async with URLValidator(timeout=10) as validator:
            # URL'leri test et
            is_accessible, working_url, error = await validator.check_archive_urls(domain)
            
            if not is_accessible:
                await self.file_manager.save_download_log(domain, "", False, error)
                return False, "", error
            
            # Dosyayı indir
            success, download_error = await self.download_archive(domain, working_url)
            
            # Log kaydet
            await self.file_manager.save_download_log(
                domain, working_url, success, download_error
            )
            
            if success:
                return True, working_url, None
            else:
                return False, working_url, download_error
    
    async def download_all_archives(self, domain_list_file: str) -> dict:
        """
        Tüm domain'lerden Archive.zip dosyalarını indirir
        
        Args:
            domain_list_file: Domain listesi dosyası
            
        Returns:
            dict: İndirme istatistikleri
        """
        # Domain listesini oku
        domains = await self.file_manager.read_domain_list(domain_list_file)
        
        if not domains:
            logger.error("Domain listesi boş veya okunamadı")
            return {"error": "Domain listesi okunamadı"}
        
        logger.info(f"Toplam {len(domains)} domain işlenecek")
        
        # Semaphore ile eşzamanlı işlem sayısını sınırla
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_with_semaphore(domain):
            async with semaphore:
                return await self.process_domain(domain)
        
        # Tüm domain'leri işle
        tasks = [process_with_semaphore(domain) for domain in domains]
        
        # Progress bar ile ilerlemeyi göster
        successful_downloads = 0
        failed_downloads = 0
        
        with tqdm(total=len(domains), desc="İndiriliyor", unit="domain") as pbar:
            for task in asyncio.as_completed(tasks):
                success, url, error = await task
                
                if success:
                    successful_downloads += 1
                    pbar.set_postfix({"Başarılı": successful_downloads, "Başarısız": failed_downloads})
                else:
                    failed_downloads += 1
                    pbar.set_postfix({"Başarılı": successful_downloads, "Başarısız": failed_downloads})
                
                pbar.update(1)
        
        # İstatistikleri hesapla
        stats = {
            "total_domains": len(domains),
            "successful_downloads": successful_downloads,
            "failed_downloads": failed_downloads,
            "success_rate": (successful_downloads / len(domains)) * 100
        }
        
        logger.info(f"İndirme tamamlandı: {successful_downloads}/{len(domains)} başarılı")
        return stats 