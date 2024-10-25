from uuid import UUID
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_core.tools import Tool

from .config import settings

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_core.callbacks import AsyncCallbackHandler, BaseCallbackHandler
from langchain_core.outputs import LLMResult
from typing import Any, Dict, List, Optional
from typing_extensions import override

langchain_cache = SQLiteCache(database_path=".langchain.db")
set_llm_cache(langchain_cache)

import threading
from contextlib import contextmanager
from typing import Any, Generator

import tiktoken
from langchain_community.callbacks.manager import openai_callback_var
from langchain_community.callbacks.openai_info import (
    standardize_model_name,
    MODEL_COST_PER_1K_TOKENS,
    get_openai_token_cost_for_model,
    OpenAICallbackHandler,
)
from langchain_core.outputs import LLMResult

openai_costs = {
    "prompt_tokens": 0,
    "prompt_cost": 0,
    "completion_tokens": 0,
    "completion_cost": 0,
    "total_tokens": 0,
    "total_cost": 0,
}


def reset_openai_costs():
    openai_costs["prompt_tokens"] = 0
    openai_costs["prompt_cost"] = 0
    openai_costs["completion_tokens"] = 0
    openai_costs["completion_cost"] = 0
    openai_costs["total_tokens"] = 0
    openai_costs["total_cost"] = 0


class CostTrackerCallback(OpenAICallbackHandler):
    prompt_tokens: int = 0
    prompt_cost: float = 0
    completion_tokens: int = 0
    completion_cost: float = 0
    total_tokens: int = 0
    total_cost: float = 0

    def __init__(self, model_name="gpt-4o") -> None:
        super().__init__()
        self.model_name = model_name
        self.encoding = tiktoken.encoding_for_model(model_name)
        self._lock = threading.Lock()

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        **kwargs: Any,
    ) -> None:
        """Calculates the prompt token number and cost."""
        prompts_string = "".join(prompts)
        prompt_tokens = len(self.encoding.encode(prompts_string))
        if self.model_name in MODEL_COST_PER_1K_TOKENS:
            prompt_cost = get_openai_token_cost_for_model(
                self.model_name, prompt_tokens
            )
        else:
            prompt_cost = 0

        self.prompt_tokens = prompt_tokens
        self.prompt_cost = prompt_cost

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        text_response = response.generations[0][0].text
        completion_tokens = len(self.encoding.encode(text_response))
        if self.model_name in MODEL_COST_PER_1K_TOKENS:
            completion_cost = get_openai_token_cost_for_model(
                self.model_name, completion_tokens, is_completion=True
            )
        else:
            completion_cost = 0
        self.completion_tokens = completion_tokens
        self.completion_cost = completion_cost
        self.total_tokens = self.prompt_tokens + self.completion_tokens
        self.total_cost = self.prompt_cost + self.completion_cost
        with self._lock:
            openai_costs["prompt_tokens"] += self.prompt_tokens
            openai_costs["prompt_cost"] += self.prompt_cost
            openai_costs["completion_tokens"] += self.completion_tokens
            openai_costs["completion_cost"] += self.completion_cost
            openai_costs["total_tokens"] += self.total_tokens
            openai_costs["total_cost"] += self.total_cost


chatOpenAI = ChatOpenAI(
    seed=123123,
    temperature=0,
    max_retries=30,
    model="gpt-4o-mini",
    api_key=settings.OPENAI_API_KEY,
    callbacks=[CostTrackerCallback("gpt-4o-mini")],
)
openAIEmbeddings = OpenAIEmbeddings(
    model="text-embedding-3-large", api_key=settings.OPENAI_API_KEY
)

search = GoogleSearchAPIWrapper(
    google_api_key=settings.GOOGLE_API_KEY,
    google_cse_id=settings.GOOGLE_CSE_ID,
)

tool = Tool(
    name="google_search",
    description="Search Google for recent results.",
    func=search.run,
)


