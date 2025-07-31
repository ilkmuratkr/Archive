import aiohttp
import asyncio
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class URLValidator:
    """URL doğrulama ve erişilebilirlik testi için sınıf"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
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
    
    async def test_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        URL'nin erişilebilir olup olmadığını test eder
        
        Args:
            url: Test edilecek URL
            
        Returns:
            Tuple[bool, Optional[str]]: (erişilebilir mi, hata mesajı)
        """
        try:
            async with self.session.head(url, allow_redirects=True) as response:
                if response.status == 200:
                    return True, None
                else:
                    return False, f"HTTP {response.status}"
        except aiohttp.ClientError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Beklenmeyen hata: {str(e)}"
    
    async def check_archive_urls(self, domain: str) -> Tuple[bool, str, Optional[str]]:
        """
        Domain için HTTPS ve HTTP Archive.zip URL'lerini test eder
        
        Args:
            domain: Test edilecek domain
            
        Returns:
            Tuple[bool, str, Optional[str]]: (başarılı mı, çalışan URL, hata mesajı)
        """
        urls_to_test = [
            f"https://{domain}/Archive.zip",
            f"http://{domain}/Archive.zip"
        ]
        
        for url in urls_to_test:
            logger.info(f"Test ediliyor: {url}")
            is_accessible, error = await self.test_url(url)
            
            if is_accessible:
                logger.info(f"Başarılı: {url}")
                return True, url, None
            else:
                logger.warning(f"Başarısız: {url} - {error}")
        
        return False, "", f"Hiçbir URL erişilebilir değil: {domain}" 