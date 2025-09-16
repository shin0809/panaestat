from typing import List
import os
import logging

from serpapi.google_search import GoogleSearch

def fetch_estat_urls(serp_api_query: str) -> List:
    """
    e-Statのサイト内検索を行い、検索結果上位のサイト20件を返します。
  
    Args:
      search_query: 検索キーワード
  
    Returns:
        List[dict]: 検索結果の配列
        str: エラーメッセージ
    """

    params = {
        "engine": "google",
        "q": serp_api_query,
        "api_key": os.getenv("SERPAPI_API_KEY"),
        "num": 20  # 上位20件の結果を取得
    }
  
    try:
        logging.csv_info(f"Fetching URLs for query: {serp_api_query}")
        search = GoogleSearch(params)
        results = search.get_dict()
        #logging.csv_info(f"Results: {results}")
        
        if "organic_results" not in results:
            logging.csv_info("No organic results found")
            return [] # 検索結果が見つからなかった場合

        search_results = []
        for _, result in enumerate(results["organic_results"]):
            title = result.get("title", "タイトルなし")
            link = result.get("link", "URLなし")
            snippet = result.get("snippet", "説明文なし")
            
            search_results.append(
                {
                    "title": title,
                    "link": link,
                    "snippet": snippet
                }
            )

        return search_results
  
    except Exception as e:
        logging.csv_error(e)
        raise Exception(f"検索中にエラーが発生しました: {str(e)}")