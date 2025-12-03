#!/usr/bin/env python3
# coding=utf-8
"""
學術平台功能測試腳本
測試 arXiv 和 PubMed API 集成是否正常工作
"""

import sys
from academic_fetcher import AcademicFetcher, crawl_academic_platforms


def test_arxiv():
    """測試 arXiv API"""
    print("=" * 60)
    print("測試 arXiv API")
    print("=" * 60)
    
    fetcher = AcademicFetcher()
    
    # 測試按類別搜索
    print("\n1. 測試按類別搜索 (cs.AI)...")
    papers = fetcher.fetch_arxiv_papers("cat:cs.AI", max_results=5)
    
    if papers:
        print(f"✓ 成功獲取 {len(papers)} 篇論文")
        print("\n第一篇論文信息：")
        paper = papers[0]
        print(f"  標題: {paper['title'][:80]}...")
        print(f"  作者: {', '.join(paper['authors'][:3])}")
        print(f"  發布: {paper['published']}")
        print(f"  URL: {paper['url']}")
    else:
        print("✗ 未獲取到論文")
        return False
    
    # 測試關鍵詞搜索
    print("\n2. 測試關鍵詞搜索 (transformer)...")
    papers = fetcher.fetch_arxiv_papers("all:transformer", max_results=3)
    
    if papers:
        print(f"✓ 成功獲取 {len(papers)} 篇論文")
    else:
        print("✗ 未獲取到論文")
        return False
    
    return True


def test_pubmed():
    """測試 PubMed API"""
    print("\n" + "=" * 60)
    print("測試 PubMed API")
    print("=" * 60)
    
    fetcher = AcademicFetcher()
    
    print("\n測試搜索 (artificial intelligence)...")
    papers = fetcher.fetch_pubmed_papers(
        "artificial intelligence",
        max_results=5,
        days_back=30
    )
    
    if papers:
        print(f"✓ 成功獲取 {len(papers)} 篇論文")
        print("\n第一篇論文信息：")
        paper = papers[0]
        print(f"  標題: {paper['title'][:80]}...")
        if paper['authors']:
            print(f"  作者: {', '.join(paper['authors'][:3])}")
        print(f"  發布: {paper['published']}")
        print(f"  PMID: {paper.get('pmid', 'N/A')}")
        print(f"  URL: {paper['url']}")
    else:
        print("✗ 未獲取到論文")
        return False
    
    return True


def test_integration():
    """測試完整集成"""
    print("\n" + "=" * 60)
    print("測試 TrendRadar 格式集成")
    print("=" * 60)
    
    platforms = [
        {
            "id": "arxiv_test",
            "name": "arXiv 測試",
            "type": "arxiv",
            "query": "cat:cs.AI",
            "max_results": 5
        },
        {
            "id": "pubmed_test",
            "name": "PubMed 測試",
            "type": "pubmed",
            "query": "machine learning",
            "max_results": 5,
            "days_back": 30
        }
    ]
    
    print("\n爬取多個學術平台...")
    results, id_to_name, failed_ids = crawl_academic_platforms(
        platforms,
        request_interval=2000
    )
    
    print(f"\n結果統計：")
    print(f"  成功平台: {list(results.keys())}")
    print(f"  失敗平台: {failed_ids}")
    
    for platform_id, titles in results.items():
        platform_name = id_to_name.get(platform_id, platform_id)
        print(f"\n{platform_name}: {len(titles)} 篇論文")
        
        # 顯示前 2 篇
        for idx, (title, data) in enumerate(list(titles.items())[:2], 1):
            print(f"  {idx}. {title[:80]}...")
    
    return len(results) > 0 and len(failed_ids) == 0


def main():
    """主測試函數"""
    print("\n" + "=" * 60)
    print("TrendRadar 學術平台功能測試")
    print("=" * 60)
    
    all_passed = True
    
    # 測試 arXiv
    try:
        if not test_arxiv():
            all_passed = False
    except Exception as e:
        print(f"\n✗ arXiv 測試失敗: {e}")
        all_passed = False
    
    # 測試 PubMed
    try:
        if not test_pubmed():
            all_passed = False
    except Exception as e:
        print(f"\n✗ PubMed 測試失敗: {e}")
        all_passed = False
    
    # 測試集成
    try:
        if not test_integration():
            all_passed = False
    except Exception as e:
        print(f"\n✗ 集成測試失敗: {e}")
        all_passed = False
    
    # 總結
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有測試通過！")
        print("=" * 60)
        return 0
    else:
        print("✗ 部分測試失敗，請檢查錯誤信息")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
