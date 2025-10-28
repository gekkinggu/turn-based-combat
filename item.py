# python
"""item.py

Item.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from action_core import Item_Action

if TYPE_CHECKING:
    from action_core import Action


class Item:
    """Item class representing an item in the game."""

    def __init__(self, name: str, action: Action, quantity = 1) -> None:
        self.name = name
        self.action = action
        self.quantity = quantity
    
    def __repr__(self):
        return f"{self.name}: {self.quantity}"


inventory = [Item("Potion", Item_Action("Potion"), 5)]