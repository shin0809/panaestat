import os
import streamlit as st
import time

from services import logout
from utils import (
    zip_logs,
    get_logs_dir_size,
    get_log_files,
    get_oldest_log,
    delete_oldest_log,
    delete_all_logs,
)
from constants import (
    LLM_OPTIONS,
    FETCH_DATA_TYPE,
    SAVE_DATA_OPTIONS,
    DEFAULT_ESTAT_DATA_LIMIT,
    LOGS_ZIP_PATH,
    LOG_DIR,
    MAX_LOGS_DIR_SIZE_MB,
    DEFAULT_USD_JPY_RATE,
    GenerativeAIModel,
    FetchDataType,
)
from session import (
    set_model_name,
    get_user_name,
    set_fetch_data_type,
    set_save_data_option,
    set_estat_data_limit,
    get_llm_costs,
    set_usd_jpy_rate,
)

def init_sidebar(file):
    """サイドバーの初期化と表示を行う関数"""
    
    with st.sidebar:
        # ユーザー名を表示
        st.sidebar.success(f"ようこそ {get_user_name()} さん！")
        
        # ファイルがアップロードされているときはPandasAIで処理を行う
        # データの取得も行えなず、LLMもOpenAIで行うため、非表示とする
        st.sidebar.write("## 基本設定")
        if file is None:
            # データ取得オプション
            fetch_data_type = st.sidebar.selectbox("データの取得方法", options=FETCH_DATA_TYPE)
            set_fetch_data_type(fetch_data_type)
            
            # データ取得オプションがe-Stat　APIの場合はe-Statのデータ取得上限を設定する
            if fetch_data_type == FetchDataType.ESTAT_API.value:
                # e-Statのデータ取得上限
                estat_data_limit = st.sidebar.number_input("e-Statのデータ取得上限", min_value=1, value=DEFAULT_ESTAT_DATA_LIMIT, max_value=500000, step=100000)
                set_estat_data_limit(estat_data_limit)
            
            # LLM 選択
            model_name = st.sidebar.selectbox("生成AIモデル", options=LLM_OPTIONS)
            set_model_name(model_name)
        else:
            st.sidebar.info("ファイルがアップロードされているため、GPT-4oが適用されます。")
            set_model_name(LLM_OPTIONS[0]) # OpenAIを使用
        
        # セッションに統計データを残すかのオプション
        save_data_option = st.sidebar.radio("統計データの保存（セッション内）", options=SAVE_DATA_OPTIONS)
        set_save_data_option(save_data_option)  # OpenAIを使用
        
        # コスト表示
        _display_costs()

        # ログ情報の表示
        _display_log_info()

        # ログアウトボタン
        st.sidebar.button("ログアウト", on_click=logout)

# コスト表示
def _display_costs():
    costs = get_llm_costs()
    openai_costs = costs[GenerativeAIModel.GPT_4O.value]
    anthropic_costs = costs[GenerativeAIModel.CLAUDE_SONNET.value]
    gemini_costs = costs[GenerativeAIModel.GEMINI_PRO.value]
    
    st.sidebar.write("## 推定コスト")
    st.sidebar.write(f"合計: {(openai_costs['input_cost'] + anthropic_costs['input_cost'] + gemini_costs['input_cost'] + openai_costs['output_cost'] + anthropic_costs['output_cost'] + gemini_costs['output_cost']):.5f} 円")
    with st.sidebar.expander("コスト詳細"):
        st.warning("セッション内で使用された推定トークン数を元に算出した推定値であり、実際のコストと異なる可能性があります。また、反映されるまでに時間差が生じる場合があります。")
        
        # USD/JPYのレート
        usd_jpy_rate = st.number_input("USD/JPY", min_value=1.0, value=DEFAULT_USD_JPY_RATE)
        set_usd_jpy_rate(usd_jpy_rate)
        
        st.write(f"### OpenAI: {(openai_costs['input_cost'] + openai_costs['output_cost']):.5f} 円")
        st.write(f"- **入力コスト**: {(openai_costs['input_cost']):.5f} 円")
        st.write(f"- **出力コスト**: {(openai_costs['output_cost']):.5f} 円")
        
        st.write(f"### Gemini: {(gemini_costs['input_cost'] + gemini_costs['output_cost']):.5f} 円")
        st.write(f"- **入力コスト**: {(gemini_costs['input_cost']):.5f} 円")
        st.write(f"- **出力コスト**: {(gemini_costs['output_cost']):.5f} 円")
        
        st.write(f"### Claude: {(anthropic_costs['input_cost'] + anthropic_costs['output_cost']):.5f} 円")
        st.write(f"- **入力コスト**: {(anthropic_costs['input_cost']):.5f} 円")
        st.write(f"- **出力コスト**: {(anthropic_costs['output_cost']):.5f} 円")
        
        
def _display_log_info():
    st.sidebar.write("## 📦 ログ使用容量")
    # ログフォルダの容量表示
    logs_size = get_logs_dir_size()
    st.sidebar.write(f"{logs_size:.2f}MB / {MAX_LOGS_DIR_SIZE_MB}MB")
    
    # 残り5%未満なら警告を表示
    if logs_size / MAX_LOGS_DIR_SIZE_MB >= 0.95:
        st.sidebar.warning("⚠️ 残りログ容量が少ないです。不要なログを削除してください。")
    
    with st.sidebar.expander("ログ管理"):
        st.warning("ログ使用容量の反映には時間差が生じる場合があります。")
        
        st.write("### ダウンロード")
        
        log_files = get_log_files()
        # ZIP作成ボタン
        # ログファイルが存在する場合のみ圧縮オプションを表示
        if log_files:
            if st.button("ログを圧縮 (ZIP作成)"):
                with st.spinner("ログを圧縮中..."):
                    zip_logs()
                st.toast("✅ ログのZIP作成が完了しました！")

        # ZIPダウンロードボタン
        if os.path.exists(LOGS_ZIP_PATH):
            with open(LOGS_ZIP_PATH, "rb") as f:
                st.download_button(
                    label="ZIPをダウンロード",
                    data=f,
                    file_name="logs.zip",
                    mime="application/zip"
                )

        # ログファイルが存在する場合のみ削除オプションを表示
        if log_files:
            st.write("### 削除")
            # 一番古いログを削除
            oldest_file = get_oldest_log()
            if oldest_file:
                st.write(f"📂 一番古いログ:  \n`{os.path.basename(oldest_file)}`")
                
                if st.button("一番古いログを削除"):
                    _confirm_delete_oldest_log(os.path.basename(oldest_file))
                
                if st.button("すべてのログを削除"):
                    _confirm_delete_all_logs()

@st.dialog("確認")
def _confirm_delete_oldest_log(file_name: str):
    st.write(f"`{file_name}` を削除しますか？")
    if st.button("はい"):
        deleted_file = delete_oldest_log()
        if deleted_file:
            st.toast(f"🗑️ 削除しました: `{file_name}`")
        else:
            st.toast(f"⚠️ {file_name}の削除に失敗しました")
        time.sleep(2) # トーストメッセージを見れるようにするための時間
        st.rerun()

@st.dialog("確認")
def _confirm_delete_all_logs():
    st.write("すべてのログを削除しますか？")
    if st.button("はい"):
        delete_all_logs()
        st.toast("🗑️ すべてのログを削除しました")
        time.sleep(2) # トーストメッセージを見れるようにするための時間
        st.rerun()
