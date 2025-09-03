def delete_newlines(text: str) -> str:
    """
    テキスト中の改行コードを削除します。

    Args:
        text (str): _description_

    Returns:
        str: _description_
    """
    return text.replace('\n', '').replace('\r', '')