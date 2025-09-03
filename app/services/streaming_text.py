from langchain.schema import AgentAction, AgentFinish
from langchain.callbacks.base import BaseCallbackHandler
import pandas as pd

class StreamlitCallbackHandler(BaseCallbackHandler):
    """
    CallbackHandlerを継承して、Streamlitでの表示を行うクラス
    Agentの思考過程の表示を行う
    """
    def __init__(self, container):
        self.container = container
        self.thought_container = None
        self.observation_container = None
        self.action_container = None
        self.final_answer_container = None

    def on_agent_action(self, action: AgentAction, **kwargs):
        if action.log:
            self.thought_container = self.container.container()
            self.thought_container.markdown(f"**Thought:** {action.log}")

        if action.tool:
            self.action_container = self.container.container()
            self.action_container.markdown(f"**Action:** {action.tool}\n**Action Input:** {action.tool_input}")

    def on_tool_end(self, output: str, **kwargs):
        # ツール実行結果をDataFrameとして表示
        self.observation_container = self.container.container()
        try:
            print("on_tool_end_TRY")
            # data = ast.literal_eval(output)
            df = pd.DataFrame(output)
            self.observation_container.markdown("**Observation:**")
            self.observation_container.dataframe(df)
        except Exception as e:
            # JSONでなければそのまま表示
            print(e)
            self.observation_container.markdown(f"**Observation:** {output}")
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs):
        self.final_answer_container = self.container.container()
        self.final_answer_container.markdown(f"**Final Answer:** {finish.return_values['output']}")

