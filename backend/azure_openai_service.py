"""
Azure OpenAI Service Integration
Simplified for production readiness
"""

import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Enhanced Azure OpenAI Service with structured JSON input and function calling"""
    
    def __init__(self):
        try:
            # Initialize OpenAI client
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url if hasattr(settings, 'openai_base_url') else None
            )
            self.model = settings.openai_model or "gpt-4o"
            logger.info(f"AI service initialized successfully using model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            raise

    async def generate_response(
        self, 
        message: str, 
        catalog_items: List[Dict] = None,
        conversation_history: List[Dict] = None,
        customer_context: Dict = None,
        business_rules: Dict = None,
        knowledge_base: List[Dict] = None
    ) -> str:
        """Generate AI response using structured JSON context and function calling"""
        try:
            # Build structured context JSON
            context_json = self._build_structured_context(
                catalog_items or [],
                conversation_history or [],
                customer_context or {},
                business_rules or {},
                knowledge_base or []
            )
            
            # Check if human escalation is needed
            if self._detect_escalation_needed(message, conversation_history):
                logger.info("Human escalation detected - flagging conversation")
                return "أنا فاهم عليك تماماً والموضوع مهم. رح أخلي واحد من زملائي يتابع معك شخصياً عشان يحل المشكلة بأسرع وقت. [NEEDS_HUMAN_ATTENTION]"
            
            # Use function calling for structured AI response
            response = await self._generate_structured_response(message, context_json)
            
            logger.info(f"Generated structured AI response: {len(response)} characters")
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._get_fallback_response()

    def _build_structured_context(
        self,
        catalog_items: List[Dict],
        conversation_history: List[Dict],
        customer_context: Dict,
        business_rules: Dict,
        knowledge_base: List[Dict]
    ) -> Dict[str, Any]:
        """Build structured JSON context for AI processing"""
        
        return {
            "merchant_profile": {
                "business_name": business_rules.get("business_name", "المتجر"),
                "business_type": business_rules.get("business_type", "متجر إلكتروني"),
                "language_preference": business_rules.get("language_preference", "arabic"),
                "response_tone": business_rules.get("response_tone", "friendly"),
                "custom_instructions": business_rules.get("custom_prompt", ""),
                "page_id": customer_context.get("page_id", "")
            },
            "business_operations": {
                "working_hours": business_rules.get("working_hours", ""),
                "delivery_info": business_rules.get("delivery_info", ""),
                "payment_methods": business_rules.get("payment_methods", ""),
                "return_policy": business_rules.get("return_policy", ""),
                "terms_conditions": business_rules.get("terms_conditions", ""),
                "contact_info": business_rules.get("contact_info", "")
            },
            "product_catalog": [
                {
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "description": item.get("description", ""),
                    "price_jod": float(item.get("price_jod", 0)),
                    "stock_quantity": int(item.get("stock_quantity", 0)),
                    "category": item.get("category", ""),
                    "product_link": item.get("product_link", ""),
                    "media_link": item.get("media_link", ""),
                    "is_available": int(item.get("stock_quantity", 0)) > 0
                }
                for item in catalog_items
            ],
            "knowledge_base": [
                {
                    "title": kb.get("title", ""),
                    "content": kb.get("content", "")[:500]  # Limit content length
                }
                for kb in knowledge_base
            ],
            "conversation_context": {
                "customer_id": customer_context.get("sender_id", ""),
                "current_message": "",  # Will be filled by the calling function
                "conversation_history": [
                    {
                        "role": "customer" if not msg.get("is_ai_response") else "assistant",
                        "message": msg.get("message", ""),
                        "timestamp": str(msg.get("created_at", ""))
                    }
                    for msg in list(reversed(conversation_history))[-10:]  # Last 10 messages
                ],
                "session_context": {
                    "total_messages": len(conversation_history),
                    "last_interaction": str(conversation_history[0].get("created_at", "")) if conversation_history else ""
                }
            }
        }

    async def _generate_structured_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate response using structured context and function calling"""
        
        # Update current message in context
        context["conversation_context"]["current_message"] = message
        
        # Define function for structured AI processing
        functions = [
            {
                "name": "process_customer_message",
                "description": "Process customer message with full merchant context and generate appropriate response",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_message": {
                            "type": "string",
                            "description": "The customer's current message"
                        },
                        "merchant_context": {
                            "type": "object",
                            "description": "Complete merchant business context including catalog, rules, and history"
                        },
                        "response_analysis": {
                            "type": "object",
                            "properties": {
                                "detected_language": {"type": "string", "enum": ["arabic", "english", "mixed"]},
                                "customer_intent": {"type": "string", "enum": ["product_inquiry", "price_check", "order_placement", "support_request", "general_chat", "complaint"]},
                                "mentioned_products": {"type": "array", "items": {"type": "string"}},
                                "requires_escalation": {"type": "boolean"},
                                "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative", "angry"]}
                            }
                        },
                        "suggested_response": {
                            "type": "string",
                            "description": "Natural, conversational response in appropriate language"
                        }
                    },
                    "required": ["customer_message", "merchant_context", "response_analysis", "suggested_response"]
                }
            }
        ]
        
        # Build system message with structured instructions
        system_message = self._build_structured_system_prompt()
        
        # Prepare messages for function calling
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Process this customer message with the provided context: {json.dumps(context, ensure_ascii=False, indent=2)}"}
        ]
        
        # Call OpenAI with function calling
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            functions=functions,
            function_call={"name": "process_customer_message"},
            max_tokens=800,
            temperature=0.7
        )
        
        # Extract function call result
        function_call = response.choices[0].message.function_call
        if function_call and function_call.name == "process_customer_message":
            try:
                result = json.loads(function_call.arguments)
                ai_response = result.get("suggested_response", "")
                
                # Log analysis for debugging
                analysis = result.get("response_analysis", {})
                logger.info(f"AI Analysis - Intent: {analysis.get('customer_intent')}, Language: {analysis.get('detected_language')}, Sentiment: {analysis.get('sentiment')}")
                
                # Check for escalation flag
                if analysis.get("requires_escalation"):
                    ai_response += " [NEEDS_HUMAN_ATTENTION]"
                
                return ai_response
                
            except json.JSONDecodeError:
                logger.error("Failed to parse function call response")
                return self._get_fallback_response()
        
        return self._get_fallback_response()

    def _build_structured_system_prompt(self) -> str:
        """Build system prompt optimized for structured JSON processing"""
        
        return """You are an advanced AI assistant for an e-commerce business on Instagram. You will receive structured JSON context containing all merchant information and must process customer messages with high accuracy.

CRITICAL RULES:
1. NEVER hallucinate or make up information not in the provided context
2. Use ONLY the data provided in the merchant_context JSON
3. Respond in the customer's detected language (Arabic/English)
4. Maintain natural, conversational tone
5. Include product media links only when explicitly requested

PROCESSING APPROACH:
1. Analyze the customer's message for intent, language, and sentiment
2. Search the provided product_catalog for relevant items
3. Use business_operations data for policies and procedures
4. Reference conversation_history for context continuity
5. Apply knowledge_base information when relevant

RESPONSE GENERATION:
- Default to Jordanian Arabic unless customer uses English
- Be conversational and helpful, not robotic
- Include specific product details when discussing items
- Suggest complementary products when appropriate
- Flag for human escalation if customer is angry or has complex issues

Your response must be natural and engaging while being factually accurate based on the provided context."""

    def _detect_escalation_needed(self, message: str, conversation_history: List[Dict] = None) -> bool:
        """Detect if conversation needs human escalation"""
        escalation_keywords = [
            "angry", "frustrated", "manager", "complaint", "terrible", "awful", "worst",
            "زعلان", "مستاء", "مدير", "شكوى", "فظيع", "سيء", "غاضب", "مشكلة كبيرة"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in escalation_keywords)

    def _get_fallback_response(self) -> str:
        """Get fallback response when AI fails"""
        return "أهلاً وسهلاً! عذراً، واجهت مشكلة تقنية صغيرة. ممكن تعيد رسالتك عشان أقدر أساعدك أحسن؟ 🙏" 