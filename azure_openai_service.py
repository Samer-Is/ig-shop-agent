"""
Azure OpenAI Service Integration
Enhanced AI capabilities for 100% production readiness
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from advanced_config import ProductionConfig

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Enhanced Azure OpenAI service for production"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        config = ProductionConfig.get_azure_openai_config()
        
        # Use Azure OpenAI if configured, fallback to OpenAI
        if config['api_base'] and config['api_key']:
            self.client = AzureOpenAI(
                azure_endpoint=config['api_base'],
                api_key=config['api_key'],
                api_version=config['api_version']
            )
            self.deployment_name = config['deployment_name']
            self.is_azure = True
            logger.info("Using Azure OpenAI service")
        else:
            # Fallback to regular OpenAI
            from openai import OpenAI
            self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            self.deployment_name = "gpt-3.5-turbo"
            self.is_azure = False
            logger.info("Using OpenAI service (fallback)")
    
    async def generate_response(
        self, 
        message: str, 
        catalog_items: List[Dict], 
        conversation_history: List[Dict] = None,
        customer_context: Dict = None
    ) -> str:
        """Generate AI response with enhanced context"""
        try:
            # Build comprehensive system prompt
            system_prompt = self._build_system_prompt(catalog_items, customer_context)
            
            # Build conversation context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            if conversation_history:
                recent_history = conversation_history[-ProductionConfig.AI_CONTEXT_WINDOW:]
                for msg in recent_history:
                    messages.append({
                        "role": "user" if not msg.get('ai_generated') else "assistant",
                        "content": msg['text']
                    })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Generate response
            response = await self._call_openai(messages)
            
            # Log interaction for improvement
            self._log_interaction(message, response, catalog_items)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._get_fallback_response()
    
    def _build_system_prompt(self, catalog_items: List[Dict], context: Dict = None) -> str:
        """Build comprehensive system prompt"""
        
        # Base system identity
        prompt = """أنت مساعد ذكي لمتجر إلكتروني أردني متخصص في الموضة والأزياء.
You are an AI assistant for a Jordanian online fashion store.

المعلومات الأساسية / Basic Information:
- اسم المتجر: IG Shop Agent
- الموقع: الأردن
- التخصص: الأزياء والموضة
- اللغة المفضلة: العربية، مع دعم الإنجليزية

إرشادات المحادثة / Conversation Guidelines:
1. كن ودودًا ومهذبًا دائماً
2. استخدم اللغة العربية كلغة أساسية
3. قدم معلومات دقيقة عن المنتجات
4. ساعد في اتخاذ قرار الشراء
5. اقترح منتجات مناسبة حسب الحاجة

"""
        
        # Add available products
        if catalog_items:
            prompt += "\nالمنتجات المتاحة / Available Products:\n"
            for item in catalog_items[:10]:  # Limit to 10 items
                prompt += f"- {item['name']}: {item['price_jod']} دينار أردني"
                if item.get('description'):
                    prompt += f" - {item['description'][:50]}..."
                if item.get('stock_quantity', 0) > 0:
                    prompt += f" (متوفر: {item['stock_quantity']} قطعة)"
                prompt += "\n"
        
        # Add customer context if available
        if context:
            prompt += f"\nمعلومات العميل / Customer Context:\n"
            if context.get('previous_orders'):
                prompt += f"- طلبات سابقة: {len(context['previous_orders'])}\n"
            if context.get('preferences'):
                prompt += f"- التفضيلات: {context['preferences']}\n"
        
        prompt += """
تعليمات الرد / Response Instructions:
- أجب باللغة العربية أولاً، ثم الإنجليزية إذا لزم الأمر
- كن مختصراً ومفيداً
- اذكر الأسعار بالدينار الأردني
- لا تخترع معلومات غير موجودة
- إذا لم تجد منتج مناسب، اقترح البدائل المتاحة
"""
        
        return prompt
    
    async def _call_openai(self, messages: List[Dict]) -> str:
        """Call OpenAI API with proper error handling"""
        try:
            if self.is_azure:
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    max_tokens=ProductionConfig.AI_RESPONSE_MAX_TOKENS,
                    temperature=ProductionConfig.AI_TEMPERATURE
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    max_tokens=ProductionConfig.AI_RESPONSE_MAX_TOKENS,
                    temperature=ProductionConfig.AI_TEMPERATURE
                )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _get_fallback_response(self) -> str:
        """Get fallback response when AI fails"""
        import random
        return random.choice(ProductionConfig.AI_FALLBACK_RESPONSES)
    
    def _log_interaction(self, message: str, response: str, catalog_items: List[Dict]):
        """Log interaction for analytics and improvement"""
        logger.info(f"AI Interaction - Input length: {len(message)}, "
                   f"Response length: {len(response)}, "
                   f"Catalog items: {len(catalog_items)}")
    
    async def analyze_customer_intent(self, message: str) -> Dict[str, Any]:
        """Analyze customer intent from message"""
        try:
            intent_prompt = f"""
            Analyze the following customer message and categorize the intent:
            
            Message: "{message}"
            
            Respond with JSON containing:
            - intent: (browse, purchase, inquiry, support, complaint)
            - products_mentioned: [list of product types]
            - urgency: (low, medium, high)
            - language: (ar, en)
            
            Response:
            """
            
            response = await self._call_openai([
                {"role": "system", "content": "You are an intent analysis system. Respond only with valid JSON."},
                {"role": "user", "content": intent_prompt}
            ])
            
            import json
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Intent analysis error: {e}")
            return {
                "intent": "inquiry",
                "products_mentioned": [],
                "urgency": "medium",
                "language": "ar"
            }
    
    async def generate_product_description(self, product_data: Dict) -> str:
        """Generate enhanced product description"""
        try:
            prompt = f"""
            Generate an attractive Arabic product description for:
            
            Product: {product_data.get('name', '')}
            Category: {product_data.get('category', '')}
            Price: {product_data.get('price_jod', 0)} JOD
            Current Description: {product_data.get('description', '')}
            
            Create a compelling description in Arabic that:
            - Highlights key features
            - Appeals to Jordanian customers
            - Includes size and material information if relevant
            - Is 2-3 sentences maximum
            """
            
            response = await self._call_openai([
                {"role": "system", "content": "You are a product description writer for Jordanian fashion e-commerce."},
                {"role": "user", "content": prompt}
            ])
            
            return response
            
        except Exception as e:
            logger.error(f"Product description generation error: {e}")
            return product_data.get('description', 'وصف المنتج غير متوفر')

# Global service instance
azure_openai_service = AzureOpenAIService() 