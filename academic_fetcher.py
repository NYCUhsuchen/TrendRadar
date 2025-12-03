# coding=utf-8
"""
學術平台數據獲取模組
支持 arXiv, PubMed, Google Scholar 等學術論文平台
"""

import time
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from urllib.parse import quote


class AcademicFetcher:
    """學術平台數據獲取器"""
    
    def __init__(self, proxy_url: Optional[str] = None):
        self.proxy_url = proxy_url
        self.proxies = None
        if proxy_url:
            self.proxies = {"http": proxy_url, "https": proxy_url}
    
    def fetch_arxiv_papers(
        self,
        query: str,
        max_results: int = 50,
        sort_by: str = "submittedDate",
        sort_order: str = "descending"
    ) -> List[Dict]:
        """
        從 arXiv 獲取論文
        
        Args:
            query: 搜索查詢（例如："cat:cs.AI" 或 "ti:machine learning"）
            max_results: 最大結果數
            sort_by: 排序方式 (submittedDate, lastUpdatedDate, relevance)
            sort_order: 排序順序 (ascending, descending)
        
        Returns:
            論文列表，每篇論文包含 title, authors, summary, url, published 等信息
        """
        base_url = "http://export.arxiv.org/api/query"
        
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Academic Paper Monitor)",
        }
        
        try:
            print(f"正在從 arXiv 獲取論文: {query}")
            response = requests.get(
                base_url,
                params=params,
                headers=headers,
                proxies=self.proxies,
                timeout=30
            )
            response.raise_for_status()
            
            # 解析 XML 響應
            papers = self._parse_arxiv_xml(response.text)
            print(f"成功獲取 {len(papers)} 篇 arXiv 論文")
            
            return papers
            
        except Exception as e:
            print(f"獲取 arXiv 論文失敗: {e}")
            return []
    
    def _parse_arxiv_xml(self, xml_text: str) -> List[Dict]:
        """解析 arXiv API 返回的 XML"""
        papers = []
        
        try:
            root = ET.fromstring(xml_text)
            
            # arXiv API 使用 Atom 命名空間
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            for entry in root.findall('atom:entry', ns):
                try:
                    # 提取基本信息
                    title_elem = entry.find('atom:title', ns)
                    title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else ""
                    
                    summary_elem = entry.find('atom:summary', ns)
                    summary = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None else ""
                    
                    # 提取作者
                    authors = []
                    for author in entry.findall('atom:author', ns):
                        name_elem = author.find('atom:name', ns)
                        if name_elem is not None:
                            authors.append(name_elem.text.strip())
                    
                    # 提取 URL
                    url = ""
                    for link in entry.findall('atom:link', ns):
                        if link.get('title') == 'pdf':
                            url = link.get('href', '')
                            break
                    if not url:
                        id_elem = entry.find('atom:id', ns)
                        url = id_elem.text.strip() if id_elem is not None else ""
                    
                    # 提取發布日期
                    published_elem = entry.find('atom:published', ns)
                    published = published_elem.text.strip() if published_elem is not None else ""
                    
                    # 提取分類
                    categories = []
                    for category in entry.findall('atom:category', ns):
                        term = category.get('term', '')
                        if term:
                            categories.append(term)
                    
                    paper = {
                        "title": title,
                        "authors": authors,
                        "summary": summary[:300] + "..." if len(summary) > 300 else summary,  # 限制摘要長度
                        "url": url,
                        "published": published,
                        "categories": categories,
                        "source": "arXiv"
                    }
                    
                    papers.append(paper)
                    
                except Exception as e:
                    print(f"解析單篇 arXiv 論文時出錯: {e}")
                    continue
                    
        except Exception as e:
            print(f"解析 arXiv XML 時出錯: {e}")
        
        return papers
    
    def fetch_pubmed_papers(
        self,
        query: str,
        max_results: int = 50,
        days_back: int = 7
    ) -> List[Dict]:
        """
        從 PubMed 獲取論文（使用 E-utilities API）
        
        Args:
            query: 搜索查詢
            max_results: 最大結果數
            days_back: 獲取最近幾天的論文
        
        Returns:
            論文列表
        """
        # PubMed E-utilities API 需要兩步：搜索 + 獲取詳情
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        
        # 第一步：搜索獲取 ID 列表
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "pub_date",
            "reldate": days_back
        }
        
        try:
            print(f"正在從 PubMed 搜索論文: {query}")
            search_response = requests.get(
                search_url,
                params=search_params,
                proxies=self.proxies,
                timeout=30
            )
            search_response.raise_for_status()
            search_data = search_response.json()
            
            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            
            if not id_list:
                print("PubMed 搜索未找到論文")
                return []
            
            print(f"找到 {len(id_list)} 篇 PubMed 論文，正在獲取詳情...")
            
            # 第二步：獲取論文詳情
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "xml"
            }
            
            time.sleep(0.5)  # API 限流
            
            fetch_response = requests.get(
                fetch_url,
                params=fetch_params,
                proxies=self.proxies,
                timeout=30
            )
            fetch_response.raise_for_status()
            
            papers = self._parse_pubmed_xml(fetch_response.text)
            print(f"成功獲取 {len(papers)} 篇 PubMed 論文詳情")
            
            return papers
            
        except Exception as e:
            print(f"獲取 PubMed 論文失敗: {e}")
            return []
    
    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict]:
        """解析 PubMed XML 響應"""
        papers = []
        
        try:
            root = ET.fromstring(xml_text)
            
            for article in root.findall('.//PubmedArticle'):
                try:
                    # 提取標題
                    title_elem = article.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else ""
                    
                    # 提取摘要
                    abstract_elem = article.find('.//AbstractText')
                    abstract = abstract_elem.text if abstract_elem is not None else ""
                    
                    # 提取作者
                    authors = []
                    for author in article.findall('.//Author'):
                        lastname = author.find('LastName')
                        forename = author.find('ForeName')
                        if lastname is not None:
                            name = lastname.text
                            if forename is not None:
                                name = f"{forename.text} {name}"
                            authors.append(name)
                    
                    # 提取 PMID
                    pmid_elem = article.find('.//PMID')
                    pmid = pmid_elem.text if pmid_elem is not None else ""
                    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
                    
                    # 提取發布日期
                    pub_date = article.find('.//PubDate')
                    published = ""
                    if pub_date is not None:
                        year = pub_date.find('Year')
                        month = pub_date.find('Month')
                        day = pub_date.find('Day')
                        if year is not None:
                            published = year.text
                            if month is not None:
                                published = f"{published}-{month.text}"
                            if day is not None:
                                published = f"{published}-{day.text}"
                    
                    paper = {
                        "title": title.strip() if title else "",
                        "authors": authors,
                        "summary": abstract[:300] + "..." if abstract and len(abstract) > 300 else abstract,
                        "url": url,
                        "published": published,
                        "source": "PubMed",
                        "pmid": pmid
                    }
                    
                    papers.append(paper)
                    
                except Exception as e:
                    print(f"解析單篇 PubMed 論文時出錯: {e}")
                    continue
                    
        except Exception as e:
            print(f"解析 PubMed XML 時出錯: {e}")
        
        return papers
    
    def format_for_trendradar(
        self,
        papers: List[Dict],
        platform_id: str,
        platform_name: str
    ) -> Tuple[Dict, Dict]:
        """
        將學術論文格式化為 TrendRadar 格式
        
        Args:
            papers: 論文列表
            platform_id: 平台 ID（如 "arxiv"）
            platform_name: 平台名稱（如 "arXiv"）
        
        Returns:
            (results, id_to_name) 元組，格式與原 DataFetcher 相同
        """
        results = {platform_id: {}}
        id_to_name = {platform_id: platform_name}
        
        for idx, paper in enumerate(papers, 1):
            # 構建標題（包含作者信息）
            title = paper['title']
            if paper.get('authors'):
                # 只顯示前 3 位作者
                author_str = ", ".join(paper['authors'][:3])
                if len(paper['authors']) > 3:
                    author_str += ", et al."
                title = f"{title} ({author_str})"
            
            results[platform_id][title] = {
                "ranks": [idx],
                "url": paper.get('url', ''),
                "mobileUrl": paper.get('url', ''),
                "metadata": {
                    "published": paper.get('published', ''),
                    "summary": paper.get('summary', ''),
                    "source": paper.get('source', ''),
                }
            }
        
        return results, id_to_name


