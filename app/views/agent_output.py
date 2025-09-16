import os
import logging

import streamlit as st
import japanize_matplotlib
from pandasai import Agent
from pandasai.llm import OpenAI
from pandasai.helpers.openai_info import get_openai_callback

from constants import PANDAS_AI_IMG_OUTPUT_PATH, DISPLAY_OPTIONS, PANDAS_AI_ERROR_MESSAGE, GENERATE_CHART_PROMPT
from utils import extract_data_extension, read_file, is_estat_url, is_estat_data, GenerativeAIModel
from session import set_agent_message, get_model_name, set_llm_input_cost, set_llm_output_cost, set_serp_api_results
from services import StreamlitCallbackHandler, calc_input_cost_from_prompt, calc_input_cost, calc_output_cost


class AgentOutput:
    def __init__(self, agent, prompt, file, header):
        self.agent = agent
        self.prompt = prompt
        self.file = file
        self.header = header

    def handle_agent_output(self):
        """
        agentの出力を処理する
        """
        if self.prompt is not None:
            logging.csv_info(f"prompt: {self.prompt}")
            if self.file is not None:
                self._output_with_file()
            else:
                self._output_without_file()

    def _output_without_file(self):
        """
        ファイルをアップロードしていない場合の処理
        Langchainを使用してユーザーの質問に対して適切な処理を実行する
        estatのダウンロードリンク取得やestatのデータの表示を行う
        """
        callback_handler = StreamlitCallbackHandler(st.expander("思考過程"))
        response = self.agent.invoke(
            {'user_input': [self.prompt]},
            config={'callbacks': [callback_handler]}
        )
        logging.csv_info(f"response: {response}")
        
        # 入力コストを計算
        input_cost = calc_input_cost_from_prompt(self.prompt, get_model_name())
        set_llm_input_cost(input_cost, get_model_name())
        
        # agentで実行したtoolの出力コストは計算する方法がないため、計算しない
        # 各tool内でLLMを使用している場合は、それぞれのtool内で計算する

        if isinstance(response, str) and "エラー" in response:
            st.error(response)

        output = response.get('output', '')

        if output == "stat_data_viewer":
            self._display_formatted_estat_data()
        elif is_estat_url(output):
            self._display_estat_url(output)
        elif is_estat_data(output):
            self._display_estat_data(output)
        else:
            self._display_markdown_text(output)

    def _output_with_file(self):
        """
        ファイルをアップロードした場合の処理
        PandasAIを使用して、ユーザーの質問に対して適切なグラフを作成する
        基本的にはDataFrameの形式でPandasDataViewerで表示する
        png形式で出力された場合はエラーとして扱う
        """
        
        logging.csv_info(f"uploaded file: {self.file.name}")
        
        extension = extract_data_extension(self.file)
        
        try:
            df = read_file(self.file, extension, self.header)
        except Exception as e:
            logging.csv_error(e)
            st.error("ファイルの読み込みに失敗しました。")
            return

        with st.chat_message("assistant"):
            st.write(df.head(5)) # データの確認
            agent = Agent(
                df,
                config={
                    "llm": OpenAI(model_name="gpt-4o"),
                    "custom_whitelisted_dependencies": ["plotly"],
                }
            )

            with get_openai_callback() as cb:
                result = agent.chat(GENERATE_CHART_PROMPT.format(user_query=self.prompt))
                prompt_tokens = cb.prompt_tokens
                completion_tokens = cb.completion_tokens
                # 入力コストを計算
                # PansasAIでOpenAIのどのモデルを使用しているか不明なため、GPT_4Oを計算
                input_cost = calc_input_cost(prompt_tokens, GenerativeAIModel.GPT_4O.value)
                set_llm_input_cost(input_cost, GenerativeAIModel.GPT_4O.value)
                
                # 出力コストを計算
                output_cost = calc_output_cost(completion_tokens, GenerativeAIModel.GPT_4O.value)
                set_llm_output_cost(output_cost, GenerativeAIModel.GPT_4O.value)

            # logging.csv_info(f"response: {result}")
            st.expander("思考過程").write(agent.explain())

            if PANDAS_AI_ERROR_MESSAGE in result:
                result = "ファイルの分析中にエラーが発生しました。"
                set_agent_message(
                    content=result,
                )
            else:
                set_agent_message(
                    content=result,
                    with_file=True,
                    is_stat_data=True,
                )

            if os.path.isfile(PANDAS_AI_IMG_OUTPUT_PATH):
                # 画像で出力されてしまった場合のハンドリング
                # ファイルを削除する
                os.remove(PANDAS_AI_IMG_OUTPUT_PATH)
            st.rerun()

    def _display_estat_url(self, output):
        """
        e-StatのURLの概要とURLのボタンを表示する
        """
        
        # serp apiの検索結果を全て格納
        set_serp_api_results(output)
        
        # outputの全要素数を計算
        total_data_count = sum(len(data) for data in output)
        results = output[0]

        with st.chat_message("assistant"):
            from views import EstatDataSummary
            estat_data_summary = EstatDataSummary(data=results, stat_data_index=1)
            set_agent_message(content=estat_data_summary.get_summary())

        urls = [item['link'] for item in results]
        
        content = {
            "urls": urls,
            "next_data_index": 1,
            "total_data_count": total_data_count,
        }

        # ボタン
        if urls and len(urls) > 0:
            set_agent_message(
                content=content,
                with_btns=True,
            )
            st.rerun()

    def _display_estat_data(self, output):
        """
        e-Statのデータを可視化して表示する
        """
        set_agent_message(
            content=output,
            display_type=DISPLAY_OPTIONS[0],
            is_stat_data=True,
        )
        st.rerun()

    def _display_formatted_estat_data(self):
        with st.chat_message("assistant"):
            viewer = st.session_state.messages[-1]["content"]
            viewer.display_data()

    def _display_markdown_text(self, text):
        set_agent_message(content=text)
        st.rerun()
