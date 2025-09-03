def is_estat_url(data) -> bool:
    """
    e-StatのURLを含むデータかどうかを判断する
    """
    return isinstance(data, dict) and 'search_results' in data and 'urls' in data
    
def is_estat_data(data) -> bool:
    """
    e-Statのデータかどうかを判断する
    """
    return isinstance(data, dict) and 'GET_STATS_DATA' in data