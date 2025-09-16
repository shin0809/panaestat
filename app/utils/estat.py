def is_estat_url(data) -> bool:
    """
    e-StatのURLを含むデータかどうかを判断する
    
    Args:
        data: 検証するデータ
        
    Returns:
        bool: 正しい形式の場合True
    """
    # リストでない場合はFalse
    if not isinstance(data, list):
        return False
        
    # 外側の配列の各要素（グループ）をチェック
    for group in data:
        # グループがリストでない場合はFalse
        if not isinstance(group, list):
            return False
            
        # グループ内の各要素をチェック
        for item in group:
            # 辞書型でない場合はFalse
            if not isinstance(item, dict):
                return False
                
            # 必要なキーが全て存在するかチェック
            required_keys = {'title', 'link', 'snippet'}
            if not all(key in item for key in required_keys):
                return False
                
            # 各値が文字列型かチェック
            if not all(isinstance(item[key], str) for key in required_keys):
                return False
    return True
    
def is_estat_data(data) -> bool:
    """
    e-Statのデータかどうかを判断する
    """
    return isinstance(data, dict) and 'GET_STATS_DATA' in data