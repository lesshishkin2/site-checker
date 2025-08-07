#!/usr/bin/env python3
"""
Site Checker - AI агент для проверки фишинговых сайтов

Использование:
    python main.py https://example.com
    python main.py --url https://example.com --verbose
"""

import asyncio
import json
import sys
import argparse
from typing import Optional
import os
from dotenv import load_dotenv

from src.agents import SiteAnalyzer


async def analyze_site(url: str, verbose: bool = False) -> None:
    """Анализ сайта и вывод результата"""
    
    if verbose:
        print(f"🔍 Анализ сайта: {url}")
        print("=" * 50)
    
    try:
        # Создаем анализатор
        analyzer = SiteAnalyzer()
        
        if verbose:
            print("📥 Получение содержимого сайта...")
        
        # Выполняем анализ
        report = await analyzer.analyze_site(url)
        
        if verbose:
            print("🤖 AI анализ...")
            print("=" * 50)
        
        # Выводим результат
        print_report(report, verbose)
        
    except Exception as e:
        print(f"❌ Ошибка при анализе: {e}", file=sys.stderr)
        sys.exit(1)


def print_report(report, verbose: bool = False) -> None:
    """Красивый вывод отчета"""
    
    result = report.analysis_result
    
    # Основная информация
    print(f"🌐 URL: {result.url}")
    print(f"⚠️  Риск: {result.risk_score:.1f}/10")
    print(f"🎯 Уверенность: {result.confidence:.0%}")
    print(f"📊 Рекомендация: {result.recommendation}")
    
    # Детали анализа
    if result.suspicious_elements:
        print(f"\\n🚨 Подозрительные элементы:")
        for element in result.suspicious_elements:
            print(f"  • {element}")
    
    if result.legitimate_indicators:
        print(f"\\n✅ Признаки легитимности:")
        for indicator in result.legitimate_indicators:
            print(f"  • {indicator}")
    
    # Флаги безопасности
    if verbose:
        flags = result.security_flags
        print(f"\\n🔒 Флаги безопасности:")
        print(f"  • HTTPS: {'✅' if flags.has_https else '❌'}")
        print(f"  • Подозрительные слова: {'⚠️' if flags.has_suspicious_keywords else '✅'}")
        print(f"  • Формы входа: {'⚠️' if flags.has_login_forms else '✅'}")
        print(f"  • Формы оплаты: {'⚠️' if flags.has_payment_forms else '✅'}")
    
    # Имитация брендов
    if result.brand_impersonation:
        print(f"\\n👥 Возможная имитация: {result.brand_impersonation}")
    
    # Пояснение
    print(f"\\n💭 Объяснение:")
    print(f"  {result.explanation}")
    
    # Техническая информация
    if verbose:
        print(f"\\n📈 Техническая информация:")
        print(f"  • Время обработки: {report.processing_time:.2f}с")
        print(f"  • Время ответа сайта: {report.site_content.response_time:.2f}с")
        print(f"  • Статус код: {report.site_content.status_code}")
        
        if report.errors:
            print(f"  • Ошибки: {', '.join(report.errors)}")


def setup_environment() -> None:
    """Настройка переменных окружения"""
    load_dotenv()
    
    # Проверяем наличие ключа OpenAI
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Предупреждение: OPENAI_API_KEY не найден в переменных окружения")
        print("   Будет использован упрощенный анализ без AI")
        print("   Создайте файл .env с вашим ключом OpenAI для полной функциональности")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Site Checker - AI агент для проверки фишинговых сайтов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py https://example.com
  python main.py --url https://suspicious-site.com --verbose
  python main.py https://paypal-security.fake --verbose
        """
    )
    
    parser.add_argument(
        "url", 
        nargs="?",
        help="URL сайта для анализа"
    )
    
    parser.add_argument(
        "--url",
        help="URL сайта для анализа (альтернативный способ)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Подробный вывод"
    )
    
    parser.add_argument(
        "--json",
        action="store_true", 
        help="Вывод в формате JSON"
    )
    
    args = parser.parse_args()
    
    # Определяем URL
    url = args.url or getattr(args, 'url', None)
    if not url:
        parser.print_help()
        sys.exit(1)
    
    # Проверяем формат URL
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    
    # Настройка окружения
    setup_environment()
    
    # Запуск анализа
    try:
        if args.verbose:
            print("🚀 Site Checker - AI Phishing Detection")
            print("=" * 50)
        
        asyncio.run(analyze_site(url, args.verbose))
        
    except KeyboardInterrupt:
        print("\\n❌ Анализ прерван пользователем")
        sys.exit(1)


if __name__ == "__main__":
    main()