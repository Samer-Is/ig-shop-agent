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
            # Check if human escalation is needed
            if self._detect_escalation_needed(message, conversation_history):
                logger.info("Human escalation detected - flagging conversation")
                return "أنا فاهم عليك تماماً والموضوع مهم. رح أخلي واحد من زملائي يتابع معك شخصياً عشان يحل المشكلة بأسرع وقت. [NEEDS_HUMAN_ATTENTION]"
            # Build system prompt with enhanced context
            system_prompt = self._build_system_prompt(
                catalog_items or [], 
                customer_context, 
                business_rules, 
                knowledge_base,
                conversation_history
            )
            
            # Build conversation context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (last 20 messages as per consultant recommendations)
            if conversation_history:
                # Reverse to get chronological order (oldest to newest)
                recent_history = list(reversed(conversation_history))
                for msg in recent_history:
                    role = "assistant" if msg.get('is_ai_response') else "user"
                    messages.append({
                        "role": role,
                        "content": msg.get('message', '')
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
    
    def _build_system_prompt(self, catalog_items: List[Dict], context: Dict = None, business_rules: Dict = None, knowledge_base: List[Dict] = None, conversation_history: List[Dict] = None) -> str:
        """Build comprehensive system prompt based on consultant recommendations (Version 2.0)"""
        
        # Enhanced Universal System Prompt - Version 2.0
        prompt = """[SYSTEM_IDENTITY]
You are a world-class conversational AI assistant for an e-commerce brand on Instagram. Your name is not "AI" or "bot"; you are a member of the team. Your persona is cool, friendly, and professional, like a helpful store insider who knows everything about the products and business. You are highly attentive to detail and your primary goal is to provide an exceptionally human-like and helpful customer experience.

[PRIMARY_DIRECTIVE]
Your absolute, non-negotiable golden rule is: DO NOT ASSUME. DO NOT HALLUCINATE. DO NOT MAKE UP ANSWERS.

Every single piece of information you provide to a customer must be derived exclusively from the data provided to you for the specific merchant. This data includes:

[Merchant Business Rules & Info] (Working hours, shipping policy, etc.)
[Product Catalog] (Item names, descriptions, prices, stock, media links.)
[Current Conversation History] (The last 20 messages.)

If the answer to a customer's question is not found in the provided data, you MUST NOT invent an answer. Instead, you must politely state that you don't have that specific information and offer to help with something else.

Example of a safe response: "ما عندي جواب أكيد على هاد السؤال للأسف، بس بقدر أساعدك بشي تاني؟" (Unfortunately, I don't have a definite answer for that question, but can I help with something else?)

[COMMUNICATION_PROTOCOL]
Primary Language: Your default communication language is Jordanian Arabic (اللهجة الأردنية). Your tone should be natural and conversational.

Language Switching: Analyze the customer's language. If the customer is writing primarily in English, you must switch and reply in fluent, natural English. If they mix, default back to Jordanian Arabic.

Human-like Typing: Type like a real person. Use natural-sounding phrases, appropriate emojis (👍, 😄, 🙏), and conversational flow. Avoid robotic lists and jargon.

No Field Names: Do NOT expose the internal data field names. Weave the information into natural sentences.

ROBOTIC (DO NOT DO THIS):
المنتج: جاكيت فيراري. الوصف: جاكيت أحمر. السعر: 10 دينار. الرابط: [link]

HUMAN-LIKE (DO THIS):
أهلاً! أكيد، الجاكيت الفيراري الأحمر موجود عنا ومواصفاته ممتازة. سعره 10 دنانير بس. (Hello! Of course, the red Ferrari jacket is available and its specs are excellent. It costs only 10 JOD.)

[CONTEXT & ACTION_RULES]
Full Context Awareness: Before EVERY response, you MUST silently review the last 20 messages in the [Current Conversation History]. Understand the context completely. Is this a follow-up question? Are they changing their mind? Your answer must be relevant to the ongoing chat.

Knowledge Base is Truth: When a question is asked, your internal thought process must be: (1) Scan [Merchant Business Rules]. (2) Scan [Product Catalog]. (3) Formulate an answer based only on what you find.

Handling Media Links: The media_link in the product catalog is a URL to a photo or video.

You MUST NOT send this link unless the customer explicitly asks for a "photo", "image", "صورة", "أشوف شكله", or a similar visual request for a specific item.

When asked, present the link naturally. Example: "أكيد، هاي صورة للجاكيت عشان تشوفه أوضح: [link]" (Of course, here is a picture of the jacket so you can see it more clearly: [link])

[PROACTIVE_ASSISTANCE_PROTOCOL]
Suggest Complements: If a customer is interested in a product, you can proactively suggest another item from the catalog that complements it.

Example: "حلو كثير هاد القميص! على فكرة، في عنا بنطلون جينز لونه أسود بلبق معه بشكل خرافي، مهتم تشوفه؟" (This shirt is very nice! By the way, we have black jeans that would go with it perfectly, interested in seeing them?)

Clarify Ambiguity: If a customer's request is vague (e.g., "do you have jackets?"), ask clarifying questions to narrow down what they want before listing everything.

Example: "أكيد عنا جاكيتات! بتدور على لون معين أو ستايل معين؟ صيفي ولا شتوي؟" (Of course we have jackets! Are you looking for a specific color or style? For summer or winter?)

[HUMAN_ESCALATION_PROTOCOL]
Detect Critical Issues: You must constantly analyze the customer's sentiment. If a customer expresses high levels of anger, frustration, or confusion, or asks for something clearly outside your scope (e.g., a complex complaint, wholesale inquiries), you must initiate a handover.

Handover Procedure:
Politely inform the customer you are getting a human specialist.

Example: "أنا فاهم عليك تماماً والموضوع مهم. رح أخلي واحد من زملائي يتابع معك شخصياً عشان يحل المشكلة بأسرع وقت." (I completely understand and the issue is important. I will have one of my colleagues follow up with you personally to solve the problem as quickly as possible.)

In your internal response, you must include the special tag: [NEEDS_HUMAN_ATTENTION] so the system can flag the conversation.

"""

        # Add merchant-specific business rules
        if business_rules:
            prompt += "\n[MERCHANT_BUSINESS_RULES]\n"
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
                prompt += f"Additional Instructions: {business_rules['custom_prompt']}\n"
            if business_rules.get('ai_instructions'):
                prompt += f"AI Behavior Guidelines: {business_rules['ai_instructions']}\n"
            if business_rules.get('language_preference'):
                prompt += f"Language Preference: {business_rules['language_preference']}\n"
            if business_rules.get('response_tone'):
                prompt += f"Response Tone: {business_rules['response_tone']}\n"

        # Add product catalog
        if catalog_items:
            prompt += "\n[PRODUCT_CATALOG]\n"
            for item in catalog_items:
                prompt += f"- {item.get('name', 'Unknown Product')}"
                if item.get('description'):
                    prompt += f": {item['description']}"
                if item.get('price_jod'):
                    prompt += f" - Price: {item['price_jod']} JOD"
                if item.get('stock_quantity') is not None:
                    stock_status = "In Stock" if item['stock_quantity'] > 0 else "Out of Stock"
                    prompt += f" - Stock: {stock_status} ({item['stock_quantity']} available)"
                if item.get('category'):
                    prompt += f" - Category: {item['category']}"
                if item.get('product_link'):
                    prompt += f" - Media Link: {item['product_link']}"
                prompt += "\n"

        # Add knowledge base
        if knowledge_base:
            prompt += "\n[KNOWLEDGE_BASE]\n"
            for kb_item in knowledge_base:
                prompt += f"- {kb_item.get('title', 'Untitled')}: {kb_item.get('content', '')}\n"

        # Add current context
        if context:
            prompt += "\n[CURRENT_CONTEXT]\n"
            if context.get('sender_id'):
                prompt += f"Customer ID: {context['sender_id']}\n"
            if context.get('page_id'):
                prompt += f"Instagram Page ID: {context['page_id']}\n"
            if context.get('conversation_history'):
                prompt += f"Previous Messages: {len(context['conversation_history'])} messages in history\n"
        
        # Add merchant Instagram page information
        if business_rules and business_rules.get('business_name'):
            prompt += f"\n[INSTAGRAM_PAGE_CONTEXT]\n"
            prompt += f"You are responding as: {business_rules['business_name']}\n"
            if context and context.get('page_id'):
                prompt += f"Instagram Page ID: {context['page_id']}\n"
            prompt += f"Remember: You represent {business_rules['business_name']} and should respond accordingly.\n"

        # Add conversation history details for context awareness
        if conversation_history:
            prompt += f"\n[CONVERSATION_HISTORY]\n"
            prompt += f"Last {len(conversation_history)} messages between customer and assistant:\n"
            # Show recent history for context (chronological order)
            for i, msg in enumerate(reversed(conversation_history[-10:])):  # Show last 10 for context
                role = "Customer" if not msg.get('is_ai_response') else "Assistant"
                prompt += f"{i+1}. {role}: {msg.get('message', '')[:100]}...\n"

        prompt += "\n[FINAL_REMINDER]\nRemember: Be human, be helpful, be accurate. Only use the information provided above. If you don't know something, admit it and offer alternative help. Default to Jordanian Arabic unless the customer uses English."

        return prompt
    
    def _detect_escalation_needed(self, message: str, conversation_history: List[Dict] = None) -> bool:
        """Detect if human escalation is needed based on message content and conversation context"""
        
        # Keywords that indicate escalation needs
        escalation_keywords = [
            'angry', 'frustrated', 'complaint', 'manager', 'supervisor', 'refund', 'cancel', 'problem',
            'issue', 'wrong', 'mistake', 'error', 'disappointed', 'unsatisfied', 'unhappy',
            'غاضب', 'مشكلة', 'خطأ', 'مدير', 'شكوى', 'استرداد', 'إلغاء', 'مشاكل'
        ]
        
        message_lower = message.lower()
        
        # Check for escalation keywords
        for keyword in escalation_keywords:
            if keyword in message_lower:
                return True
        
        # Check for repeated similar messages (customer frustration)
        if conversation_history and len(conversation_history) >= 4:
            recent_customer_messages = [
                msg.get('message', '') for msg in conversation_history[-4:] 
                if not msg.get('is_ai_response')
            ]
            
            # If customer sent similar messages repeatedly, escalate
            if len(set(recent_customer_messages)) <= 2 and len(recent_customer_messages) >= 3:
                return True
        
        return False
    
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