import asyncio
from datetime import datetime
from typing import List, Dict, Any
from agents import Agent, Runner
from ..models import SiteContent, SecurityFlags, AnalysisResult, PhishingReport
from ..services import WebScraper


class SiteAnalyzer:
    """AI агент для анализа сайтов на предмет фишинга"""
    
    def __init__(self):
        self.content_analyzer = Agent(
            name="Site Content Analyzer",
            instructions="""
            Ты эксперт по кибербезопасности, специализирующийся на выявлении фишинговых сайтов.
            
            Анализируй предоставленное содержимое веб-сайта и определи:
            1. Подозрительные элементы, указывающие на фишинг
            2. Легитимные индикаторы
            3. Оценку риска от 0 до 10 (где 10 - максимальный риск фишинга)
            4. Уверенность в анализе от 0 до 1
            
            Обращай внимание на:
            - Подозрительные ключевые слова (urgent, limited time, verify account, suspended)
            - Формы для ввода личных данных (логин, пароль, номера карт)
            - Качество дизайна и орфографические ошибки
            - Подозрительные URL и домены
            - Имитацию известных брендов
            - SSL сертификаты и безопасность
            
            Отвечай в формате JSON с полями:
            - risk_score: float (0-10)
            - confidence: float (0-1)  
            - suspicious_elements: list[str]
            - legitimate_indicators: list[str]
            - recommendation: str
            - explanation: str
            - brand_impersonation: str или null
            """
        )
    
    async def analyze_site(self, url: str) -> PhishingReport:
        """Полный анализ сайта"""
        start_time = datetime.now()
        errors = []
        
        try:
            # Получаем содержимое сайта
            async with WebScraper() as scraper:
                site_content = await scraper.scrape_site(url)
            
            # Анализируем содержимое с помощью AI агента
            analysis_result = await self._analyze_content(site_content)
            
            # Подсчитываем время обработки
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return PhishingReport(
                site_content=site_content,
                analysis_result=analysis_result,
                processing_time=processing_time,
                errors=errors
            )
            
        except Exception as e:
            errors.append(f"Analysis error: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Возвращаем базовый отчет с ошибкой
            return PhishingReport(
                site_content=SiteContent(
                    url=url,
                    html_content="",
                    text_content=f"Error: {str(e)}"
                ),
                analysis_result=AnalysisResult(
                    url=url,
                    risk_score=5.0,
                    confidence=0.1,
                    security_flags=SecurityFlags(),
                    recommendation="Unable to analyze due to error",
                    explanation=f"Analysis failed: {str(e)}"
                ),
                processing_time=processing_time,
                errors=errors
            )
    
    async def _analyze_content(self, site_content: SiteContent) -> AnalysisResult:
        """Анализ содержимого сайта с помощью AI"""
        
        # Подготавливаем данные для анализа
        content_summary = self._prepare_content_summary(site_content)
        
        # Определяем флаги безопасности
        security_flags = self._analyze_security_flags(site_content)
        
        # Запускаем AI анализ
        try:
            ai_analysis = await Runner.run(
                self.content_analyzer,
                f"Проанализируй этот веб-сайт на предмет фишинга:\\n\\n{content_summary}"
            )
            
            # Парсим ответ AI (предполагаем JSON формат)
            ai_result = self._parse_ai_response(ai_analysis.final_output)
            
        except Exception as e:
            # Fallback анализ без AI
            ai_result = self._fallback_analysis(site_content)
        
        return AnalysisResult(
            url=site_content.url,
            risk_score=ai_result.get("risk_score", 5.0),
            confidence=ai_result.get("confidence", 0.5),
            security_flags=security_flags,
            suspicious_elements=ai_result.get("suspicious_elements", []),
            legitimate_indicators=ai_result.get("legitimate_indicators", []),
            recommendation=ai_result.get("recommendation", "Requires manual review"),
            explanation=ai_result.get("explanation", "Automated analysis completed"),
            brand_impersonation=ai_result.get("brand_impersonation")
        )
    
    def _prepare_content_summary(self, site_content: SiteContent) -> str:
        """Подготовка краткого содержимого для анализа"""
        summary_parts = []
        
        summary_parts.append(f"URL: {site_content.url}")
        
        if site_content.title:
            summary_parts.append(f"Title: {site_content.title}")
        
        if site_content.meta_description:
            summary_parts.append(f"Meta Description: {site_content.meta_description}")
        
        # Берем первые 1000 символов текста
        if site_content.text_content:
            text_preview = site_content.text_content[:1000]
            summary_parts.append(f"Text Content Preview: {text_preview}")
        
        # Информация о формах
        if site_content.forms:
            forms_info = []
            for form in site_content.forms[:3]:  # Первые 3 формы
                form_fields = [field.get("type", "unknown") for field in form.get("fields", [])]
                forms_info.append(f"Form with fields: {', '.join(form_fields)}")
            summary_parts.append(f"Forms: {'; '.join(forms_info)}")
        
        # Количество ссылок
        if site_content.links:
            summary_parts.append(f"Links count: {len(site_content.links)}")
        
        return "\\n".join(summary_parts)
    
    def _analyze_security_flags(self, site_content: SiteContent) -> SecurityFlags:
        """Анализ флагов безопасности"""
        url_str = str(site_content.url)
        
        # Проверка HTTPS
        has_https = url_str.startswith("https://")
        
        # Проверка подозрительных ключевых слов
        suspicious_keywords = [
            "urgent", "verify", "suspended", "limited time", "act now",
            "confirm", "update", "security alert", "locked", "expires"
        ]
        text_lower = site_content.text_content.lower()
        has_suspicious_keywords = any(keyword in text_lower for keyword in suspicious_keywords)
        
        # Проверка форм входа
        has_login_forms = any(
            any(field.get("type") == "password" for field in form.get("fields", []))
            for form in site_content.forms
        )
        
        # Проверка форм оплаты
        payment_field_types = ["email", "text", "password", "tel"]
        has_payment_forms = any(
            len([f for f in form.get("fields", []) if f.get("type") in payment_field_types]) > 2
            for form in site_content.forms
        )
        
        return SecurityFlags(
            has_https=has_https,
            has_valid_certificate=has_https,  # Упрощенная проверка
            has_suspicious_keywords=has_suspicious_keywords,
            has_login_forms=has_login_forms,
            has_payment_forms=has_payment_forms,
            is_blacklisted=False  # Требует интеграции с blacklist API
        )
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Парсинг ответа AI"""
        try:
            import json
            # Пытаемся найти JSON в ответе
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except Exception:
            pass
        
        # Fallback - базовый анализ на основе ключевых слов в ответе
        return self._extract_from_text_response(response)
    
    def _extract_from_text_response(self, response: str) -> Dict[str, Any]:
        """Извлечение информации из текстового ответа"""
        response_lower = response.lower()
        
        # Определяем риск на основе ключевых слов
        high_risk_indicators = ["high risk", "phishing", "suspicious", "fake", "scam"]
        low_risk_indicators = ["legitimate", "safe", "low risk", "trusted"]
        
        risk_score = 5.0
        if any(indicator in response_lower for indicator in high_risk_indicators):
            risk_score = 8.0
        elif any(indicator in response_lower for indicator in low_risk_indicators):
            risk_score = 2.0
        
        return {
            "risk_score": risk_score,
            "confidence": 0.6,
            "suspicious_elements": ["AI analysis inconclusive"],
            "legitimate_indicators": [],
            "recommendation": "Manual review recommended",
            "explanation": "AI response could not be parsed properly",
            "brand_impersonation": None
        }
    
    def _fallback_analysis(self, site_content: SiteContent) -> Dict[str, Any]:
        """Упрощенный анализ без AI"""
        risk_factors = 0
        suspicious_elements = []
        legitimate_indicators = []
        
        # Проверка HTTPS
        if not str(site_content.url).startswith("https://"):
            risk_factors += 2
            suspicious_elements.append("No HTTPS encryption")
        else:
            legitimate_indicators.append("HTTPS encryption present")
        
        # Проверка подозрительных слов
        suspicious_words = ["urgent", "verify", "suspended", "expires"]
        text_lower = site_content.text_content.lower()
        found_suspicious = [word for word in suspicious_words if word in text_lower]
        if found_suspicious:
            risk_factors += len(found_suspicious)
            suspicious_elements.extend([f"Suspicious keyword: {word}" for word in found_suspicious])
        
        # Проверка форм
        if site_content.forms:
            has_password_forms = any(
                any(field.get("type") == "password" for field in form.get("fields", []))
                for form in site_content.forms
            )
            if has_password_forms:
                risk_factors += 1
                suspicious_elements.append("Password input forms detected")
        
        risk_score = min(risk_factors * 1.5, 10.0)
        
        return {
            "risk_score": risk_score,
            "confidence": 0.7,
            "suspicious_elements": suspicious_elements,
            "legitimate_indicators": legitimate_indicators,
            "recommendation": "Low risk" if risk_score < 3 else "Medium risk" if risk_score < 7 else "High risk",
            "explanation": f"Rule-based analysis found {risk_factors} risk factors",
            "brand_impersonation": None
        }