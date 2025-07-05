"""
Azure OpenAI Service Integration
Simplified for production readiness
"""

import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .config import Settings

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Simplified OpenAI service for production"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        settings = Settings()
        
        # Use OpenAI API
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"
        logger.info("OpenAI service initialized")
    
    async def generate_response(
        self, 
        message: str, 
        catalog_items: List[Dict] = None,
        conversation_history: List[Dict] = None,
        customer_context: Dict = None
    ) -> str:
        """Generate AI response with context"""
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(catalog_items or [], customer_context)
            
            # Build conversation context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (last 5 messages)
            if conversation_history:
                recent_history = conversation_history[-5:]
                for msg in recent_history:
                    messages.append({
                        "role": "user" if not msg.get('ai_generated') else "assistant",
                        "content": msg['text']
                    })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"Generated AI response: {len(result)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._get_fallback_response()
    
    def _build_system_prompt(self, catalog_items: List[Dict], context: Dict = None) -> str:
        """Build system prompt for AI"""
        
        prompt = """You are a helpful shopping assistant for an Instagram store in Jordan.
You speak both English and Arabic fluently.

Guidelines:
1. Be friendly and helpful
2. Provide accurate product information
3. Help customers make purchasing decisions
4. Suggest appropriate products based on needs
5. For orders, collect: product name, quantity, customer name, phone, address

"""
        
        # Add available products
        if catalog_items:
            prompt += "Available Products:\n"
            for item in catalog_items[:10]:  # Limit to 10 items
                prompt += f"- {item.get('name', 'Unknown')}: {item.get('price_jod', 0)} JOD"
                if item.get('description'):
                    prompt += f" - {item['description'][:50]}..."
                if item.get('stock_quantity', 0) > 0:
                    prompt += f" (Stock: {item['stock_quantity']})"
                prompt += "\n"
        
        prompt += "\nRespond in the same language as the customer. Be concise and helpful."
        
        return prompt
    
    def _get_fallback_response(self) -> str:
        """Get fallback response when AI fails"""
        return "I apologize, but I'm having trouble processing your request right now. Please try again or contact our support team."
    
    async def analyze_customer_intent(self, message: str) -> Dict[str, Any]:
        """Analyze customer intent from message"""
        try:
            intent_prompt = f"""
            Analyze this customer message and respond with JSON:
            Message: "{message}"
            
            JSON format:
            {{
                "intent": "browse|purchase|inquiry|support",
                "products_mentioned": [],
                "urgency": "low|medium|high",
                "language": "en|ar"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an intent analysis system. Respond only with valid JSON."},
                    {"role": "user", "content": intent_prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Intent analysis error: {e}")
            return {
                "intent": "inquiry",
                "products_mentioned": [],
                "urgency": "medium",
                "language": "en"
            }

# Global service instance
_openai_service = None

def get_openai_client() -> AzureOpenAIService:
    """Get the global OpenAI service instance"""
    global _openai_service
    if _openai_service is None:
        _openai_service = AzureOpenAIService()
    return _openai_service 