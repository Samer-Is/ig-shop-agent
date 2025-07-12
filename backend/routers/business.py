"""
Business Rules and Configuration Management
Handles merchant-specific business information and AI settings
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from database import get_database, DatabaseService
from auth_middleware import get_current_user_id, require_auth
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/business", tags=["business"])

class BusinessRulesUpdate(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    working_hours: Optional[str] = None
    delivery_info: Optional[str] = None
    payment_methods: Optional[str] = None
    return_policy: Optional[str] = None
    terms_conditions: Optional[str] = None
    contact_info: Optional[str] = None
    custom_prompt: Optional[str] = None
    ai_instructions: Optional[str] = None
    language_preference: Optional[str] = None
    response_tone: Optional[str] = None

class BusinessRulesResponse(BaseModel):
    id: str
    user_id: str
    business_name: Optional[str]
    business_type: Optional[str]
    working_hours: Optional[str]
    delivery_info: Optional[str]
    payment_methods: Optional[str]
    return_policy: Optional[str]
    terms_conditions: Optional[str]
    contact_info: Optional[str]
    custom_prompt: Optional[str]
    ai_instructions: Optional[str]
    language_preference: str
    response_tone: str

@router.get("/rules", response_model=BusinessRulesResponse)
async def get_business_rules(request: Request, db: DatabaseService = Depends(get_database)):
    """Get current business rules and configuration"""
    try:
        # Get current user ID
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        rules = await db.fetch_one(
            "SELECT * FROM business_rules WHERE user_id = $1",
            user_id
        )
        
        if not rules:
            # Create default rules if none exist
            await db.execute_query(
                """
                INSERT INTO business_rules (id, user_id, language_preference, response_tone) 
                VALUES (gen_random_uuid(), $1, $2, $3)
                """,
                user_id,
                "en,ar",
                "professional"
            )
            
            rules = await db.fetch_one(
                "SELECT * FROM business_rules WHERE user_id = $1",
                user_id
            )
        
        return BusinessRulesResponse(**rules)
        
    except Exception as e:
        logger.error(f"Error fetching business rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch business rules")

@router.put("/rules", response_model=BusinessRulesResponse)
async def update_business_rules(
    rules_update: BusinessRulesUpdate,
    request: Request,
    db: DatabaseService = Depends(get_database)
):
    """Update business rules and configuration"""
    try:
        # Get current user ID
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get current rules
        current_rules = await db.fetch_one(
            "SELECT * FROM business_rules WHERE user_id = $1",
            user_id
        )
        
        if not current_rules:
            # Create new rules
            await db.execute_query(
                """
                INSERT INTO business_rules (
                    id, user_id, business_name, business_type, working_hours, 
                    delivery_info, payment_methods, return_policy, terms_conditions, 
                    contact_info, custom_prompt, ai_instructions, language_preference, 
                    response_tone
                ) VALUES (
                    gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
                )
                """,
                user_id,
                rules_update.business_name,
                rules_update.business_type,
                rules_update.working_hours,
                rules_update.delivery_info,
                rules_update.payment_methods,
                rules_update.return_policy,
                rules_update.terms_conditions,
                rules_update.contact_info,
                rules_update.custom_prompt,
                rules_update.ai_instructions,
                rules_update.language_preference or "en,ar",
                rules_update.response_tone or "professional"
            )
        else:
            # Update existing rules
            update_fields = []
            update_values = []
            param_count = 1
            
            for field, value in rules_update.dict(exclude_unset=True).items():
                if value is not None:
                    update_fields.append(f"{field} = ${param_count + 1}")
                    update_values.append(value)
                    param_count += 1
            
            if update_fields:
                update_values.append(user_id)  # user_id for WHERE clause
                query = f"UPDATE business_rules SET {', '.join(update_fields)}, updated_at = NOW() WHERE user_id = ${param_count + 1}"
                await db.execute_query(query, *update_values)
        
        # Return updated rules
        updated_rules = await db.fetch_one(
            "SELECT * FROM business_rules WHERE user_id = $1",
            user_id
        )
        
        return BusinessRulesResponse(**updated_rules)
        
    except Exception as e:
        logger.error(f"Error updating business rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to update business rules")

@router.post("/rules/reset")
async def reset_business_rules(request: Request, db: DatabaseService = Depends(get_database)):
    """Reset business rules to defaults"""
    try:
        # Get current user ID
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        await db.execute_query(
            "DELETE FROM business_rules WHERE user_id = $1",
            user_id
        )
        
        await db.execute_query(
            """
            INSERT INTO business_rules (id, user_id, language_preference, response_tone) 
            VALUES (gen_random_uuid(), $1, $2, $3)
            """,
            user_id,
            "en,ar",
            "professional"
        )
        
        return {"message": "Business rules reset to defaults"}
        
    except Exception as e:
        logger.error(f"Error resetting business rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset business rules") 