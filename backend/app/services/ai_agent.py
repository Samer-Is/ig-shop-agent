"""
AI Agent service for Instagram DM automation with Jordanian Arabic support.
"""
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import openai
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from ..config import settings
from ..models import Conversation, CatalogItem, BusinessProfile, Order
from .licensing import verify_license


logger = logging.getLogger(__name__)


class AIAgent:
    """AI Agent for handling Instagram DMs in Jordanian Arabic."""
    
    def __init__(self):
        self.client = openai.AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version="2024-02-01"
        ) if settings.azure_openai_endpoint else openai.AsyncOpenAI(
            api_key=settings.azure_openai_api_key
        )
    
    async def process_message(
        self,
        tenant_id: int,
        sender: str,
        message: str,
        conversation_history: List[Dict],
        catalog_items: List[CatalogItem],
        business_profile: BusinessProfile
    ) -> Tuple[str, Optional[Dict], int, int]:
        """
        Process incoming Instagram message and generate AI response.
        
        Returns:
            Tuple of (response_text, function_call_result, tokens_in, tokens_out)
        """
        try:
            # Verify license first
            if not await verify_license(tenant_id):
                logger.warning(f"License verification failed for tenant {tenant_id}")
                return "خدمة المساعدة غير متاحة حالياً", None, 0, 0
            
            # Get system prompt
            system_prompt = self._build_system_prompt(business_profile, catalog_items)
            
            # Build conversation context
            messages = self._build_conversation_context(
                system_prompt, conversation_history, message
            )
            
            # Get knowledge base context if available
            knowledge_context = await self._search_knowledge_base(tenant_id, message)
            if knowledge_context:
                messages.insert(-1, {
                    "role": "system",
                    "content": f"معلومات إضافية من قاعدة المعرفة:\n{knowledge_context}"
                })
            
            # Call OpenAI with function calling
            response = await self.client.chat.completions.create(
                model=settings.gpt_model_name,
                messages=messages,
                functions=self._get_function_definitions(),
                function_call="auto",
                temperature=0.7,
                max_tokens=500
            )
            
            message_response = response.choices[0].message
            tokens_in = response.usage.prompt_tokens
            tokens_out = response.usage.completion_tokens
            
            # Handle function calls
            function_result = None
            if message_response.function_call:
                function_result = await self._execute_function_call(
                    tenant_id, message_response.function_call
                )
            
            # Get the AI response text
            response_text = message_response.content or "تم تنفيذ طلبك بنجاح"
            
            return response_text, function_result, tokens_in, tokens_out
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "عذراً، حدث خطأ في المعالجة. يرجى المحاولة مرة أخرى.", None, 0, 0
    
    def _build_system_prompt(
        self, 
        business_profile: BusinessProfile, 
        catalog_items: List[CatalogItem]
    ) -> str:
        """Build system prompt with business context."""
        profile_data = business_profile.profile_data if business_profile else {}
        
        # Build catalog summary
        catalog_summary = "\n".join([
            f"- {item.name}: {item.price_jod} دينار (كود: {item.sku})"
            for item in catalog_items[:10]  # Limit to first 10 items
        ])
        
        business_info = profile_data.get('business_info', {})
        policies = profile_data.get('policies', {})
        
        return f"""أنت مساعد ذكي لمتجر {business_info.get('name', 'متجر')} على إنستغرام.

معلومات العمل:
- اسم المتجر: {business_info.get('name', 'متجر')}
- الوصف: {business_info.get('description', 'متجر إلكتروني')}
- ساعات العمل: {business_info.get('hours', 'يومياً من 9 صباحاً حتى 9 مساءً')}

منتجاتنا المتاحة:
{catalog_summary}

سياسات المتجر:
- التوصيل: {policies.get('delivery', 'خدمة التوصيل متاحة في عمان')}
- الإرجاع: {policies.get('returns', 'يمكن الإرجاع خلال 7 أيام')}
- الدفع: {policies.get('payment', 'نقداً عند التسليم أو تحويل بنكي')}

أسلوب التواصل:
- استخدم اللهجة الأردنية الودودة والمهذبة
- كن مفيداً ومساعداً في الإجابة على الاستفسارات
- قدم معلومات دقيقة عن المنتجات والأسعار
- ساعد العملاء في إتمام الطلبات
- أظهر الاهتمام بحاجات العملاء

وظائف متاحة:
- إنشاء طلب جديد للعميل
- البحث عن منتج معين
- تقديم معلومات عن المتجر
"""
    
    def _build_conversation_context(
        self, 
        system_prompt: str, 
        history: List[Dict], 
        current_message: str
    ) -> List[Dict]:
        """Build conversation context with memory limit."""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history (limited to last N messages)
        recent_history = history[-settings.max_conversation_memory:]
        for msg in recent_history:
            role = "assistant" if msg.get('is_ai_response') == "true" else "user"
            messages.append({
                "role": role,
                "content": msg.get('text', '')
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        return messages
    
    async def _search_knowledge_base(self, tenant_id: int, query: str) -> Optional[str]:
        """Search knowledge base for relevant information using vector search."""
        try:
            # Import vector search here to avoid circular imports
            from .vector_search import VectorSearch
            vector_search = VectorSearch()
            
            # Search knowledge base using vector similarity
            results = await vector_search.search_knowledge(tenant_id, query, limit=3)
            
            # Combine search results
            context_parts = []
            for result in results:
                if 'content' in result:
                    context_parts.append(result['content'][:500])  # Limit content length
            
            return "\n\n".join(context_parts) if context_parts else None
            
        except Exception as e:
            logger.error(f"Knowledge base search error: {e}")
            return None
    
    def _get_function_definitions(self) -> List[Dict]:
        """Get function definitions for OpenAI function calling."""
        return [
            {
                "name": "create_order",
                "description": "إنشاء طلب جديد للعميل",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sku": {
                            "type": "string",
                            "description": "كود المنتج"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "الكمية المطلوبة"
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "اسم العميل"
                        },
                        "phone": {
                            "type": "string",
                            "description": "رقم هاتف العميل"
                        },
                        "notes": {
                            "type": "string",
                            "description": "ملاحظات إضافية"
                        }
                    },
                    "required": ["sku", "quantity", "customer_name"]
                }
            },
            {
                "name": "search_products",
                "description": "البحث عن منتجات معينة",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "كلمات البحث"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    
    async def _execute_function_call(
        self, 
        tenant_id: int, 
        function_call
    ) -> Optional[Dict]:
        """Execute function call and return result."""
        try:
            function_name = function_call.name
            arguments = json.loads(function_call.arguments)
            
            if function_name == "create_order":
                return await self._create_order(tenant_id, arguments)
            elif function_name == "search_products":
                return await self._search_products(tenant_id, arguments)
            
        except Exception as e:
            logger.error(f"Function call execution error: {e}")
            return {"error": str(e)}
        
        return None
    
    async def _create_order(self, tenant_id: int, args: Dict) -> Dict:
        """Create a new order."""
        # This would typically interact with the database
        # For now, return a mock response
        return {
            "success": True,
            "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "message": f"تم إنشاء الطلب بنجاح لـ {args.get('customer_name')}"
        }
    
    async def _search_products(self, tenant_id: int, args: Dict) -> Dict:
        """Search for products."""
        query = args.get('query', '')
        # This would typically search the catalog database
        # For now, return a mock response
        return {
            "success": True,
            "results": [
                {"name": "منتج تجريبي", "sku": "DEMO-001", "price": "25.000"}
            ],
            "message": f"تم العثور على نتائج للبحث: {query}"
        }


# Global AI agent instance
ai_agent = AIAgent()
