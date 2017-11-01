from roboscaffold_sim.message.message import Message
from typing import List


class MessageQueue:
    def __init__(self) -> None:
        self.message: List(Message) = []
