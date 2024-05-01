from __future__ import annotations
from typing import (
    Any,
    AsyncIterator,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    cast,
)
from langchain_google_genai.chat_models import _chat_with_retry,_achat_with_retry,_response_to_result,_parse_chat_history
import google.generativeai as genai 
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessageChunk,
    BaseMessage,
    ChatMessageChunk,
    HumanMessageChunk,
)
from langchain_core.outputs import ChatGenerationChunk, ChatResult
from langchain_core.pydantic_v1 import Field, SecretStr, root_validator
from langchain_core.utils import get_from_dict_or_env


class TUNED_LLM(BaseChatModel):
    model: str = Field(
       
    )
    max_output_tokens: int = Field(default=None, description="Max output tokens")

    client: Any 
    google_api_key: Optional[SecretStr] = None
    temperature: Optional[float] = None
    top_k: Optional[int] = None
    top_p: Optional[int] = None
  
    n: int = Field(default=1, alias="candidate_count")
    
    convert_system_message_to_human: bool = False
    
    client_options: Optional[Dict] = Field(
        None,
       
    )
    transport: Optional[str] = Field(
        None,
        
    )
    class Config:
        allow_population_by_field_name = True

    @property
    def lc_secrets(self) -> Dict[str, str]:
        return {"google_api_key": "GOOGLE_API_KEY"}

    @property
    def _llm_type(self) -> str:
        return "chat-google-generative-ai"

    @property
    def _is_geminiai(self) -> bool:
        return self.model is not None and "gemini" in self.model

    @classmethod
    def is_lc_serializable(self) -> bool:
        return True

    @root_validator(allow_reuse=True)
    def validate_environment(cls, values: Dict) -> Dict:
        allow_reuse=True
        google_api_key = get_from_dict_or_env(
            values, "google_api_key", "GOOGLE_API_KEY"
        )
        if isinstance(google_api_key, SecretStr):
            google_api_key = google_api_key.get_secret_value()

        genai.configure(
            api_key=google_api_key,
            transport=values.get("transport"),
            client_options=values.get("client_options"),
            )
        if (
            values.get("temperature") is not None
            and not 0 <= values["temperature"] <= 1
            ):
            raise ValueError("temperature must be in the range [0.0, 1.0]")

        if values.get("top_p") is not None and not 0 <= values["top_p"] <= 1:
            raise ValueError("top_p must be in the range [0.0, 1.0]")

        if values.get("top_k") is not None and values["top_k"] <= 0:
            raise ValueError("top_k must be positive")
        model = values["model"]
        values["client"] = genai.GenerativeModel(model_name=model)
        return values


    @property
    def _identifying_params(self) -> Dict[str, Any]:
        
        return {
            "model": self.model,
            "temperature": self.temperature,
            "top_k": self.top_k,
            "n": self.n,
        }

    def _prepare_params(
        self, stop: Optional[List[str]], **kwargs: Any
    ) -> Dict[str, Any]:
        gen_config = {
            k: v
            for k, v in {
                "candidate_count": self.n,
                "temperature": self.temperature,
                "stop_sequences": stop,
                "max_output_tokens": self.max_output_tokens,
                "top_k": self.top_k,
                "top_p": self.top_p,
            }.items()
            if v is not None
        }
        if "generation_config" in kwargs:
            gen_config = {**gen_config, **kwargs.pop("generation_config")}
        params = {"generation_config": gen_config, **kwargs}
        return params

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        params, chat, message = self._prepare_chat(messages, stop=stop)
        response: genai.types.GenerateContentResponse = _chat_with_retry(
            content=message,
            **params,
            generation_method=chat.send_message,
        )
        return _response_to_result(response)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        params, chat, message = self._prepare_chat(messages, stop=stop)
        response: genai.types.GenerateContentResponse = await _achat_with_retry(
            content=message,
            **params,
            generation_method=chat.send_message_async,
        )
        return _response_to_result(response)

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        params, chat, message = self._prepare_chat(messages, stop=stop)
        response: genai.types.GenerateContentResponse = _chat_with_retry(
            content=message,
            **params,
            generation_method=chat.send_message,
            stream=True,
        )
        for chunk in response:
            _chat_result = _response_to_result(
                chunk,
                ai_msg_t=AIMessageChunk,
                human_msg_t=HumanMessageChunk,
                chat_msg_t=ChatMessageChunk,
                generation_t=ChatGenerationChunk,
            )
            gen = cast(ChatGenerationChunk, _chat_result.generations[0])
            yield gen
            if run_manager:
                run_manager.on_llm_new_token(gen.text)

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        params, chat, message = self._prepare_chat(messages, stop=stop)
        async for chunk in await _achat_with_retry(
            content=message,
            **params,
            generation_method=chat.send_message_async,
            stream=True,
        ):
            _chat_result = _response_to_result(
                chunk,
                ai_msg_t=AIMessageChunk,
                human_msg_t=HumanMessageChunk,
                chat_msg_t=ChatMessageChunk,
                generation_t=ChatGenerationChunk,
            )
            gen = cast(ChatGenerationChunk, _chat_result.generations[0])
            yield gen
            if run_manager:
                await run_manager.on_llm_new_token(gen.text)

    def _prepare_chat(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Tuple[Dict[str, Any], genai.ChatSession, genai.types.ContentDict]:
        params = self._prepare_params(stop, **kwargs)
        history = _parse_chat_history(
            messages,
            convert_system_message_to_human=self.convert_system_message_to_human,
        )
        message = history.pop()
        chat = self.client.start_chat(history=history)
        return params, chat, message