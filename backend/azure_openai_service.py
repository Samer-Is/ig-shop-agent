"""
Azure OpenAI Service Integration
Simplified for production readiness
"""

import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Simplified OpenAI service for production"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        # Check if Azure OpenAI is configured
        if settings.use_azure_openai:
            logger.info("Using Azure OpenAI service")
            if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_API_KEY:
                logger.error("Azure OpenAI endpoint or API key not configured!")
                raise ValueError("Azure OpenAI configuration is incomplete")
            
            # Use Azure OpenAI
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION
            )
            self.model = settings.AZURE_OPENAI_DEPLOYMENT_NAME
            logger.info(f"Azure OpenAI service initialized with endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
            
        else:
            logger.info("Using regular OpenAI service")
            # Check if API key is available
            if not settings.OPENAI_API_KEY:
                logger.error("OPENAI_API_KEY environment variable is not set!")
                raise ValueError("OpenAI API key is required but not configured")
            
            # Use OpenAI API
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4o"
            
        logger.info(f"AI service initialized successfully using model: {self.model}")
    
    async def generate_response(
        self, 
        message: str, 
        catalog_items: List[Dict] = None,
        conversation_history: List[Dict] = None,
        customer_context: Dict = None,
        business_rules: Dict = None,
        knowledge_base: List[Dict] = None
    ) -> str:
        """Generate AI response with context"""
        try:
            # Build system prompt with enhanced context
            system_prompt = self._build_system_prompt(
                catalog_items or [], 
                customer_context, 
                business_rules, 
                knowledge_base
            )
            
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
    
    def _build_system_prompt(self, catalog_items: List[Dict], context: Dict = None, business_rules: Dict = None, knowledge_base: List[Dict] = None) -> str:
        """Build comprehensive system prompt for AI with universal base and merchant-specific context"""
        
        # Universal base prompt - works for any domain/business
        prompt = """You are an intelligent customer service assistant specialized in helping customers through Instagram Direct Messages.

CORE CAPABILITIES:
• Multilingual communication (primarily English and Arabic)
• Product information and recommendations
• Order processing and customer support
• Business inquiry handling
• Professional and friendly assistance

RESPONSE GUIDELINES:
1. Always respond in the same language the customer uses
2. Be helpful, professional, and conversational
3. Provide accurate information based on available context
4. For product inquiries: Check available inventory and provide detailed information
5. For orders: Collect all required information (product, quantity, customer details, delivery address)
6. If information is unavailable: Politely direct to appropriate resources
7. Maintain conversation context and remember previous interactions

"""
        
        # Add business-specific information
        if business_rules:
            prompt += "\n=== BUSINESS INFORMATION ===\n"
            
            if business_rules.get('business_name'):
                prompt += f"Business Name: {business_rules['business_name']}\n"
            
            if business_rules.get('business_type'):
                prompt += f"Business Type: {business_rules['business_type']}\n"
            
            if business_rules.get('working_hours'):
                prompt += f"Working Hours: {business_rules['working_hours']}\n"
                
            if business_rules.get('delivery_info'):
                prompt += f"Delivery Information: {business_rules['delivery_info']}\n"
                
            if business_rules.get('payment_methods'):
                prompt += f"Payment Methods: {business_rules['payment_methods']}\n"
                
            if business_rules.get('return_policy'):
                prompt += f"Return Policy: {business_rules['return_policy']}\n"
                
            if business_rules.get('terms_conditions'):
                prompt += f"Terms & Conditions: {business_rules['terms_conditions']}\n"
                
            if business_rules.get('contact_info'):
                prompt += f"Contact Information: {business_rules['contact_info']}\n"
                
            if business_rules.get('custom_prompt'):
                prompt += f"\nSpecial Instructions: {business_rules['custom_prompt']}\n"
                
            if business_rules.get('ai_instructions'):
                prompt += f"AI Behavior Guidelines: {business_rules['ai_instructions']}\n"
            
            prompt += "\n"
        
        # Add knowledge base information
        if knowledge_base:
            prompt += "=== KNOWLEDGE BASE ===\n"
            for item in knowledge_base[:5]:  # Limit to avoid token limit
                if item.get('title') and item.get('content'):
                    prompt += f"• {item['title']}:\n{item['content'][:300]}...\n\n"
        
        # Add product catalog
        if catalog_items:
            prompt += "=== AVAILABLE PRODUCTS ===\n"
            for item in catalog_items[:15]:  # Increased limit for better context
                product_info = f"• {item.get('name', 'Unknown Product')}"
                
                if item.get('price_jod'):
                    product_info += f" - {item.get('price_jod')} JOD"
                    
                if item.get('description'):
                    product_info += f"\n  Description: {item['description'][:100]}..."
                    
                if item.get('category'):
                    product_info += f"\n  Category: {item['category']}"
                    
                if item.get('product_link'):
                    product_info += f"\n  Purchase Link: {item['product_link']}"
                    
                stock_status = item.get('stock_quantity', 0)
                if stock_status > 0:
                    product_info += f"\n  Stock: {stock_status} available"
                else:
                    product_info += f"\n  Stock: Out of stock"
                    
                prompt += product_info + "\n\n"
        
        # Final instructions
        prompt += """
=== IMPORTANT REMINDERS ===
• Always check product availability before confirming orders
• For out-of-stock items, suggest alternatives or notify about restocking
• Be proactive in offering help and product recommendations
• Maintain a friendly, professional tone that reflects the business personality
• If you cannot find specific information, acknowledge it and offer to connect them with support

Remember: You represent this business, so ensure every interaction enhances the customer experience and builds trust.
"""
        
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