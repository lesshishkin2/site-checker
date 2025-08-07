#!/usr/bin/env python3
"""
Пример использования Site Checker API

Демонстрирует различные способы использования агента для анализа сайтов
"""

import asyncio
import json
from src.agents import SiteAnalyzer


async def basic_example():
    """Базовый пример анализа сайта"""
    print("🔍 Базовый пример анализа")
    print("=" * 40)
    
    analyzer = SiteAnalyzer()
    
    # Анализируем легитимный сайт
    report = await analyzer.analyze_site("https://github.com")
    
    print(f"URL: {report.analysis_result.url}")
    print(f"Risk Score: {report.analysis_result.risk_score}/10")
    print(f"Recommendation: {report.analysis_result.recommendation}")
    print(f"Processing Time: {report.processing_time:.2f}s")
    print()


async def detailed_example():
    """Подробный пример с полным отчетом"""
    print("📊 Подробный анализ")
    print("=" * 40)
    
    analyzer = SiteAnalyzer()
    
    # Анализируем сайт с потенциально подозрительным содержимым
    test_urls = [
        "https://example.com",
        "https://google.com", 
        "https://microsoft.com"
    ]
    
    for url in test_urls:
        try:
            print(f"\\nАнализ: {url}")
            print("-" * 30)
            
            report = await analyzer.analyze_site(url)
            result = report.analysis_result
            
            print(f"Risk Score: {result.risk_score:.1f}/10")
            print(f"Confidence: {result.confidence:.0%}")
            
            if result.suspicious_elements:
                print("Suspicious elements:")
                for element in result.suspicious_elements[:3]:
                    print(f"  • {element}")
            
            if result.legitimate_indicators:
                print("Legitimate indicators:")
                for indicator in result.legitimate_indicators[:3]:
                    print(f"  • {indicator}")
            
            print(f"Security flags:")
            flags = result.security_flags
            print(f"  • HTTPS: {flags.has_https}")
            print(f"  • Suspicious keywords: {flags.has_suspicious_keywords}")
            print(f"  • Login forms: {flags.has_login_forms}")
            
        except Exception as e:
            print(f"Error analyzing {url}: {e}")


async def json_output_example():
    """Пример вывода в формате JSON"""
    print("\\n📄 JSON Output Example")
    print("=" * 40)
    
    analyzer = SiteAnalyzer()
    
    try:
        report = await analyzer.analyze_site("https://stackoverflow.com")
        
        # Конвертируем в словарь для JSON serialization
        json_report = {
            "url": str(report.analysis_result.url),
            "risk_score": report.analysis_result.risk_score,
            "confidence": report.analysis_result.confidence,
            "recommendation": report.analysis_result.recommendation,
            "explanation": report.analysis_result.explanation,
            "suspicious_elements": report.analysis_result.suspicious_elements,
            "legitimate_indicators": report.analysis_result.legitimate_indicators,
            "security_flags": {
                "has_https": report.analysis_result.security_flags.has_https,
                "has_suspicious_keywords": report.analysis_result.security_flags.has_suspicious_keywords,
                "has_login_forms": report.analysis_result.security_flags.has_login_forms,
                "has_payment_forms": report.analysis_result.security_flags.has_payment_forms,
            },
            "processing_time": report.processing_time,
            "timestamp": report.analysis_result.analysis_timestamp.isoformat()
        }
        
        print(json.dumps(json_report, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {e}")


async def batch_analysis_example():
    """Пример пакетного анализа нескольких сайтов"""
    print("\\n🔄 Batch Analysis Example")
    print("=" * 40)
    
    urls_to_check = [
        "https://github.com",
        "https://stackoverflow.com",
        "https://reddit.com"
    ]
    
    analyzer = SiteAnalyzer()
    results = []
    
    print("Analyzing multiple sites...")
    
    for i, url in enumerate(urls_to_check, 1):
        try:
            print(f"[{i}/{len(urls_to_check)}] {url}")
            report = await analyzer.analyze_site(url)
            
            results.append({
                "url": str(report.analysis_result.url),
                "risk_score": report.analysis_result.risk_score,
                "recommendation": report.analysis_result.recommendation,
                "processing_time": report.processing_time
            })
            
        except Exception as e:
            print(f"Error with {url}: {e}")
            results.append({
                "url": url,
                "error": str(e),
                "risk_score": None
            })
    
    print("\\nBatch Analysis Results:")
    print("-" * 40)
    for result in results:
        if "error" in result:
            print(f"{result['url']}: ERROR - {result['error']}")
        else:
            print(f"{result['url']}: {result['risk_score']:.1f}/10 - {result['recommendation']}")


async def main():
    """Запуск всех примеров"""
    print("🚀 Site Checker - Usage Examples")
    print("=" * 50)
    
    try:
        await basic_example()
        await detailed_example() 
        await json_output_example()
        await batch_analysis_example()
        
        print("\\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\\n❌ Error running examples: {e}")


if __name__ == "__main__":
    # Убедимся что у нас есть необходимые переменные окружения
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found")
        print("   The examples will use simplified analysis without AI")
        print("   Create a .env file with your OpenAI API key for full functionality\\n")
    
    asyncio.run(main())