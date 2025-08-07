import asyncio
import time
import ssl
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
from ..models import SiteContent


class WebScraper:
    """Сервис для получения содержимого веб-сайтов"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.browser: Optional[Browser] = None
    
    async def __aenter__(self):
        """Асинхронный контекст-менеджер для инициализации браузера"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие браузера"""
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()
    
    async def scrape_site(self, url: str) -> SiteContent:
        """Получить полную информацию о сайте"""
        start_time = time.time()
        
        try:
            # Основная информация через Playwright
            content_data = await self._scrape_with_playwright(url)

            # Дополнительная информация через requests
            additional_data = await self._get_additional_info(url)
            
            response_time = time.time() - start_time
            
            return SiteContent(
                url=url,
                title=content_data.get("title"),
                html_content=content_data.get("html_content", ""),
                text_content=content_data.get("text_content", ""),
                meta_description=content_data.get("meta_description"),
                meta_keywords=content_data.get("meta_keywords", []),
                links=content_data.get("links", []),
                forms=content_data.get("forms", []),
                screenshot_path=content_data.get("screenshot_path"),
                response_time=response_time,
                status_code=additional_data.get("status_code")
            )
            
        except Exception as e:
            # Возвращаем базовую информацию даже при ошибке
            response_time = time.time() - start_time
            return SiteContent(
                url=url,
                html_content="",
                text_content=f"Error scraping site: {str(e)}",
                response_time=response_time,
                status_code=0
            )
    
    async def _scrape_with_playwright(self, url: str) -> Dict[str, Any]:
        """Получить содержимое сайта через Playwright"""
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")
        
        page = await self.browser.new_page()
        
        try:
            # Переход на страницу
            response = await page.goto(url, timeout=self.timeout * 1000)
            
            # Ждем загрузки контента
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            # Получаем основную информацию
            title = await page.title()
            html_content = await page.content()
            text_content = await page.inner_text("body")
            
            # Мета-теги
            meta_description = await page.get_attribute('meta[name="description"]', "content")
            meta_keywords_elem = await page.query_selector('meta[name="keywords"]')
            meta_keywords = []
            if meta_keywords_elem:
                keywords_content = await meta_keywords_elem.get_attribute("content")
                if keywords_content:
                    meta_keywords = [kw.strip() for kw in keywords_content.split(",")]
            
            # Ссылки
            links = await self._extract_links(page, url)
            
            # Формы
            forms = await self._extract_forms(page)
            
            # Скриншот
            screenshot_path = await self._take_screenshot(page, url)
            
            return {
                "title": title,
                "html_content": html_content,
                "text_content": text_content,
                "meta_description": meta_description,
                "meta_keywords": meta_keywords,
                "links": links,
                "forms": forms,
                "screenshot_path": screenshot_path
            }
            
        finally:
            await page.close()
    
    async def _extract_links(self, page: Page, base_url: str) -> List[str]:
        """Извлечь все ссылки со страницы"""
        try:
            link_elements = await page.query_selector_all("a[href]")
            links = []
            
            for link in link_elements:
                href = await link.get_attribute("href")
                if href:
                    absolute_url = urljoin(base_url, href)
                    links.append(absolute_url)
            
            return links[:50]  # Ограничиваем количество ссылок
            
        except Exception:
            return []
    
    async def _extract_forms(self, page: Page) -> List[Dict[str, Any]]:
        """Извлечь информацию о формах"""
        try:
            form_elements = await page.query_selector_all("form")
            forms = []
            
            for form in form_elements:
                form_info = {
                    "action": await form.get_attribute("action") or "",
                    "method": await form.get_attribute("method") or "get",
                    "fields": []
                }
                
                # Поля ввода
                inputs = await form.query_selector_all("input")
                for inp in inputs:
                    field_type = await inp.get_attribute("type") or "text"
                    field_name = await inp.get_attribute("name") or ""
                    field_placeholder = await inp.get_attribute("placeholder") or ""
                    
                    form_info["fields"].append({
                        "type": field_type,
                        "name": field_name,
                        "placeholder": field_placeholder
                    })
                
                forms.append(form_info)
            
            return forms
            
        except Exception:
            return []
    
    async def _take_screenshot(self, page: Page, url: str) -> Optional[str]:
        """Сделать скриншот страницы"""
        try:
            # Создаем имя файла из URL
            parsed_url = urlparse(url)
            filename = f"screenshot_{parsed_url.netloc}_{int(time.time())}.png"
            screenshot_path = f"screenshots/{filename}"
            
            # Делаем скриншот
            await page.screenshot(path=screenshot_path, full_page=True)
            return screenshot_path
            
        except Exception:
            return None
    
    async def _get_additional_info(self, url: str) -> Dict[str, Any]:
        """Получить дополнительную информацию через requests"""
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            return {
                "status_code": response.status_code
            }
        except Exception:
            return {"status_code": 0}