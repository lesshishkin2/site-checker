from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


class SiteContent(BaseModel):
    """Модель для содержимого сайта"""
    url: HttpUrl
    title: Optional[str] = None
    html_content: str
    text_content: str
    meta_description: Optional[str] = None
    meta_keywords: Optional[List[str]] = None
    links: List[str] = Field(default_factory=list)
    forms: List[Dict[str, Any]] = Field(default_factory=list)
    screenshot_path: Optional[str] = None
    response_time: Optional[float] = None
    status_code: Optional[int] = None


class SecurityFlags(BaseModel):
    """Флаги безопасности сайта"""
    has_https: bool = False
    has_valid_certificate: bool = False
    has_suspicious_keywords: bool = False
    has_login_forms: bool = False
    has_payment_forms: bool = False
    domain_age_days: Optional[int] = None
    is_blacklisted: bool = False


class AnalysisResult(BaseModel):
    """Результат анализа сайта"""
    url: HttpUrl
    risk_score: float = Field(ge=0, le=10, description="Скор риска от 0 до 10")
    confidence: float = Field(ge=0, le=1, description="Уверенность в анализе от 0 до 1")
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    
    # Результаты анализа
    security_flags: SecurityFlags
    suspicious_elements: List[str] = Field(default_factory=list)
    legitimate_indicators: List[str] = Field(default_factory=list)
    
    # Заключение
    recommendation: str
    explanation: str
    
    # Дополнительные данные
    brand_impersonation: Optional[str] = None
    similar_legitimate_sites: List[str] = Field(default_factory=list)


class PhishingReport(BaseModel):
    """Итоговый отчет о проверке на фишинг"""
    site_content: SiteContent
    analysis_result: AnalysisResult
    processing_time: float
    errors: List[str] = Field(default_factory=list)