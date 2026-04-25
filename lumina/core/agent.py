import json
import requests
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..tools.base import ToolRegistry
from .prompts import SYSTEM_PROMPT

class LLMProvider(ABC):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def generate(self, system_prompt: str, history: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
        pass

class GeminiProvider(LLMProvider):
    def generate(self, system_prompt: str, history: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": history,
            "system_instruction": {"parts": [{"text": system_prompt}]}
        }
        if tools:
            payload["tools"] = [{"function_declarations": tools}]
        
        response = requests.post(api_url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Gemini Error: {response.text}")
        
        data = response.json()
        tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
        return data["candidates"][0]["content"], tokens

class OpenAIProvider(LLMProvider):
    def generate(self, system_prompt: str, history: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        messages = [{"role": "system", "content": system_prompt}]
        for h in history:
            role = "assistant" if h["role"] == "model" else h["role"]
            text = "".join([p.get("text", "") for p in h.get("parts", [])])
            if text: messages.append({"role": role, "content": text})

        payload = {"model": self.model, "messages": messages}
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"OpenAI Error: {response.text}")
        
        text = response.json()["choices"][0]["message"]["content"]
        return {"role": "model", "parts": [{"text": text}]}

class AnthropicProvider(LLMProvider):
    def generate(self, system_prompt: str, history: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        api_url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        messages = []
        for h in history:
            role = "assistant" if h["role"] == "model" else h["role"]
            text = "".join([p.get("text", "") for p in h.get("parts", [])])
            if text: messages.append({"role": role, "content": text})

        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": messages,
            "max_tokens": 4096
        }
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Anthropic Error: {response.text}")
        data = response.json()
        text = data["content"][0]["text"]
        tokens = data.get("usage", {}).get("output_tokens", 0) + data.get("usage", {}).get("input_tokens", 0)
        return {"role": "model", "parts": [{"text": text}]}, tokens

class OpenRouterProvider(LLMProvider):
    def generate(self, system_prompt: str, history: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = [{"role": "system", "content": system_prompt}]
        for h in history:
            role = "assistant" if h["role"] == "model" else h["role"]
            text = "".join([p.get("text", "") for p in h.get("parts", [])])
            if text: messages.append({"role": role, "content": text})

        payload = {"model": self.model, "messages": messages}
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"OpenRouter Error: {response.text}")
        
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        return {"role": "model", "parts": [{"text": text}]}, tokens

class GroqProvider(LLMProvider):
    def generate(self, system_prompt: str, history: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
        api_url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = [{"role": "system", "content": system_prompt}]
        for h in history:
            role = "assistant" if h["role"] == "model" else h["role"]
            text = "".join([p.get("text", "") for p in h.get("parts", [])])
            if text: messages.append({"role": role, "content": text})

        payload = {"model": self.model, "messages": messages}
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Groq Error: {response.text}")
        
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        return {"role": "model", "parts": [{"text": text}]}, tokens

class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "llama3"):
        super().__init__("", model)
        self.api_url = "http://localhost:11434/api/chat"

    def generate(self, system_prompt: str, history: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
        messages = [{"role": "system", "content": system_prompt}]
        for h in history:
            role = "assistant" if h["role"] == "model" else h["role"]
            text = "".join([p.get("text", "") for p in h.get("parts", [])])
            if text: messages.append({"role": role, "content": text})

        payload = {"model": self.model, "messages": messages, "stream": False}
        response = requests.post(self.api_url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Ollama Error: {response.text}")
        data = response.json()
        text = data["message"]["content"]
        tokens = len(text) // 4 # Ollama doesn't return easy tokens in same way
        return {"role": "model", "parts": [{"text": text}]}, tokens

class LuminaAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.history: List[Dict[str, Any]] = []
        self.registry = ToolRegistry()
        self.system_prompt = SYSTEM_PROMPT

    def add_tool_registry(self, registry: ToolRegistry):
        self.registry = registry

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def run(self, user_input: str, on_tool_call: Optional[callable] = None) -> tuple[str, int]:
        self.history.append({"role": "user", "parts": [{"text": user_input}]})
        total_tokens = 0
        
        while True:
            tools = self.registry.to_gemini_tools()
            response_data = self.provider.generate(self.system_prompt, self.history, tools)
            
            # response_data is now a tuple (content, tokens)
            message, tokens = response_data
            total_tokens += tokens
            
            self.history.append(message)
            parts = message.get("parts", [])
            tool_calls = [p.get("functionCall") for p in parts if p.get("functionCall")]
            if not tool_calls:
                text_parts = [p.get("text") for p in parts if p.get("text")]
                return "\n".join(text_parts) if text_parts else "Done.", total_tokens
            
            tool_results = []
            for tc in tool_calls:
                name, args = tc.get("name"), tc.get("args", {})
                if on_tool_call: on_tool_call(name, args)
                tool = self.registry.get_tool(name)
                result = tool.execute(**args) if tool else f"Error: Tool {name} not found."
                tool_results.append({"functionResponse": {"name": name, "response": {"result": result}}})
            self.history.append({"role": "model", "parts": tool_results})
