# python
"""ui.py

UI system for the turn-based combat game using pygame.
"""

from __future__ import annotations

import pygame
from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass

if TYPE_CHECKING:
    from character import Character
    from battle import Battle
    from action_core import Command, Action

# Color constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
RED = (255, 0, 0)
DARK_RED = (128, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 128)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# UI Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
PANEL_PADDING = 10
MENU_ITEM_HEIGHT = 40


class SelectingState:
    """Indicates the current selection state in the UI."""
    def __init__(self):
        pass
    def __repr__(self) -> str:
        return self.__class__.__name__
    def on_cancel(self, ui: BattleUI) -> None:
        """Handle cancel/back action."""
        pass
    def on_confirm(self, ui: BattleUI, actor: Character) -> None:
        """Handle confirm/select action."""
        pass
    def on_navigate(self, ui: BattleUI, direction: int) -> None:
        """Handle navigation (up/down) action."""
        pass


class SelectingCommand(SelectingState):
    """State for selecting a command."""
    def __init__(self):
        super().__init__()
    def on_cancel(self, ui):
        pass
    def on_confirm(self, ui, actor: Character):
        selected = ui.command_menu.get_selected_item()
        if selected and selected.enabled:

            selected_command = selected.data
            ui.selected_command = selected_command
            if selected_command.is_single:
                ui.selected_action = selected_command.actions[0]
                ui.setup_target_menu(ui.selected_action, actor)
                ui.selecting_state = SelectingTarget()
            else:
                ui.setup_action_menu(selected_command, actor)
                ui.selecting_state = SelectingAction()
    def on_navigate(self, ui, direction: int):
        ui.command_menu.move_selection(direction)


class SelectingAction(SelectingState):
    """State for selecting an action."""
    def __init__(self):
        super().__init__()
    def on_cancel(self, ui):
        ui.selecting_state = SelectingCommand()
    def on_confirm(self, ui, actor: Character):
        selected = ui.action_menu.get_selected_item()
        if selected and selected.enabled:
            selected_action = selected.data
            ui.selected_action = selected_action
            ui.setup_target_menu(selected_action, actor)
            ui.selecting_state = SelectingTarget()
    def on_navigate(self, ui, direction: int):
        ui.action_menu.move_selection(direction)    
    

class SelectingTarget(SelectingState):
    """State for selecting targets."""
    def __init__(self):
        super().__init__()
    def on_cancel(self, ui):
        ui.selecting_state = SelectingAction()
    def on_confirm(self, ui, actor: Character):
        selected = ui.target_menu.get_selected_item()
        if selected:
            ui.selected_targets = [selected.data]
            ui.selecting_state = SelectionFinished()
    def on_navigate(self, ui, direction: int):
        ui.target_menu.move_selection(direction)


class SelectionFinished(SelectingState):
    """State indicating selection is finished."""
    def __init__(self):
        super().__init__()


# @dataclass
# class UIState:
#     """Stores the current UI selection state."""
#     selected_command: Command | None = None
#     selected_action: Action | None = None
#     selected_targets: list[Character] = None
#     menu_index: int = 0
#     submenu_index: int = 0
#     in_submenu: bool = False
#     targeting: bool = False
    
#     def reset(self) -> None:
#         """Reset the UI state."""
#         self.selected_command = None
#         self.selected_action = None
#         self.selected_targets = []
#         self.menu_index = 0
#         self.submenu_index = 0
#         self.in_submenu = False
#         self.targeting = False


class Button:
    """A clickable button UI element."""
    
    def __init__(self, rect: pygame.Rect, text: str, 
                 color: tuple = DARK_BLUE, hover_color: tuple = BLUE):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button on the surface."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos: tuple[int, int]) -> None:
        """Check if the mouse is hovering over the button."""
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos: tuple[int, int]) -> bool:
        """Check if the button was clicked."""
        return self.rect.collidepoint(pos)


class MenuItem:
    """A selectable menu item."""
    
    def __init__(self, text: str, data: any = None, enabled: bool = True):
        self.text = text
        self.data = data  # Can store Command, Action, Character, etc.
        self.enabled = enabled


