from .utils import get_gemini_response

def process(text, model_name="gemini-3-pro-preview"):
    """
    Final proofreading step.
    """
    
    prompt = f"""
    あなたはベテランの校正者です。
    以下のテキストの誤字脱字、明白な文法ミス、助詞の誤用を修正してください。

    # チェック項目
    * 主語と述語のねじれがないか
    * 助詞（てにをは）が正しいか
    * ら抜き言葉、い抜き言葉があれば修正
    * 誤字脱字

    # 注意
    大きく文章を変える必要はありません。あくまで「校正」の範囲で修正してください。
    
    # 禁止事項
    * Markdown形式（**太字**、# 見出し等）は絶対に使用しないでください。
    * 元のテキストがマークダウンを含んでいない限り、プレーンテキストで返してください。

    # 対象テキスト
    {text}

    # 校正後のテキスト
    """
    
    return get_gemini_response(prompt, temperature=0.1, model_name=model_name)
