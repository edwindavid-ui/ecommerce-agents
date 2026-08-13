from datetime import datetime, timezone
from typing import Any, Optional

from app.schemas.buyer_agent import BuyerTaskCreate, BuyerAgentState


class BuyerTaskRepository:
    def __init__(self, collection: Any):
        self.collection = collection
        self._tasks: dict[str, dict] = {}

    async def create_task(self, task_data: BuyerTaskCreate) -> dict:
        task_id = f"task_{len(self._tasks) + 1}"
        now = datetime.now(timezone.utc).isoformat()
        
        task = {
            "id": task_id,
            "buyer_id": task_data.buyer_id,
            "requirement": task_data.requirement,
            "budget": task_data.budget,
            "category": task_data.category,
            "min_price": task_data.min_price,
            "status": "task_created",
            "selected_seller_id": None,
            "selected_product_id": None,
            "recommendation_id": None,
            "created_at": now,
            "updated_at": now,
        }
        self._tasks[task_id] = task
        return task

    async def get_task_by_id(self, task_id: str) -> Optional[dict]:
        return self._tasks.get(task_id)

    async def update_task_status(self, task_id: str, status: str) -> Optional[dict]:
        task = self._tasks.get(task_id)
        if not task:
            return None
        task["status"] = status
        task["updated_at"] = datetime.now(timezone.utc).isoformat()
        return task

    async def update_task_with_recommendation(self, task_id: str, recommendation_id: str) -> Optional[dict]:
        task = self._tasks.get(task_id)
        if not task:
            return None
        task["recommendation_id"] = recommendation_id
        task["updated_at"] = datetime.now(timezone.utc).isoformat()
        return task

    async def list_tasks_by_buyer(self, buyer_id: str) -> list[dict]:
        return [t for t in self._tasks.values() if t["buyer_id"] == buyer_id]


class BuyerAgentStateRepository:
    def __init__(self, collection: Any):
        self.collection = collection
        self._states: dict[str, dict] = {}

    async def save_state(self, task_id: str, state: BuyerAgentState) -> dict:
        saved_state = state.model_dump()
        self._states[task_id] = saved_state
        return saved_state

    async def get_state(self, task_id: str) -> Optional[dict]:
        return self._states.get(task_id)

    async def append_to_history(self, task_id: str, event: dict) -> Optional[dict]:
        state = self._states.get(task_id)
        if not state:
            return None
        state["history"].append(event)
        return state
