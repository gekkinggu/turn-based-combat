# python
"""game.py

Game module for the turn-based combat system with integrated UI.
"""

from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from battle import Battle, ControlledTurn, SelectingTieWinner, Victory
from battle import Loss
from character import Character, Enemy
from ui_copy import BattleUI, SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    pass


class Game:
    """Game class for the turn-based combat system."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.battle: Battle | None = None
        self.battle_ui: BattleUI | None = None
        self.in_battle = False
        
    def start_battle(self, party: list[Character], enemies: list[Character]
                     ) -> None:
        """Initialize and start a battle."""
        self.battle = Battle(party, enemies)
        self.battle_ui = BattleUI(self.screen, self.battle)
        self.in_battle = True
        self.battle_ui.add_log_message("Battle started!")
        
    def update_battle(self, dt: float) -> None:
        """Update the battle state."""
        if not self.battle or not self.in_battle:
            return
            
        # Update battle logic
        self.battle.loop(dt)
        
        while self.battle.log_messages:
            self.battle_ui.add_log_message(self.battle.log_messages.pop(0))

        # Check for battle end
        if isinstance(self.battle.state, Victory):
            self.battle_ui.add_log_message("Victory! You defeated all enemies!")
            self.in_battle = False
        elif isinstance(self.battle.state, Loss):
            self.battle_ui.add_log_message("Defeat! Your party was wiped out!")
            self.in_battle = False
            
    def handle_battle_input(self, event: pygame.event.Event) -> None:
        """Handle input during battle."""
        if not self.battle or not self.battle_ui or not self.in_battle:
            return
            
        # Only handle input during ControlledTurn state
        if isinstance(self.battle.state, ControlledTurn):
            actor = self.battle.state.actor
            
            # Initialize the command menu if not already done
            if not self.battle_ui.selected_command and not self.battle_ui.command_menu.items:
                self.battle_ui.setup_command_menu(actor)
                
            # Handle input and check if action is complete            
            if self.battle_ui.handle_input(event, actor):
                # Signal back to Battle the selected action and targets
                self.battle.state.selected_action = self.battle_ui.selected_action
                self.battle.state.selected_targets = self.battle_ui.selected_targets
                
        # Handle tie winner selection
        elif isinstance(self.battle.state, SelectingTieWinner):
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    # Select tie winner by number key
                    key_num = int(event.unicode) if event.unicode.isdigit() else 0
                    if 1 <= key_num <= len(self.battle.state.people_in_tie):
                        tie_winner = self.battle.state.people_in_tie[key_num - 1]
                        self.battle.ready_actors = [tie_winner]
                        from battle import PrepareActor
                        self.battle.state = PrepareActor(tie_winner)
                        self.battle_ui.add_log_message(f"{tie_winner.name} wins the speed tie!")
                           
    def draw_battle(self) -> None:
        """Draw the battle UI."""
        if not self.battle or not self.battle_ui:
            return
            
        # Determine current actor for UI display
        current_actor = None
        if isinstance(self.battle.state, ControlledTurn):
            current_actor = self.battle.state.actor
            
        self.battle_ui.draw(current_actor)


def main():
    """Main game loop."""
    pygame.init()
    pygame.display.set_caption("Turn-Based Combat System")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = Game(screen)
    
    # Create test battle
    warrior = Character("Warrior", 50)
    mage = Character("Mage", 50)
    
    enemy1 = Enemy("Goblin", 40)
    enemy2 = Enemy("Orc", 45)
    
    game.start_battle(party=[warrior, mage], enemies=[enemy1, enemy2])
    
    running = True
    while running:
        dt = game.clock.tick(60) / 1000  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                # Handle battle input
                game.handle_battle_input(event)
        
        # Update battle
        if game.in_battle:
            game.update_battle(dt)
            game.draw_battle()
        else:
            # Battle ended - show results
            game.draw_battle()
            
            # Draw "Battle Ended" message
            font = pygame.font.Font(None, 72)
            if game.battle:
                outcome_text = game.battle.outcome if game.battle.outcome else "Battle Ended"
                text_surf = font.render(outcome_text, True, (255, 255, 0))
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                       SCREEN_HEIGHT // 2))
                screen.blit(text_surf, text_rect)
                
                # Draw restart prompt
                small_font = pygame.font.Font(None, 36)
                prompt_surf = small_font.render("Press R to restart or Q to quit", True, (255, 255, 255))
                prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                           SCREEN_HEIGHT // 2 + 60))
                screen.blit(prompt_surf, prompt_rect)
            
            pygame.display.flip()
            
            # Check for restart/quit
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                # Restart battle
                warrior = Character("Warrior", 50)
                mage = Character("Mage", 50)
                enemy1 = Enemy("Goblin", 40)
                enemy2 = Enemy("Orc", 45)
                game.start_battle(party=[warrior, mage], enemies=[enemy1, enemy2])
            elif keys[pygame.K_q]:
                running = False
    
    pygame.quit()


if __name__ == "__main__":
    main()