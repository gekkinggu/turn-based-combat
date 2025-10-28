# Turn-Based Combat System

A robust turn-based combat system with an integrated UI built using pygame.

## Features

- **ATB (Active Time Battle) System**: Characters act based on their speed and ATB gauge
- **Rich UI System**: Visual representation of battle state with status panels, menus, and battle log
- **Command System**: Select commands, actions, and targets through an intuitive menu system
- **Status Effects**: Apply buffs, debuffs, and special status effects to characters
- **Flexible Action System**: Support for various action types (attacks, spells, items, etc.)
- **Enemy AI**: Automated behavior system for enemy characters

## Installation

1. Make sure you have Python 3.10+ installed
2. Install pygame:

```bash
pip install pygame
```

## Running the Game

To start a battle simulation:

```bash
python game.py
```

## Controls

### During Battle

- **↑/W**: Move selection up
- **↓/S**: Move selection down
- **Enter/Space**: Confirm selection
- **Escape/Backspace**: Go back to previous menu

### Menu Navigation Flow

1. **Command Selection**: Choose Attack, Abilities, Magic, or Items
2. **Action Selection**: Select specific action from the chosen command
3. **Target Selection**: Choose target(s) for the action

### After Battle

- **R**: Restart battle
- **Q**: Quit game

## UI Components

### Character Status Panels
- **Name and Level**: Character identification
- **HP Bar**: Current and maximum hit points (Green → Yellow → Red)
- **MP Bar**: Current and maximum magic points (Cyan)
- **ATB Gauge**: Action readiness indicator (Blue → Yellow when ready)
- **Status Effects**: Active buffs and debuffs

### Battle Log
- Shows recent battle events
- Displays actions, damage, healing, and status changes

### Command Menus
- **Commands**: Primary action categories
- **Actions**: Specific moves within a category
- **Targets**: Available targets for the selected action

## File Structure

```
├── game.py           # Main game loop and battle integration
├── ui.py             # UI system with menus and visual elements
├── battle.py         # Battle state machine and logic
├── character.py      # Character class and stats
├── action_core.py    # Actions, commands, and status effects
├── behaviour.py      # AI behavior patterns
├── item.py           # Item system
└── definitions/      # CSV data files
    ├── actions.csv
    ├── battlers.csv
    └── statuses.csv
```

## Customization

### Creating Characters

```python
from character import Character, Enemy

# Create a player character
warrior = Character("Warrior", 50)

# Create an enemy
goblin = Enemy("Goblin", 40)
```

### Starting a Battle

```python
from game import Game
from character import Character, Enemy
import pygame

pygame.init()
screen = pygame.display.set_mode((1000, 700))
game = Game(screen)

# Create party and enemies
party = [Character("Warrior", 50), Character("Mage", 45)]
enemies = [Enemy("Goblin", 40), Enemy("Orc", 45)]

# Start the battle
game.start_battle(party, enemies)
```

### Defining Custom Actions

Edit `definitions/actions.csv` to add new actions with custom properties:
- name: Action name
- type: Action type (e.g., "Damage Single", "Heal All")
- potency: Base damage/healing value
- is_physical: Whether it uses physical or magical stats
- element: Elemental affinity
- targetting: Who can be targeted
- mp_cost: MP required to use

### Defining Characters

Edit `definitions/battlers.csv` to create new character types with:
- Base stats (HP, MP, Strength, Defense, Magic, etc.)
- Abilities and spells
- Elemental affinities
- Speed

## Architecture

### Battle State Machine

The battle system uses a state machine pattern with the following states:

1. **Waiting**: ATB gauges fill, characters become ready
2. **SpeedTie**: Resolves simultaneous readiness
3. **PrepareActor**: Initializes a character's turn
4. **ControlledTurn**: Player-controlled character's turn
5. **SelectingCommands**: UI handles player input (NEW - integrated with UI)
6. **AITurn**: AI executes automated behavior
7. **CheckingDeath**: Checks for defeated characters
8. **EndingTurn**: Finalizes turn and updates effects
9. **Burying**: Removes defeated characters
10. **Victory/Loss**: Battle end states

### UI State Management

The UI system maintains its own state for menu navigation:
- **Command Selection**: Choosing attack/magic/item/ability
- **Action Selection**: Picking specific action from command
- **Target Selection**: Selecting battle participants

## Code Integration

The UI system integrates with the battle system through the `SelectingCommands` state:

```python
# In battle.py
class SelectingCommands(BattleState):
    def __init__(self, actor: Character) -> None:
        super().__init__()
        self.actor = actor
        self.action_selected = False  # UI sets this when ready

    def loop(self, battle: Battle, dt: float) -> None:
        if self.action_selected:
            battle.state = CheckingDeath()
```

The UI handles all player input and executes actions when complete:

```python
# In game.py
def handle_battle_input(self, event: pygame.event.Event) -> None:
    if isinstance(self.battle.state, SelectingCommands):
        actor = self.battle.state.actor
        action_complete = self.battle_ui.handle_input(event, actor)
        
        if action_complete:
            self.battle_ui.execute_selected_action(actor)
            self.battle.state.action_selected = True
```

## Future Enhancements

- Sound effects and music
- Battle animations
- More complex AI patterns
- Multiplayer support
- Save/load battle states
- Character progression system
- Equipment and inventory management

## License

This project is open source and available for educational purposes.
