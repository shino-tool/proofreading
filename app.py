import streamlit as st
import os
import sys

# Add the current directory to sys.path to ensure modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from modules import humanizer, seo, rules, proofread, utils

st.set_page_config(
    page_title="AI Writing Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("AI ライティング & SEO オプティマイザー")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    
    st.divider()
    
    st.divider()
    
    # model_name = st.selectbox("使用モデル", ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-3-pro-preview"], index=0)
    # User restriction:
    model_name = "gemini-3-pro-preview"
    st.caption(f"使用モデル: {model_name}")
    
    mode = st.radio("処理モード", ["単一記事", "一括処理 (CSV/Spreadsheet)"])
    
    st.divider()
    
    # Global Settings for Bulk & Single
    st.subheader("SEO設定 (Google Search)")
    google_cse_id = st.text_input("Custom Search Engine ID (cx)")
    
    st.divider()
    st.info("処理順序:\n1. ヒューマナイズ\n2. SEO最適化\n3. 独自ルール\n4. 文法チェック")

# --- Main Content ---

if mode == "単一記事":
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("原稿入力")
        input_text = st.text_area("ここに原稿を入力してください (Markdown対応)", height=400)
        target_kw = st.text_input("狙うキーワード (例: 格安SIM おすすめ)")
        
    with col2:
        st.subheader("処理フロー設定")
        
        # Step 2: Humanizer
        with st.expander("② ヒューマナイズ設定", expanded=True):
            humanize_enabled = st.checkbox("有効にする", value=True, key="h_enable")
            creativity = st.slider("ゆらぎ度 (Temperature)", 0.0, 1.0, 0.7)
            
        # Step 3: SEO Optimizer
        with st.expander("③ SEO最適化設定"):
            seo_enabled = st.checkbox("有効にする", value=True, key="s_enable")
            if seo_enabled and not google_cse_id:
                st.caption("※SEO機能の一部（リアルタイム検索）にはサイドバーでのEngine ID設定が必要です。設定がない場合はLLMの知識ベースを使用します。")
            
        # Step 4: Custom Rules
        with st.expander("④ 独自ルール設定"):
            rules_enabled = st.checkbox("有効にする", value=True, key="r_enable")
            forbidden_words = st.text_area("禁止ワード (カンマ区切り)", "コスパ最強, 絶対")
            custom_check_items = st.text_area("順守すべきチェック項目 (自由記述)", "例：文体は親しみやすく、専門用語は噛み砕く")
            
        # Step 1: Proofreading
        with st.expander("① 文法チェック設定"):
            proofread_enabled = st.checkbox("有効にする", value=True, key="p_enable")
            
    # Action Button
    if st.button("リライト実行", type="primary"):
        if not input_text:
            st.warning("原稿を入力してください。")
        elif not os.environ.get("GOOGLE_API_KEY"):
            st.error("Gemini API Keyを設定してください。")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            current_text = input_text
            
            # 1. Humanize (Module 2)
            if humanize_enabled:
                status_text.text("② ヒューマナイズ実行中...")
                current_text = humanizer.process(current_text, creativity, model_name=model_name)
                st.session_state['result_humanized'] = current_text
                progress_bar.progress(25)
            
            # 2. SEO (Module 3)
            if seo_enabled:
                status_text.text("③ SEO分析・リライト実行中...")
                # Pass global CSE ID
                current_text = seo.process(current_text, target_kw, custom_search_engine_id=google_cse_id, model_name=model_name)
                st.session_state['result_seo'] = current_text
                progress_bar.progress(50)

            # 3. Rules (Module 4)
            if rules_enabled:
                status_text.text("④ 独自ルール適用中...")
                current_text = rules.process(current_text, forbidden_words_str=forbidden_words, check_items_str=custom_check_items, model_name=model_name)
                st.session_state['result_rules'] = current_text
                progress_bar.progress(75)
            
            # 4. Proofread (Module 1)
            if proofread_enabled:
                status_text.text("① 文法チェック実行中...")
                current_text = proofread.process(current_text, model_name=model_name)
                st.session_state['result_proofread'] = current_text
                progress_bar.progress(100)
            
            status_text.text("完了！")
            st.success("すべての処理が完了しました。")
            
            st.subheader("リライト結果")
            
            # Result Visualization Tabs
            res_tab1, res_tab2, res_tab3 = st.tabs(["完了テキスト", "差分確認 (Diff)", "処理履歴"])
            
            with res_tab1:
                st.text_area("完了テキスト", value=current_text, height=600, key="final_output")
                
            with res_tab2:
                st.caption("左：変更前 / 右：変更後")
                col_diff_1, col_diff_2 = st.columns(2)
                with col_diff_1:
                    st.text_area("Original", input_text, height=600, disabled=True)
                with col_diff_2:
                    st.text_area("Rewritten", current_text, height=600, disabled=True)
            
            with res_tab3:
                if 'result_humanized' in st.session_state:
                    st.text_area("Step 2: Humanized", st.session_state['result_humanized'], height=150)
                if 'result_seo' in st.session_state:
                    st.text_area("Step 3: SEO Optimized", st.session_state['result_seo'], height=150)
                if 'result_rules' in st.session_state:
                    st.text_area("Step 4: Rule Applied", st.session_state['result_rules'], height=150)
            
elif mode == "一括処理 (CSV/Spreadsheet)":
    import pandas as pd
    from io import BytesIO
    
    st.subheader("一括処理 (CSV/Excel)")
    uploaded_file = st.file_uploader("ファイルをアップロードしてください", type=["csv", "xlsx"])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.dataframe(df.head())
            
            col_options = df.columns.tolist()
            text_col = st.selectbox("原稿テキストの列を選択", col_options)
            kw_col = st.selectbox("キーワードの列を選択 (オプション)", ["(指定なし)"] + col_options)
            
            # Copy single mode settings for bulk
            with st.expander("各ステップの設定（単一モードと共通）"):
                 humanize_enable_bulk = st.checkbox("ヒューマナイズ", value=True)
                 seo_enable_bulk = st.checkbox("SEO最適化", value=True)
                 rules_enable_bulk = st.checkbox("独自ルール", value=True)
                 proofread_enable_bulk = st.checkbox("文法チェック", value=True)
                 # Sliders and other configs could be mirrored here or shared via session state
            
            if st.button("一括処理開始"):
                if not os.environ.get("GOOGLE_API_KEY"):
                    st.error("API Keyが設定されていません")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    results = []
                    
                    total_rows = len(df)
                    
                    for index, row in df.iterrows():
                        status_text.text(f"Processing row {index + 1}/{total_rows}...")
                        
                        original_text = str(row[text_col])
                        current_text = original_text
                        target_kw = str(row[kw_col]) if kw_col != "(指定なし)" else ""
                        
                        # Pipeline with simplified error handling
                        try:
                            if humanize_enable_bulk:
                                current_text = humanizer.process(current_text, model_name=model_name) 
                            
                            if seo_enable_bulk:
                                current_text = seo.process(current_text, target_kw, custom_search_engine_id=google_cse_id, model_name=model_name)
                                
                            if rules_enable_bulk:
                                current_text = rules.process(current_text, forbidden_words_str="コスパ最強, 絶対", check_items_str="文体は親しみやすく", model_name=model_name) 
                                
                            if proofread_enable_bulk:
                                current_text = proofread.process(current_text, model_name=model_name)
                                
                            results.append(current_text)
                        
                        except Exception as e:
                            results.append(f"Error: {str(e)}")
                        
                        progress_bar.progress((index + 1) / total_rows)
                    
                    df['Rewritten_Text'] = results
                    status_text.text("全件完了しました！")
                    st.success("完了")
                    
                    st.dataframe(df)
                    
                    # Download
                    output = BytesIO()
                    if uploaded_file.name.endswith('.csv'):
                        df.to_csv(output, index=False)
                        mime = 'text/csv'
                        fn = 'rewritten_results.csv'
                    else:
                        df.to_excel(output, index=False)
                        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        fn = 'rewritten_results.xlsx'
                        
                    st.download_button("結果ファイルをダウンロード", data=output.getvalue(), file_name=fn, mime=mime)

        except Exception as e:
            st.error(f"ファイル読み込みエラー: {e}")

