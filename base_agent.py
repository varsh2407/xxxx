import os
import json
import re
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from openai import AzureOpenAI
from architecture import AgentRole

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Enterprise base class for all specialized AI agents."""

    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self, role: AgentRole):
        self.role = role
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_API_KEY"),
            azure_endpoint=os.getenv("AZURE_API_BASE"),
            api_version=os.getenv("AZURE_API_VERSION", "2024-02-01"),
        )
        self.deployment = os.getenv("AZURE_DEPLOYMENT", "gpt-4o")
        self.memory: List[Dict] = []

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Each agent defines its specialized system prompt."""
        pass

    def think(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        json_mode: bool = True,
    ) -> Dict[str, Any]:
        """Main reasoning method with retry logic and structured output."""

        system_prompt = self.get_system_prompt()
        if json_mode:
            system_prompt += """

STRICT OUTPUT RULES:
- Return ONLY valid, parseable JSON
- No markdown code fences (no ```json)
- No explanatory text before or after JSON
- No trailing commas
- All strings must be properly escaped
- Ensure JSON is properly formatted and complete
"""

        formatted_input = self._format_input(user_input, context)
        messages = self.memory + [{"role": "user", "content": formatted_input}]

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.deployment,
                    max_tokens=8000,
                    temperature=0.3,  # Lower temp for more consistent JSON
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *messages,
                    ],
                )

                raw_text = response.choices[0].message.content
                result = self._parse_response(raw_text, json_mode)

                # Update memory with summarized context (avoid token bloat)
                self.memory.append({"role": "user", "content": formatted_input})
                self.memory.append(
                    {
                        "role": "assistant",
                        "content": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
                    }
                )

                return result

            except json.JSONDecodeError as e:
                logger.warning(f"[{self.role.value}] JSON parse error on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                    # Ask the model to fix its output
                    messages.append({
                        "role": "assistant",
                        "content": raw_text
                    })
                    messages.append({
                        "role": "user",
                        "content": "Your previous response was not valid JSON. Please return ONLY valid JSON with no other text."
                    })
                else:
                    logger.error(f"[{self.role.value}] Failed to get valid JSON after {self.MAX_RETRIES} attempts")
                    return {"raw_response": raw_text, "error": str(e)}

            except Exception as e:
                logger.error(f"[{self.role.value}] API error on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                else:
                    raise

        return {"error": "Max retries exceeded"}

    def _format_input(self, user_input: str, context: Optional[Dict] = None) -> str:
        """Format input with context."""
        if not context:
            return user_input
        context_str = json.dumps(context, indent=2, default=str)
        return f"Context:\n{context_str}\n\nTask:\n{user_input}"

    def _parse_response(self, response: str, json_mode: bool) -> Any:
        """Robust JSON parser with multiple extraction strategies."""
        if not json_mode:
            return {"raw_response": response}

        text = response.strip()

        # Strategy 1: Direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Strip markdown fences
        cleaned = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Strategy 3: Extract first complete JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Strategy 4: Extract JSON array
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        raise json.JSONDecodeError("Could not extract valid JSON", text, 0)

    def clear_memory(self):
        """Clear conversation memory."""
        self.memory = []