class Menu:
    """A menu that displays selectable items."""
    
    def __init__(self, rect: pygame.Rect, title: str = ""):
        self.rect = rect
        self.title = title
        self.items: list[MenuItem] = []
        self.selected_index = 0
        self.scroll_offset = 0
        
    def set_items(self, items: list[MenuItem]) -> None:
        """Set the menu items."""
        self.items = items
        self.selected_index = 0
        self.scroll_offset = 0
        
    def move_selection(self, delta: int) -> None:
        """Move the selection up or down."""
        if not self.items:
            return
            
        old_index = self.selected_index
        self.selected_index = (self.selected_index + delta) % len(self.items)
        
        # Skip disabled items
        attempts = 0
        while not self.items[self.selected_index].enabled and attempts < len(self.items):
            self.selected_index = (self.selected_index + delta) % len(self.items)
            attempts += 1
            
    def get_selected_item(self) -> MenuItem | None:
        """Get the currently selected menu item."""
        if self.items and 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None
        
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the menu on the surface."""
        # Draw background
        pygame.draw.rect(surface, DARK_GRAY, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        y_offset = self.rect.y + PANEL_PADDING
        
        # Draw title
        if self.title:
            title_surf = font.render(self.title, True, YELLOW)
            surface.blit(title_surf, (self.rect.x + PANEL_PADDING, y_offset))
            y_offset += 30
            
        # Calculate visible items
        max_visible = (self.rect.height - y_offset + self.rect.y - PANEL_PADDING) // MENU_ITEM_HEIGHT
        
        # Draw items
        for i, item in enumerate(self.items[self.scroll_offset:self.scroll_offset + max_visible]):
            actual_index = i + self.scroll_offset
            item_rect = pygame.Rect(
                self.rect.x + PANEL_PADDING,
                y_offset + i * MENU_ITEM_HEIGHT,
                self.rect.width - 2 * PANEL_PADDING,
                MENU_ITEM_HEIGHT - 5
            )
            
            # Highlight selected item
            if actual_index == self.selected_index:
                pygame.draw.rect(surface, BLUE, item_rect)
            elif not item.enabled:
                pygame.draw.rect(surface, DARK_RED, item_rect)
            else:
                pygame.draw.rect(surface, GRAY, item_rect)
                
            pygame.draw.rect(surface, WHITE, item_rect, 1)
            
            # Draw text
            color = LIGHT_GRAY if not item.enabled else WHITE
            text_surf = font.render(item.text, True, color)
            surface.blit(text_surf, (item_rect.x + 5, item_rect.y + 10))


class BattleUI:
    """Main UI controller for the battle system."""
    
    def __init__(self, screen: pygame.Surface, battle: Battle):
        self.screen = screen
        self.battle = battle
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.large_font = pygame.font.Font(None, 36)
        
        self.selecting_state: SelectingState = SelectingCommand()
        self.selected_command: Command | None = None
        self.selected_action: Action | None = None
        self.selected_targets: list[Character] = []
        
        # Create UI panels
        self.command_menu = Menu(
            pygame.Rect(20, 450, 300, 230),
            "Commands"
        )
        
        self.action_menu = Menu(
            pygame.Rect(340, 450, 300, 230),
            "Actions"
        )
        
        self.target_menu = Menu(
            pygame.Rect(660, 450, 320, 230),
            "Select Target"
        )
        
        # Battle log
        self.log_messages: list[str] = []
        self.max_log_messages = 5
        
    def add_log_message(self, message: str) -> None:
        """Add a message to the battle log."""
        self.log_messages.append(message)
        if len(self.log_messages) > self.max_log_messages:
            self.log_messages.pop(0)
            
    def clear_log(self) -> None:
        """Clear the battle log."""
        self.log_messages.clear()
        
    def draw_character_status(self, character: Character, rect: pygame.Rect, 
                             is_enemy: bool = False) -> None:
        """Draw a character's status panel."""
        # Background
        color = DARK_RED if is_enemy else DARK_BLUE
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, WHITE, rect, 2)
        
        y_offset = rect.y + 5
        x_offset = rect.x + 10
        
        # Name
        name_surf = self.font.render(character.name, True, WHITE)
        self.screen.blit(name_surf, (x_offset, y_offset))
        y_offset += 30
        
        # Level
        level_text = f"Lv. {character.level}"
        level_surf = self.small_font.render(level_text, True, LIGHT_GRAY)
        self.screen.blit(level_surf, (x_offset, y_offset))
        y_offset += 25
        
        # HP Bar
        hp_percentage = character.hp / character.hp_max if character.hp_max > 0 else 0
        hp_text = f"HP: {character.hp}/{character.hp_max}"
        hp_surf = self.small_font.render(hp_text, True, WHITE)
        self.screen.blit(hp_surf, (x_offset, y_offset))
        y_offset += 20
        
        bar_width = rect.width - 20
        bar_height = 15
        bar_rect = pygame.Rect(x_offset, y_offset, bar_width, bar_height)
        pygame.draw.rect(self.screen, DARK_GRAY, bar_rect)
        
        hp_bar_width = int(bar_width * hp_percentage)
        hp_bar_rect = pygame.Rect(x_offset, y_offset, hp_bar_width, bar_height)
        hp_color = GREEN if hp_percentage > 0.5 else (YELLOW if hp_percentage > 0.25 else RED)
        pygame.draw.rect(self.screen, hp_color, hp_bar_rect)
        pygame.draw.rect(self.screen, WHITE, bar_rect, 1)
        y_offset += 20
        
        # MP Bar
        mp_percentage = character.mp / character.mp_max if character.mp_max > 0 else 0
        mp_text = f"MP: {character.mp}/{character.mp_max}"
        mp_surf = self.small_font.render(mp_text, True, WHITE)
        self.screen.blit(mp_surf, (x_offset, y_offset))
        y_offset += 20
        
        mp_bar_rect = pygame.Rect(x_offset, y_offset, bar_width, bar_height)
        pygame.draw.rect(self.screen, DARK_GRAY, mp_bar_rect)
        
        mp_bar_width = int(bar_width * mp_percentage)
        mp_bar_fill = pygame.Rect(x_offset, y_offset, mp_bar_width, bar_height)
        pygame.draw.rect(self.screen, CYAN, mp_bar_fill)
        pygame.draw.rect(self.screen, WHITE, mp_bar_rect, 1)
        y_offset += 20
        
        # ATB Gauge
        atb_percentage = min(character.atb / self.battle.READY_THRESHOLD, 1.0)
        atb_text = f"ATB: {int(atb_percentage * 100)}%"
        atb_surf = self.small_font.render(atb_text, True, WHITE)
        self.screen.blit(atb_surf, (x_offset, y_offset))
        y_offset += 20
        
        atb_bar_rect = pygame.Rect(x_offset, y_offset, bar_width, bar_height)
        pygame.draw.rect(self.screen, DARK_GRAY, atb_bar_rect)
        
        atb_bar_width = int(bar_width * atb_percentage)
        atb_bar_fill = pygame.Rect(x_offset, y_offset, atb_bar_width, bar_height)
        atb_color = YELLOW if atb_percentage >= 1.0 else BLUE
        pygame.draw.rect(self.screen, atb_color, atb_bar_fill)
        pygame.draw.rect(self.screen, WHITE, atb_bar_rect, 1)
        y_offset += 25
        
        # Status effects
        if character.statuses:
            status_text = "Status: " + ", ".join([str(s) for s in character.statuses[:2]])
            if len(character.statuses) > 2:
                status_text += "..."
            status_surf = self.small_font.render(status_text, True, MAGENTA)
            self.screen.blit(status_surf, (x_offset, y_offset))
            
    def draw_party_status(self) -> None:
        """Draw status panels for all party members."""
        panel_width = 240
        panel_height = 200
        spacing = 20
        
        for i, character in enumerate(self.battle.party):
            if character in self.battle.graveyard:
                continue
            rect = pygame.Rect(
                20 + i * (panel_width + spacing),
                20,
                panel_width,
                panel_height
            )
            self.draw_character_status(character, rect, is_enemy=False)
            
    def draw_enemy_status(self) -> None:
        """Draw status panels for all enemies."""
        panel_width = 240
        panel_height = 200
        spacing = 20
        start_x = SCREEN_WIDTH - panel_width - 20
        
        for i, character in enumerate(self.battle.enemies):
            if character in self.battle.graveyard:
                continue
            rect = pygame.Rect(
                start_x - i * (panel_width + spacing),
                20,
                panel_width,
                panel_height
            )
            self.draw_character_status(character, rect, is_enemy=True)
            
    def draw_battle_log(self) -> None:
        """Draw the battle log."""
        log_rect = pygame.Rect(20, 240, SCREEN_WIDTH - 40, 190)
        pygame.draw.rect(self.screen, DARK_GRAY, log_rect)
        pygame.draw.rect(self.screen, WHITE, log_rect, 2)
        
        # Title
        title_surf = self.font.render("Battle Log", True, YELLOW)
        self.screen.blit(title_surf, (log_rect.x + 10, log_rect.y + 5))
        
        # Messages
        y_offset = log_rect.y + 40
        for message in self.log_messages[-5:]:  # Show last 5 messages
            msg_surf = self.small_font.render(message, True, WHITE)
            self.screen.blit(msg_surf, (log_rect.x + 10, y_offset))
            y_offset += 30
            
    def draw_current_turn_indicator(self, actor: Character) -> None:
        """Draw an indicator showing whose turn it is."""
        indicator_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250, 300, 50)
        pygame.draw.rect(self.screen, DARK_GREEN, indicator_rect)
        pygame.draw.rect(self.screen, YELLOW, indicator_rect, 3)
        
        text = f"{actor.name}'s Turn!"
        text_surf = self.large_font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=indicator_rect.center)
        self.screen.blit(text_surf, text_rect)
        
    def setup_command_menu(self, actor: Character) -> None:
        """Setup the command menu for the current actor."""
        items = []
        for command in actor.commands:
            # Check if command has usable actions
            enabled = True
            if command.name == "Magic":
                enabled = len(command.actions) > 0
            elif command.name == "Item":
                enabled = len(self.battle.inventory) > 0
                
            items.append(MenuItem(command.name, command, enabled))
            
        self.command_menu.set_items(items)
        
    def setup_action_menu(self, command: Command, actor: Character) -> None:
        """Setup the action menu for the selected command."""
        items = []
        
        if command.name == "Item":
            # Show items from inventory
            for item in self.battle.inventory:
                items.append(MenuItem(item.name, item, True))
        else:
            # Show actions from command
            for action in command.actions:
                # Check if actor has enough MP
                enabled = actor.mp >= action.mp_cost
                mp_text = f" (MP: {action.mp_cost})" if action.mp_cost > 0 else ""
                text = f"{action.name}{mp_text}"
                items.append(MenuItem(text, action, enabled))
                
        self.action_menu.set_items(items)
        
    def setup_target_menu(self, action: Action, actor: Character) -> None:
        """Setup the target menu based on the action's targeting."""
        items = []
        
        # Determine valid targets based on action type
        if action.targetting in ["Single Enemy", "All Enemies"]:
            targets = [e for e in self.battle.enemies if e not in self.battle.graveyard]
        elif action.targetting in ["Single Ally", "All Allies"]:
            targets = [p for p in self.battle.party if p not in self.battle.graveyard]
        elif action.targetting == "Self":
            targets = [actor]
        else:  # "All"
            targets = [b for b in self.battle.battlers if b not in self.battle.graveyard]
            
        for target in targets:
            hp_text = f" (HP: {target.hp}/{target.hp_max})"
            text = f"{target.name}{hp_text}"
            items.append(MenuItem(text, target, True))
            
        self.target_menu.set_items(items)
        
    def handle_input(self, event: pygame.event.Event, actor: Character):
        """
        Handle user input for command selection.
        Returns True when a complete action is selected.
        """
        if event.type != pygame.KEYDOWN:
            return False
            
        # Cancel/Back
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
            self.selecting_state.on_cancel(self)
                
        # Navigation
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            self.selecting_state.on_navigate(self, -1)
                
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            self.selecting_state.on_navigate(self, 1)

        # Confirm selection
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self.selecting_state.on_confirm(self, actor)

        # Check if selection is finished
        if isinstance(self.selecting_state, SelectionFinished):
            self.selecting_state = SelectingCommand()  # Reset for next turn
            return True  # Action selection complete

    def draw(self, actor: Character | None = None) -> None:
        """Draw the complete battle UI."""
        self.screen.fill(BLACK)
        
        # Draw character status panels
        self.draw_party_status()
        self.draw_enemy_status()
        
        # Draw battle log
        self.draw_battle_log()
        
        # If in player turn, draw menus
        if actor and actor.is_controllable:
            self.draw_current_turn_indicator(actor)
            
            # Draw appropriate menus based on state
            self.command_menu.draw(self.screen, self.font)
            
            if isinstance(self.selecting_state, SelectingAction):
                self.action_menu.draw(self.screen, self.font)
                
            if isinstance(self.selecting_state, SelectingTarget):
                self.target_menu.draw(self.screen, self.font)
                
        pygame.display.flip()

