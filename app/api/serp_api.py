from typing import List
from serpapi.google_search import GoogleSearch
import os
import logging

def fetch_estat_urls(serp_api_query: str) -> List[str]:
    """
    e-Statのサイト内検索を行い、検索結果上位のサイト20件を返します。
  
    Args:
      search_query: 検索キーワード
  
    Returns:
        検索結果の文字列（タイトル、URL、説明文を含む）の配列
    """

    params = {
        "engine": "google",
        "q": serp_api_query,
        "api_key": os.getenv("SERPAPI_API_KEY"),
        "num": 20  # 上位20件の結果を取得
    }
  
    try:
        logging.info(f"Fetching URLs for query: {serp_api_query}")
        search = GoogleSearch(params)
        results = search.get_dict()
        #logging.info(f"Results: {results}")
        
        if "organic_results" not in results:
            logging.info("No organic results found")
            return [] # 検索結果が見つからなかった場合

        search_results = []
        for i, result in enumerate(results["organic_results"]):
            title = result.get("title", "タイトルなし")
            link = result.get("link", "URLなし")
            snippet = result.get("snippet", "説明文なし")
            
            search_results.append(
                f"[{i}] {title}\n"
                f"    URL: {link}\n"
                f"    概要: {snippet}\n"
            )
        # logging.info(f"Fetched search results: {search_results}")
        return search_results
  
    except Exception as e:
        logging.exception(e)
        raise Exception(f"検索中にエラーが発生しました: {str(e)}")