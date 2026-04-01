from typing import Optional
from uuid import UUID
import os 
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from groq import Groq

import models
import schemas
from database import get_db 
from dependencies import get_current_user

#Initialiing the Groq Client
groq_client = Groq(api_key = os.getenv("GROQ_API_KEY"))

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("/analyze", response_model=schemas.ConversationAnalysisResponse)
def analyze_conversation(
    conversation_input: schemas.ConversationInput,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    raw_text = conversation_input.raw_text

    prompt = f"""You are a sales coach AI analyzing a client's conversation. Extract actionale insights and return ONLY valid JSON (no markdown, no extra text).models
    
    CONVERSTATION:
    {raw_text}
    Analyze this conversation and return a JSON object with this EXACT structure:
    {{
        "contact_name": "First name or full name if mentioned, or null",
        "company": "Company name if mentioned, or null",
        "contact_email": "Email address if mentioned, or null",
        "status": "Hot lead or Warm lead or Cold lead based on the conversation",
        "summary": "2-3 sentence summary of what is happening",
        "blocker": "Main concern or obstacle mentioned, or null",
        "decision_expected": "When they will decide (e.g Next week, By Friday) or null",
        "window_closes": "Specific date/day before decision (e.g Friday March 26), or null",
        "next_action_date": "Suggested date to act (e.g. Thursday March 25), or null",
        "reasoning": "Why this timing/action makes sense based on the conversation",
        "signal_strength": "1/5 or 2/5 or 3/5 or 4/5 or 5/5",
        "signal_factors": ["Factor 1", "Factor 2", "Factor 3"]
    }}

    RULES:
    - Extract contact_name, company, contact_email ONLY if explicitly mentioned
    - For signal_strength: 5/5=clear intent+timeline+no blockers, 4/5=clear intent+timeline+minor blocker, 3/5=intent+vague timeline, 2/5=vague intent+vague timeline, 1/5=no clear intent or timeline
    - Make next_action SPECIFIC
    - Return ONLY the JSON object, no markdown, no explanations
    """

    try:
        response = groq_client.chat.completions.create(
            model = "llama-3.1-8b-instant",
            messages = [
                {
                    "role": "system",
                    "content": "You are a sales coach AI. Analyze conversations and return structured JSON insights."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        ai_response = response.choices[0].message.content

    except Exception as e:
        print(f"DEBUG-GroqAI Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing conversation with AI")
    try:
        ai_data = json.loads(ai_response)
    except json.JSONDecodeError as e:
        print(f"DEBUG-JSON Decode Error: {str(e)}")
        print(f"DEBUG-AI Response: {ai_response}")
        raise HTTPException(status_code=500, detail="AI response is not valid JSON")
    

    new_conversation = models.Conversation(
        user_id = current_user.id,
        raw_text = raw_text,
        extracted_contact_name = ai_data.get("contact_name"),
        extracted_company = ai_data.get("company"),
        extracted_email = ai_data.get("contact_email"),
        ai_summary = ai_data.get("summary"),
        ai_next_action = ai_data.get("next_action"),
        ai_follow_up_date=ai_data.get("next_action_date"),
        ai_sentiment = ai_data.get("status"),
        ai_blocker = ai_data.get("blocker"),
    )
    
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)

    deal_insight = schemas.DealInsight(
        contact_name=ai_data.get("contact_name"),
        company=ai_data.get("company"),
        contact_email=ai_data.get("contact_email"),
        status=ai_data.get("status", "Warm lead"),
        summary=ai_data.get("summary", ""),
        blocker=ai_data.get("blocker"),
        decision_expected=ai_data.get("decision_expected"),
        window_closes=ai_data.get("window_closes"),
        next_action=ai_data.get("next_action", "Follow up soon"),
        next_action_date=ai_data.get("next_action_date"),
        reasoning=ai_data.get("reasoning", ""),
        signal_strength=ai_data.get("signal_strength", "3/5"),
        signal_factors=ai_data.get("signal_factors", []),
    )

    return schemas.ConversationAnalysisResponse(
        conversation_id=str(new_conversation.id),
        deal_insights=deal_insight,
        raw_text=raw_text,
        created_at=new_conversation.created_at.isoformat(),
        suggest_create_contact=bool(ai_data.get("contact_name") or ai_data.get("company"))
    )


@router.get("/{conversation_id}", response_model=schemas.ConversationAnalysisResponse)
def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == current_user.id
    ).first()
 
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
 
    deal_insight = schemas.DealInsight(
        contact_name=conversation.extracted_contact_name,
        company=conversation.extracted_company,
        contact_email=conversation.extracted_email,
        status=conversation.ai_sentiment or "Warm lead",
        summary=conversation.ai_summary or "",
        blocker=conversation.ai_blocker,
        next_action=conversation.ai_next_action or "Follow up",
        next_action_date=conversation.ai_follow_up_date,
        reasoning="",
        signal_strength=conversation.ai_signal_strength or "3/5",
        signal_factors=[],
    )
 
    return schemas.ConversationAnalysisResponse(
        conversation_id=str(conversation.id),
        deal_insights=deal_insight,
        raw_text=conversation.raw_text,
        created_at=conversation.created_at.isoformat(),
        suggest_create_contact=bool(conversation.extracted_contact_name or conversation.extracted_company)
    )
 