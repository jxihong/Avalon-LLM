import numpy as np
from typing import List
from .agent import GOPSAgent
from src.server.task import Session
class NaiveGOPSAgent(GOPSAgent):
    def __init__(self, id: int, hand: List[int], session: Session) -> None:
        super().__init__(
            id       =    id,
            hand     =    hand,
        )
        self.session = session

    def __repr__(self) -> str:
        return "Player {}".format(self.id)

    async def play_card(self) -> int:
        card_id = np.random.choice(len(self.hand))
        card = self.hand[card_id]
        self.hand = np.delete(self.hand, np.where(self.hand == card))
        return card