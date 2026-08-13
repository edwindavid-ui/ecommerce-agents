from typing import Any, Optional

from app.schemas.seller_agent import SellerAgentCreate


class SellerAgentRepository:
    def __init__(self, collection: Any):
        self.collection = collection
        self._agents: dict[str, dict] = {}

    async def create_agent(self, agent_data: SellerAgentCreate) -> dict:
        agent_id = f"agent_{len(self._agents) + 1}"
        
        agent = {
            "id": agent_id,
            "seller_id": agent_data.seller_id,
            "product_id": agent_data.product_id,
            "list_price": agent_data.list_price,
            "min_price": agent_data.min_price,
            "target_price": agent_data.target_price,
            "max_negotiation_rounds": agent_data.max_negotiation_rounds,
            "current_round": 0,
            "status": "active",
        }
        self._agents[agent_id] = agent
        return agent

    async def get_agent_by_id(self, agent_id: str) -> Optional[dict]:
        return self._agents.get(agent_id)

    async def get_agent_by_seller_and_product(self, seller_id: str, product_id: str) -> Optional[dict]:
        for agent in self._agents.values():
            if agent["seller_id"] == seller_id and agent["product_id"] == product_id:
                return agent
        return None

    async def list_agents_by_seller(self, seller_id: str) -> list[dict]:
        return [a for a in self._agents.values() if a["seller_id"] == seller_id]

    async def update_agent_round(self, agent_id: str, round_num: int) -> Optional[dict]:
        agent = self._agents.get(agent_id)
        if not agent:
            return None
        agent["current_round"] = round_num
        return agent

    async def update_agent_status(self, agent_id: str, status: str) -> Optional[dict]:
        agent = self._agents.get(agent_id)
        if not agent:
            return None
        agent["status"] = status
        return agent
