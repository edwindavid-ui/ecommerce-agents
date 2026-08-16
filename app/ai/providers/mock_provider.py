from typing import Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json
import re
import os

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

debug_mode = os.environ.get("DEBUG_MODE", "False")

print(f"Connecting to: Gemini API")
print(f"Debug mode is set to: {debug_mode}")

from app.ai.models.structured_output import StructuredResponse


class BaseLLMProvider:
    def call_model(self, prompt: str, **kwargs) -> dict:
        raise NotImplementedError


class MockLLMProvider(BaseLLMProvider):
    def call_model(self, prompt: str, **kwargs) -> dict:
        """
        Mock LLM provider that returns deterministic structured responses.
        Used for testing and MVP development.
        """
        response = StructuredResponse(
            reasoning="Mock reasoning based on prompt",
            decision="PROCEED",
            confidence=0.85,
        )
        return response.model_dump()


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-3.5-flash"):
        """
        Gemini API provider for structured LLM calls.
        
        Args:
            api_key: Google Gemini API key
            model: Model name (e.g., "gemini-2.0-flash", "gemini-1.5-pro")
        """
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        self.api_key = api_key
        self.model = model
        
        # Import here to avoid requiring the library if not used
        try:
            self.client = genai.Client(api_key=api_key)
        except ImportError:
            raise ImportError("google-generativeai is required for Gemini provider. Install with: pip install google-generativeai")

    def call_model(self, prompt: str, **kwargs) -> dict:
        """
        Call Gemini API with structured output validation.
        
        Returns a dict matching StructuredResponse schema:
        {
            "reasoning": str,
            "decision": str,
            "confidence": float
        }
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",  # Forces Gemini to output clean JSON
                    temperature=0.3,
                ),
             )
            result = json.loads(response.text)  
            # Parse the response to extract structured data
            # Gemini returns text, we need to extract the structured fields            
            # Validate against schema
            response_data = self._parse_response(response.text)
            validated = StructuredResponse(**response_data)
            return validated.model_dump()
            
            
        except Exception as exc:
            raise RuntimeError(f"Gemini API call failed: {exc}")

    @staticmethod
    def _parse_response(text: str) -> dict:
        """
        Parse Gemini response text into structured format.
        Expects JSON-like structure in the response.
        """
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return {
                    "reasoning": parsed.get("reasoning", text[:500]),
                    "decision": parsed.get("decision", "PROCEED"),
                    "confidence": float(parsed.get("confidence", 0.7)),
                }
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Fallback: extract from text patterns
        return {
            "reasoning": text[:500],
            "decision": "PROCEED",
            "confidence": 0.7,
        }
