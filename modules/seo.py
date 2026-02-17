from .utils import get_gemini_response
from .utils import get_gemini_response
import os
from googleapiclient.discovery import build

def get_search_results(query, cx, api_key):
    """
    Fetches search results using Google Custom Search JSON API.
    """
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cx, num=10).execute()
        return res.get('items', [])
    except Exception as e:
        print(f"Search API Error: {e}")
        return []

def analyze_serp_snippets(items, keyword, model_name="gemini-1.5-pro"):
    """
    Extracts keywords from snippets (cheaper/faster than scraping full pages).
    """
    snippets = [item.get('snippet', '') + " " + item.get('title', '') for item in items]
    all_text = "\n".join(snippets)
    
    prompt = f"""
    あなたはSEOの専門家です。
    以下はキーワード「{keyword}」の検索上位サイトのタイトルとディスクリプション（スニペット）のリストです。
    これらを分析し、ユーザーの検索意図を満たすために記事に含めるべき「共起語（関連キーワード）」を10個抽出してください。
    
    # 分析対象テキスト
    {all_text}
    
    # 出力形式
    カンマ区切りの単語リストのみを出力してください。（例: 言葉1, 言葉2, 言葉3...）
    """
    return get_gemini_response(prompt, model_name=model_name)

def mock_serp_analysis(keyword, model_name="gemini-1.5-pro"):
    """
    Fallback mock function.
    """
    prompt = f"""
    あなたはSEOの専門家です。
    キーワード「{keyword}」で検索した際の上位サイトを分析したと仮定し、
    その検索意図を満たすために記事に含めるべき「共起語（関連キーワード）」を10個挙げてください。
    カンマ区切りのリストで出力してください。
    """
    return get_gemini_response(prompt, model_name=model_name)

def process(text, target_keyword, custom_search_engine_id=None, model_name="gemini-1.5-pro"):
    """
    SEO Optimization process.
    1. Analyze/Get related keywords (Real API or Mock).
    2. Check missing keywords.
    3. Rewrite to include them.
    """
    
    api_key = os.environ.get("GOOGLE_API_KEY") 
    
    related_keywords_str = ""
    
    if custom_search_engine_id and api_key and target_keyword:
        items = get_search_results(target_keyword, custom_search_engine_id, api_key)
        if items:
            related_keywords_str = analyze_serp_snippets(items, target_keyword, model_name=model_name)
        else:
            related_keywords_str = mock_serp_analysis(target_keyword, model_name=model_name)
    else:
        # Fallback if no CSE ID provided
        related_keywords_str = mock_serp_analysis(target_keyword, model_name=model_name)
    
    # Step 2: Rewrite
    prompt = f"""
    あなたはSEOライティングのプロです。
    以下の記事を、ターゲットキーワード「{target_keyword}」で上位表示させるためにリライトしてください。

    # SEO要件
    以下の共起語（関連キーワード）を、文章の流れを壊さないように自然に盛り込んでください。
    無理やり詰め込むのではなく、文脈に合わせて補筆・修正を行ってください。

    # 盛り込むべきキーワードリスト
    {related_keywords_str}
    
    # 禁止事項
    * **要約・省略の禁止**: 元のテキストの情報量は100%維持してください。勝手に文章を削ったり、短くまとめたりすることは絶対に禁止です。文字数は極力変えないでください。
    * **HTMLタグの維持**: 入力テキストにHTMLタグが含まれる場合、タグは絶対に削除・変更せず、そのまま維持してください。
    * Markdown形式（**太字**、# 見出し等）は絶対に使用しないでください。ただのプレーンテキストで出力してください。
    * 「記事をリライトしました」などの挨拶や前置きは一切不要です。リライト後の本文のみを出力してください。
    * 「いかがでしたか？」などの無意味な定型文は削除してください。

    # 元のテキスト
    {text}

    # リライト後のテキスト（プレーンテキストのみ）
    """
    
    return get_gemini_response(prompt, temperature=0.5, model_name=model_name) # Lower temperature for SEO precision
