from .utils import get_gemini_response
import json

def process(text, rules_json_str=None, forbidden_words_str=None, check_items_str=None, model_name="gemini-3-pro-preview"):
    """
    Applies custom rules to the text.
    Uses LLM for complex tonal adjustments, and simple string replacement for strict rules (optional).
    """
    
    rules_instruction = ""
    if rules_json_str:
        # In the future, parse JSON and build prompt
        pass
        
    forbidden_instruction = ""
    if forbidden_words_str:
        forbidden_list = [w.strip() for w in forbidden_words_str.split(",")]
        forbidden_instruction = f"""
        * **禁止ワード**: 以下の単語は絶対に使用しないでください。別の表現に言い換えてください。
          リスト: {', '.join(forbidden_list)}
        """
    else:
        # Defaults mentioned in requirements
        forbidden_instruction = "* **禁止ワード**: 「コスパ最強」「絶対」などの誇張表現が含まれている場合は修正してください。"
        
    check_items_instruction = ""
    if check_items_str:
        check_items_instruction = f"""
        * **遵守項目**: 以下の指示を守れているか確認し、守れていない場合は修正してください。
          指示: {check_items_str}
        """

    prompt = f"""
    あなたはWebメディアの編集長です。
    以下のテキストに対して、サイト独自のルール（レギュレーション）を適用して最終確認・修正を行ってください。

    # ルール
    1. **表記ゆれ**: 「スマホ」は「スマートフォン」に、「引越」は「引っ越し」に統一してください。（もし該当語があれば）
    2. **語尾の統一**: 「〜です・〜ます」調（デスマス調）で統一してください。
    3. **禁止ワード・遵守項目の適用**:
    {forbidden_instruction}
    {check_items_instruction}

    # 禁止事項
    * **要約・省略の禁止**: 元のテキストの情報量は100%維持してください。勝手に文章を削ったり、短くまとめたりすることは絶対に禁止です。文字数は極力変えないでください。
    * **HTMLタグの維持**: 入力テキストにHTMLタグが含まれる場合、タグは絶対に削除・変更せず、そのまま維持してください。
    * Markdown形式（**太字**、# 見出し等）は絶対に使用しないでください。
    * 挨拶や「修正しました」等の報告は不要です。本文のみを出力してください。

    # テキスト
    {text}

    # 修正後のテキスト（プレーンテキストのみ）
    """
    
    return get_gemini_response(prompt, temperature=0.3, model_name=model_name)
