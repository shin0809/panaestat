def delete_newlines(text: str) -> str:
    """
    テキスト中の改行コードを削除します。

    Args:
        text (str): _description_

    Returns:
        str: _description_
    """
    return text.replace('\n', '').replace('\r', '')


def extract_statdisp_id(url: str) -> str:
    """
    e-Stat URLからstatdisp_idを抽出します
    
    Args:
        url: e-StatのURL
        
    Returns:
        statdisp_id: 抽出されたstatdisp_id
    """
    # URLに'statdisp_id='が含まれているか確認
    if 'statdisp_id=' not in url:
        return None
    
    # 'statdisp_id='以降の文字列を取得
    statdisp_id = url.split('statdisp_id=')[1]
    
    # '&'で区切られている場合は、最初の部分だけを取得
    if '&' in statdisp_id:
        statdisp_id = statdisp_id.split('&')[0]
        
    # 改行コードを削除
    statdisp_id = delete_newlines(statdisp_id)
        
    return statdisp_id