import os
import asyncio
from typing import Dict, Any, Optional
import openai
import logging

logger = logging.getLogger(__name__)

class LLMService:
    """
    LLM service for integrating with OpenAI API.
    Provides text processing capabilities like summarization and rephrasing.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.client = None
        
        if self.api_key:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        else:
            logger.warning("OPENAI_API_KEY not found in environment variables")
    
    async def process_text(self, text: str, operation: str = "summarize") -> str:
        """
        Process text using OpenAI API.
        
        Args:
            text: The input text to process
            operation: The type of operation (summarize, rephrase, etc.)
            
        Returns:
            Processed text result
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY.")
        
        try:
            prompt = self._get_prompt(text, operation)
            
            logger.info(f"Processing text with operation: {operation}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that processes text according to user instructions. Be concise and clear in your responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            result = response.choices[0].message.content.strip()
            
            logger.info(f"Successfully processed text with {operation} operation")
            return result
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ValueError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in LLM processing: {e}")
            raise ValueError(f"Error processing text: {str(e)}")
    
    def _get_prompt(self, text: str, operation: str) -> str:
        """
        Generate appropriate prompt based on operation type.
        
        Args:
            text: Input text
            operation: Type of operation
            
        Returns:
            Formatted prompt string
        """
        prompts = {
            "summarize": f"Please provide a concise summary of the following text:\n\n{text}",
            "rephrase": f"Please rephrase the following text in a different way while maintaining the same meaning:\n\n{text}",
            "analyze": f"Please analyze the sentiment and key themes in the following text:\n\n{text}",
            "questions": f"Generate 3 insightful questions based on the following text:\n\n{text}",
            "expand": f"Please expand on the following text with additional relevant details:\n\n{text}"
        }
        
        return prompts.get(operation, prompts["summarize"])
    
    async def health_check(self) -> bool:
        """
        Check if OpenAI API is accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.client:
            return False
            
        try:
            # Simple test call to check API connectivity
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ],
                max_tokens=5,
            )
            
            return response.choices[0].message.content is not None
            
        except Exception as e:
            logger.warning(f"LLM health check failed: {e}")
            return False
    
    async def generate_follow_up_questions(self, original_text: str, reversed_text: str) -> str:
        """
        Bonus feature: Generate follow-up questions based on reversed input.
        
        Args:
            original_text: The original input text
            reversed_text: The reversed text
            
        Returns:
            Generated follow-up questions
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            prompt = f"""
            Given the original text: "{original_text}"
            And its reversed version: "{reversed_text}"
            
            Generate 2-3 creative and insightful follow-up questions that could lead to interesting discussions or analysis.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative assistant that generates thought-provoking questions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.8,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {e}")
            raise ValueError(f"Error generating questions: {str(e)}") 