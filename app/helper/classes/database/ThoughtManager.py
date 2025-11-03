from .BaseManager import BaseManager
from app.database.models import Thought, Profile, ProfileIdentity
from app.helper.functions.response_schemas import success_res, error_res
from flask import Flask, current_app
from sqlalchemy import select, extract, cast, Date
from datetime import datetime, timezone

class ThoughtManager(BaseManager):
    def __init__(self, db_manager_instance) -> None:
        super().__init__(db_manager_instance)
    
    def get_thought_by_id(self, thought_id) -> Thought | None:
        if not thought_id:
            return None

        return self._session.get(Thought, thought_id)
    
    def create_thought(self, profile: Profile, profile_identity: ProfileIdentity, content):
        if not content or not profile or not profile_identity:
            return error_res("Missing core data to construct thought")

        profile_id = profile.id
        profile_identity_id = profile_identity.id

        try:
            new_thought = Thought(
                profile_id=profile_id, 
                profile_identity_id=profile_identity_id,
                content=content
            )
            
            self._session.add(new_thought)
            self._session.commit()
            return success_res(payload={}, msg="Thought created!")
        except Exception as e:
            self._session.rollback()
            return error_res(msg=f"Error creating thought. Error {e}")
    
    def get_ordered_thoughts(self, identity_id, **filter_kwargs):
        if not identity_id:
            return error_res("Identity not given")
        
        query = select(Thought).where(
            Thought.profile_identity_id == identity_id
        )
        
        year = filter_kwargs.get("year")
        month = filter_kwargs.get("month")

        if year and month:
            query = query.where(
                extract('year', Thought.created_at) == year,
                extract('month', Thought.created_at) == month
            )
        else:
            today = datetime.now(timezone.utc).date()
            query = query.where(
                cast(Thought.created_at, Date) == today
            )
        
        try:
            res = self._session.scalars(
                query.order_by(Thought.created_at.asc())
            ).all()

            return success_res(payload={ "thoughts": res }, msg="Thoughts found!")

        except Exception as e:
            return error_res(msg=f"Error getting thoughts. Error {e}")
    
    def delete_thought(self, thought_id):
        if not thought_id:
            return error_res("Thought not given")
        
        try:
            thought: Thought | None = self.get_thought_by_id(thought_id)

            if not thought:
                return error_res("Thought not found...")

            self._session.delete(thought)
            self._session.commit()
            return success_res(msg="Thought deleted!", payload={})

        except Exception as e:
            self._session.rollback()
            return error_res(msg=f"Error deleting thoughts. Error {e}")
    
    def edit_thought(self, thought_id, content):
        if not thought_id or not content:
            return error_res("Thought not given")
    
        try:
            thought = self.get_thought_by_id(thought_id)

            if not thought:
                return error_res("Thought not found...")
            
            thought.content = content

            self._session.add(thought)
            self._session.commit()
            return success_res(msg="Thought updated!", payload={})

        except Exception as e:
            self._session.rollback()
            return error_res(msg=f"Error deleting thoughts. Error {e}")

