"""LLM client for interfacing with OpenAI, Anthropic, and other providers."""

import os
from typing import Dict, List, Optional, Any, Literal
import json
from dataclasses import dataclass

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    raw_response: Optional[Any] = None


class LLMClient:
    """Unified client for multiple LLM providers."""
    
    def __init__(
        self,
        provider: Literal["openai", "anthropic"] = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider to use
            api_key: API key (if None, will try to get from environment)
            model: Model name (if None, uses default for provider)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
        """
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Set API key
        if api_key:
            self.api_key = api_key
        elif provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
        elif provider == "anthropic":
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        if not self.api_key:
            raise ValueError(f"No API key provided for {provider}")
        
        # Set model
        if model:
            self.model = model
        elif provider == "openai":
            self.model = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
        elif provider == "anthropic":
            self.model = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
        
        # Initialize client
        if provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not installed. Run: uv add openai")
            self.client = openai.OpenAI(api_key=self.api_key)
        elif provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package not installed. Run: uv add anthropic")
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Generate text using the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (instruction)
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            
        Returns:
            LLMResponse with generated text
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        if self.provider == "openai":
            return self._generate_openai(prompt, system_prompt, temp, tokens)
        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt, system_prompt, temp, tokens)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate using OpenAI API."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            provider="openai",
            model=self.model,
            tokens_used=response.usage.total_tokens if response.usage else None,
            raw_response=response
        )
    
    def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate using Anthropic API."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        response = self.client.messages.create(**kwargs)
        
        # Extract text content
        content = ""
        for block in response.content:
            if hasattr(block, 'text'):
                content += block.text
        
        return LLMResponse(
            content=content,
            provider="anthropic",
            model=self.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
            raw_response=response
        )
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON response from LLM.
        
        Args:
            prompt: User prompt (should ask for JSON)
            system_prompt: System prompt
            temperature: Temperature (lower is better for JSON)
            conversation_history: Previous conversation messages (list of dicts with 'role' and 'content')
            
        Returns:
            Parsed JSON as dictionary
        """
        temp = temperature if temperature is not None else 0.3  # Lower temp for JSON
        
        # Add JSON instruction to prompt if not present
        if "json" not in prompt.lower():
            prompt += "\n\nRespond with valid JSON only."
        
        # Use conversation history if provided
        if conversation_history:
            response = self._generate_with_history(
                prompt=prompt,
                system_prompt=system_prompt,
                conversation_history=conversation_history,
                temperature=temp
            )
        else:
            response = self.generate(prompt, system_prompt, temp)
        
        # Try to parse JSON from response
        content = response.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line (```)
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            content = "\n".join(lines)
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Try to find JSON in the response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            raise ValueError(f"Failed to parse JSON from LLM response: {e}")
    
    def _generate_with_history(
        self,
        prompt: str,
        system_prompt: Optional[str],
        conversation_history: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Generate response with conversation history.
        
        Args:
            prompt: Current user prompt
            system_prompt: System prompt
            conversation_history: Previous conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLMResponse with generated text
        """
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        if self.provider == "openai":
            return self._generate_openai_with_history(
                prompt, system_prompt, conversation_history, temperature, tokens
            )
        elif self.provider == "anthropic":
            return self._generate_anthropic_with_history(
                prompt, system_prompt, conversation_history, temperature, tokens
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _generate_openai_with_history(
        self,
        prompt: str,
        system_prompt: Optional[str],
        conversation_history: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate using OpenAI API with conversation history."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history (excluding the current prompt)
        for msg in conversation_history:
            # Map 'agent' role to 'assistant' for OpenAI
            role = msg.get("role", "user")
            if role == "agent":
                role = "assistant"
            messages.append({
                "role": role,
                "content": msg.get("content", "")
            })
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            provider="openai",
            model=self.model,
            tokens_used=response.usage.total_tokens if response.usage else None,
            raw_response=response
        )
    
    def _generate_anthropic_with_history(
        self,
        prompt: str,
        system_prompt: Optional[str],
        conversation_history: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate using Anthropic API with conversation history."""
        messages = []
        
        # Add conversation history (excluding the current prompt)
        for msg in conversation_history:
            # Map 'agent' role to 'assistant' for Anthropic
            role = msg.get("role", "user")
            if role == "agent":
                role = "assistant"
            messages.append({
                "role": role,
                "content": msg.get("content", "")
            })
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        response = self.client.messages.create(**kwargs)
        
        # Extract text content
        content = ""
        for block in response.content:
            if hasattr(block, 'text'):
                content += block.text
        
        return LLMResponse(
            content=content,
            provider="anthropic",
            model=self.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
            raw_response=response
        )


def get_default_client() -> LLMClient:
    """
    Get default LLM client based on environment variables.
    
    Returns:
        Configured LLMClient
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    # Check which API keys are available
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if provider == "openai" and openai_key:
        return LLMClient(provider="openai")
    elif provider == "anthropic" and anthropic_key:
        return LLMClient(provider="anthropic")
    elif openai_key:
        return LLMClient(provider="openai")
    elif anthropic_key:
        return LLMClient(provider="anthropic")
    else:
        raise ValueError(
            "No LLM API key found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY "
            "in your environment variables."
        )


def test_connection(provider: Optional[str] = None) -> bool:
    """
    Test LLM connection.
    
    Args:
        provider: Provider to test (if None, tests default)
        
    Returns:
        True if connection successful
    """
    try:
        if provider:
            client = LLMClient(provider=provider)
        else:
            client = get_default_client()
        
        # Simple test prompt
        response = client.generate(
            "Say 'ok' if you can read this.",
            max_tokens=10
        )
        
        return len(response.content) > 0
    except Exception:
        return False

