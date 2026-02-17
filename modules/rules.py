from .utils import get_gemini_response
import json

def process(text, rules_json_str=None, forbidden_words_str=None, model_name="gemini-1.5-pro"):
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
        以下の単語は「禁止ワード」です。絶対に使用しないでください。もし含まれている場合は、別の表現に言い換えてください。
        禁止ワードリスト: {', '.join(forbidden_list)}
        """
    else:
        # Defaults mentioned in requirements
        forbidden_instruction = "「コスパ最強」「絶対」などの誇張表現が含まれている場合は修正してください。"

    prompt = f"""
    あなたはWebメディアの編集長です。
    以下のテキストに対して、サイト独自のルール（レギュレーション）を適用して最終確認・修正を行ってください。

    # ルール
    1. **表記ゆれ**: 「スマホ」は「スマートフォン」に、「引越」は「引っ越し」に統一してください。（もし該当語があれば）
    2. **語尾の統一**: 「〜です・〜ます」調（デスマス調）で統一してください。
    3. **禁止ワードの排除**:
    {forbidden_instruction}

    # テキスト
    {text}

    # 修正後のテキスト
    """
    
    return get_gemini_response(prompt, temperature=0.3, model_name=model_name)
