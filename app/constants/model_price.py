from utils import GenerativeAIModel

MODEL_PRICES = {
    "input": {
        GenerativeAIModel.GPT_4O.value: 2.5 / 1_000_000,
        GenerativeAIModel.GEMINI_PRO.value: 3.5 / 1_000_000,
        GenerativeAIModel.CLAUDE_SONNET.value: 3 / 1_000_000,
    },
    "output": {
        GenerativeAIModel.GPT_4O.value: 10 / 1_000_000,
        GenerativeAIModel.GEMINI_PRO.value: 10.5 / 1_000_000,
        GenerativeAIModel.CLAUDE_SONNET.value: 15 / 1_000_000,
    }
}