def crawl_academic_platforms(
    platforms: List[Dict],
    request_interval: int = 1000,
    proxy_url: Optional[str] = None
) -> Tuple[Dict, Dict, List]:
    """
    爬取多個學術平台
    
    Args:
        platforms: 平台配置列表，每個配置包含:
            - id: 平台 ID
            - name: 平台名稱
            - type: 平台類型 (arxiv, pubmed)
            - query: 搜索查詢
            - max_results: 最大結果數
        request_interval: 請求間隔（毫秒）
        proxy_url: 代理 URL
    
    Returns:
        (results, id_to_name, failed_ids) 元組
    """
    fetcher = AcademicFetcher(proxy_url)
    all_results = {}
    all_id_to_name = {}
    failed_ids = []
    
    for i, platform in enumerate(platforms):
        platform_id = platform['id']
        platform_name = platform.get('name', platform_id)
        platform_type = platform.get('type', 'arxiv')
        query = platform.get('query', '')
        max_results = platform.get('max_results', 50)
        
        print(f"\n處理平台: {platform_name} ({platform_type})")
        
        try:
            if platform_type == 'arxiv':
                papers = fetcher.fetch_arxiv_papers(query, max_results)
            elif platform_type == 'pubmed':
                days_back = platform.get('days_back', 7)
                papers = fetcher.fetch_pubmed_papers(query, max_results, days_back)
            else:
                print(f"不支持的平台類型: {platform_type}")
                failed_ids.append(platform_id)
                continue
            
            if papers:
                results, id_to_name = fetcher.format_for_trendradar(
                    papers, platform_id, platform_name
                )
                all_results.update(results)
                all_id_to_name.update(id_to_name)
            else:
                failed_ids.append(platform_id)
                
        except Exception as e:
            print(f"處理平台 {platform_name} 時出錯: {e}")
            failed_ids.append(platform_id)
        
        # 請求間隔
        if i < len(platforms) - 1:
            time.sleep(request_interval / 1000)
    
    print(f"\n成功: {list(all_results.keys())}, 失敗: {failed_ids}")
    return all_results, all_id_to_name, failed_ids
