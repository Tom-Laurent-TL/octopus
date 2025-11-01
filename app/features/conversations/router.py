from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.features.conversations import schemas
from app.features.conversations.service import ConversationService, MessageService
from app.db.database import get_db
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("/", response_model=schemas.Conversation, status_code=201)
async def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db)
):
    """Create a new conversation with optional participants."""
    return ConversationService.create_conversation(
        db, 
        title=conversation.title,
        participant_ids=conversation.participant_ids
    )


@router.get("/", response_model=List[schemas.Conversation])
async def list_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all conversations."""
    return ConversationService.list_conversations(db, skip=skip, limit=limit)


@router.get("/user/{user_id}", response_model=List[schemas.Conversation])
async def list_user_conversations(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all conversations for a specific user."""
    return ConversationService.list_user_conversations(db, user_id, skip=skip, limit=limit)


@router.get("/{conversation_id}", response_model=schemas.Conversation)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages."""
    conversation = ConversationService.get_conversation(db, conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.put("/{conversation_id}", response_model=schemas.Conversation)
async def update_conversation(
    conversation_id: int,
    conversation_update: schemas.ConversationUpdate,
    db: Session = Depends(get_db)
):
    """Update a conversation."""
    conversation = ConversationService.update_conversation(
        db, 
        conversation_id, 
        title=conversation_update.title
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages."""
    deleted = ConversationService.delete_conversation(db, conversation_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return None


@router.post("/{conversation_id}/messages", response_model=schemas.Message, status_code=201)
async def add_message(
    conversation_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db)
):
    """Add a message to a conversation."""
    # Check if conversation exists
    conversation = ConversationService.get_conversation(db, conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Validate role
    if message.role not in ['user', 'assistant', 'system']:
        raise HTTPException(status_code=400, detail="Role must be 'user', 'assistant', or 'system'")
    
    # If user_id provided, verify user is a participant
    if message.user_id:
        user_ids = [p.id for p in conversation.participants]
        if message.user_id not in user_ids:
            raise HTTPException(status_code=403, detail="User is not a participant in this conversation")
    
    return MessageService.add_message(
        db, 
        conversation_id=conversation_id,
        role=message.role,
        content=message.content,
        user_id=message.user_id
    )


@router.get("/{conversation_id}/messages", response_model=List[schemas.Message])
async def get_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all messages from a conversation."""
    # Check if conversation exists
    conversation = ConversationService.get_conversation(db, conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return MessageService.get_messages(db, conversation_id, skip=skip, limit=limit)


@router.post("/{conversation_id}/participants", response_model=schemas.Conversation, status_code=201)
async def add_participant(
    conversation_id: int,
    participant: schemas.ConversationAddParticipant,
    db: Session = Depends(get_db)
):
    """Add a participant to a conversation."""
    conversation = ConversationService.add_participant(db, conversation_id, participant.user_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation or user not found")
    
    return conversation


@router.delete("/{conversation_id}/participants/{user_id}", response_model=schemas.Conversation)
async def remove_participant(
    conversation_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Remove a participant from a conversation."""
    conversation = ConversationService.remove_participant(db, conversation_id, user_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation or user not found")
    
    return conversation
