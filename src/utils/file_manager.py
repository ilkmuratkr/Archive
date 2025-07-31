import os
import aiofiles
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

class FileManager:
    """Dosya ve klasör yönetimi için sınıf"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.downloads_dir = self.base_dir / "downloads"
        self.domains_dir = self.base_dir / "domains"
        self.logs_dir = Path("logs")
        
        # Klasörleri oluştur
        self._create_directories()
    
    def _create_directories(self):
        """Gerekli klasörleri oluşturur"""
        directories = [
            self.downloads_dir,
            self.domains_dir,
            self.logs_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Klasör oluşturuldu: {directory}")
    
    async def read_domain_list(self, filename: str) -> List[str]:
        """
        Domain listesini dosyadan okur
        
        Args:
            filename: Domain listesi dosyasının adı
            
        Returns:
            List[str]: Domain listesi
        """
        file_path = self.domains_dir / filename
        
        if not file_path.exists():
            logger.error(f"Dosya bulunamadı: {file_path}")
            return []
        
        domains = []
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                async for line in f:
                    domain = line.strip()
                    if domain and not domain.startswith('#'):
                        domains.append(domain)
            
            logger.info(f"{len(domains)} domain okundu: {filename}")
            return domains
            
        except Exception as e:
            logger.error(f"Dosya okuma hatası: {e}")
            return []
    
    def get_domain_download_path(self, domain: str) -> Path:
        """
        Domain için indirme klasörü yolunu döndürür
        
        Args:
            domain: Domain adı
            
        Returns:
            Path: İndirme klasörü yolu
        """
        # Domain adını güvenli dosya adına çevir
        safe_domain = self._sanitize_filename(domain)
        domain_dir = self.downloads_dir / safe_domain
        domain_dir.mkdir(exist_ok=True)
        return domain_dir
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Dosya adını güvenli hale getirir
        
        Args:
            filename: Orijinal dosya adı
            
        Returns:
            str: Güvenli dosya adı
        """
        # Geçersiz karakterleri kaldır
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Nokta ile başlayan dosya adlarını düzelt
        if filename.startswith('.'):
            filename = '_' + filename
        
        return filename
    
    async def save_download_log(self, domain: str, url: str, success: bool, error: Optional[str] = None):
        """
        İndirme logunu kaydeder
        
        Args:
            domain: Domain adı
            url: İndirilen URL
            success: Başarılı mı
            error: Hata mesajı
        """
        log_file = self.logs_dir / "downloads.log"
        
        timestamp = Path().stat().st_mtime
        status = "BAŞARILI" if success else "BAŞARISIZ"
        error_msg = f" - Hata: {error}" if error else ""
        
        log_entry = f"[{timestamp}] {domain} - {url} - {status}{error_msg}\n"
        
        try:
            async with aiofiles.open(log_file, 'a', encoding='utf-8') as f:
                await f.write(log_entry)
        except Exception as e:
            logger.error(f"Log kaydetme hatası: {e}")
    
    def get_download_stats(self) -> dict:
        """
        İndirme istatistiklerini döndürür
        
        Returns:
            dict: İstatistikler
        """
        total_domains = len(list(self.downloads_dir.glob("*")))
        successful_downloads = len([d for d in self.downloads_dir.glob("*") if (d / "Archive.zip").exists()])
        
        return {
            "total_domains": total_domains,
            "successful_downloads": successful_downloads,
            "success_rate": (successful_downloads / total_domains * 100) if total_domains > 0 else 0
        } 