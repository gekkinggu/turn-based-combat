# UI System Architecture

## Overview

The UI system is built using pygame and integrates seamlessly with the existing battle state machine. It provides visual feedback and handles all player input during battles.

## Component Hierarchy

```
Game
├── Battle (battle logic)
│   ├── Battle State Machine
│   └── Characters (party + enemies)
│
└── BattleUI (visual interface)
    ├── Character Status Panels
    ├── Battle Log
    ├── Command Menu
    ├── Action Menu
    └── Target Menu
```

## UI Components

### 1. BattleUI (Main Controller)

The central UI controller that manages all visual elements and user input.

**Responsibilities:**
- Render all UI elements
- Handle keyboard input
- Manage UI state transitions
- Execute selected actions
- Update battle log

**Key Methods:**
- `draw()`: Render the complete UI
- `handle_input()`: Process keyboard events
- `execute_selected_action()`: Perform the selected action

### 2. Menu System

Generic menu component for displaying selectable lists.

**Components:**
- `Menu`: Container for menu items with selection tracking
- `MenuItem`: Individual selectable item with associated data

**Features:**
- Keyboard navigation (up/down)
- Disabled item support
- Automatic scrolling for long lists
- Visual selection highlighting

### 3. Character Status Panel

Visual representation of a character's current state.

**Displays:**
- Character name and level
- HP bar (color-coded by percentage)
- MP bar
- ATB gauge (action readiness)
- Active status effects

**Color Coding:**
- HP: Green (>50%) → Yellow (25-50%) → Red (<25%)
- ATB: Blue (filling) → Yellow (ready)
- Party: Blue background
- Enemies: Red background

### 4. Battle Log

Scrolling text display showing recent battle events.

**Features:**
- Displays last 5 messages
- Auto-scrolls as new messages arrive
- Shows action usage, damage, healing, status changes

### 5. UIState

Tracks the current state of menu navigation.

**Properties:**
```python
selected_command: Optional[Command]    # Selected command (Attack, Magic, etc.)
selected_action: Optional[Action]      # Selected action (Fire, Heal, etc.)
selected_targets: list[Character]      # Selected target(s)
menu_index: int                        # Current menu selection
submenu_index: int                     # Current submenu selection
in_submenu: bool                       # Whether in action submenu
targeting: bool                        # Whether selecting targets
```

## Integration with Battle System

### State Machine Integration

The UI integrates at the `SelectingCommands` state:

```python
# battle.py
class SelectingCommands(BattleState):
    def __init__(self, actor: Character) -> None:
        self.actor = actor
        self.action_selected = False  # UI controls this
    
    def loop(self, battle: Battle, dt: float) -> None:
        # Wait for UI to set action_selected = True
        if self.action_selected:
            battle.state = CheckingDeath()
```

### Input Flow

```
User Input (Keyboard)
    ↓
game.handle_battle_input()
    ↓
battle_ui.handle_input()
    ↓
Menu Navigation / Selection
    ↓
[Action Complete?]
    ↓
battle_ui.execute_selected_action()
    ↓
action.execute(actor, targets, battle)
    ↓
battle.state.action_selected = True
    ↓
Battle continues
```

## Menu Navigation Flow

### Level 1: Command Selection

```
┌─────────────────┐
│   Commands      │
├─────────────────┤
│ > Attack        │ ← Selected
│   Abilities     │
│   Magic         │
│   Items         │
└─────────────────┘
```

**Actions:**
- UP/DOWN: Navigate commands
- ENTER: Select command
  - If single-action (Attack): Jump to targeting
  - Otherwise: Open action submenu

### Level 2: Action Selection

```
┌─────────────────┐  ┌──────────────────┐
│   Commands      │  │   Actions        │
├─────────────────┤  ├──────────────────┤
│   Attack        │  │ > Fire (MP: 10)  │ ← Selected
│ > Magic         │  │   Ice (MP: 10)   │
│   Abilities     │  │   Lightning      │
│   Items         │  │   Heal (MP: 15)  │
└─────────────────┘  └──────────────────┘
```

**Actions:**
- UP/DOWN: Navigate actions
- ENTER: Select action
  - If multi-target (All Enemies): Auto-select targets, execute
  - Otherwise: Open target menu
- ESCAPE: Back to command selection

### Level 3: Target Selection

```
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│   Commands      │  │   Actions        │  │   Select Target      │
├─────────────────┤  ├──────────────────┤  ├──────────────────────┤
│   Attack        │  │   Fire (MP: 10)  │  │ > Goblin (HP: 80/100)│ ← Selected
│ > Magic         │  │ > Ice (MP: 10)   │  │   Orc (HP: 120/150)  │
│   Abilities     │  │   Lightning      │  │   Troll (HP: 200/200)│
│   Items         │  │   Heal (MP: 15)  │  └──────────────────────┘
└─────────────────┘  └──────────────────┘
```

**Actions:**
- UP/DOWN: Navigate targets
- ENTER: Select target, execute action
- ESCAPE: Back to action selection

## Screen Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  ┌──────────────┐  ┌──────────────┐                 ┌──────────────┐ │
│  │  Warrior     │  │  Mage        │                 │  Orc         │ │
│  │  Lv. 50      │  │  Lv. 45      │                 │  Lv. 45      │ │
│  │  HP: ████░░  │  │  HP: ██████  │                 │  HP: ████░░  │ │
│  │  MP: ████░░  │  │  MP: ██░░░░  │                 │  MP: ██████  │ │
│  │  ATB: █████  │  │  ATB: ███░░  │                 │  ATB: ██░░░  │ │
│  └──────────────┘  └──────────────┘                 └──────────────┘ │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  Battle Log                                                      │ │
│  │  ────────────────────────────────────────────────────────────   │ │
│  │  Warrior's Turn!                                                │ │
│  │  Warrior uses Fire on Orc!                                      │ │
│  │  Orc takes 45 damage!                                           │ │
│  │  Orc uses Attack on Mage!                                       │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐  │
│  │  Commands    │  │  Actions     │  │  Select Target             │  │
│  │──────────────│  │──────────────│  │────────────────────────────│  │
│  │ > Attack     │  │ > Fire       │  │ > Goblin (HP: 80/100)      │  │
│  │   Abilities  │  │   Ice        │  │   Orc (HP: 120/150)        │  │
│  │   Magic      │  │   Lightning  │  │   Troll (HP: 200/200)      │  │
│  │   Items      │  │   Heal       │  └────────────────────────────┘  │
│  └──────────────┘  └──────────────┘                                  │
└──────────────────────────────────────────────────────────────────────┘

Dimensions: 1000x700 pixels
```

## Color Scheme

```python
# Primary Colors
BLACK = (0, 0, 0)         # Background
WHITE = (255, 255, 255)   # Text, borders
GRAY = (128, 128, 128)    # Inactive elements
DARK_GRAY = (64, 64, 64)  # Panel backgrounds

# Status Colors
GREEN = (0, 255, 0)       # High HP
YELLOW = (255, 255, 0)    # Medium HP, ready ATB
RED = (255, 0, 0)         # Low HP
CYAN = (0, 255, 255)      # MP bar

# Team Colors
BLUE = (0, 0, 255)        # Party, selected items
DARK_BLUE = (0, 0, 128)   # Party panels
DARK_RED = (128, 0, 0)    # Enemy panels

# Special
MAGENTA = (255, 0, 255)   # Status effects
```

## Keyboard Controls

| Key | Action | Context |
|-----|--------|---------|
| ↑ | Move selection up | Any menu |
| ↓ | Move selection down | Any menu |
| W | Move selection up (alternate) | Any menu |
| S | Move selection down (alternate) | Any menu |
| Enter | Confirm selection | Any menu |
| Space | Confirm selection (alternate) | Any menu |
| Escape | Cancel / Go back | Submenus only |
| Backspace | Cancel / Go back (alternate) | Submenus only |
| R | Restart battle | Battle ended |
| Q | Quit game | Battle ended |

## Extension Points

### Adding New UI Elements

1. **New Panel Type**:
   - Create drawing method in `BattleUI`
   - Call from `draw()` method
   - Update layout constants if needed

2. **New Menu**:
   - Create `Menu` instance in `BattleUI.__init__()`
   - Add setup method for populating items
   - Handle in `handle_input()` method

3. **New Visual Effect**:
   - Add drawing code in appropriate method
   - Use pygame drawing primitives
   - Follow existing color scheme

### Customization Examples

**Change UI Colors:**
```python
# In ui.py
PARTY_COLOR = (0, 128, 255)  # Light blue instead of dark blue
ENEMY_COLOR = (255, 64, 0)   # Orange instead of dark red
```

**Adjust Panel Sizes:**
```python
# In BattleUI.__init__()
self.command_menu = Menu(
    pygame.Rect(20, 450, 400, 230),  # Wider command menu
    "Commands"
)
```

**Add Custom Log Messages:**
```python
# In your action execute method
if hasattr(battle, 'battle_ui') and battle.battle_ui:
    battle.battle_ui.add_log_message(f"{actor.name} casts {self.name}!")
```

## Performance Considerations

- **Drawing Optimization**: All static elements cached where possible
- **Frame Rate**: Locked to 60 FPS for smooth animation
- **Input Debouncing**: Built-in pygame event handling prevents input spam
- **Memory Usage**: Minimal - no large textures or sprites loaded

## Future Enhancements

1. **Mouse Support**: Click to select from menus
2. **Animations**: Character sprites, action effects
3. **Sound Effects**: Audio feedback for actions
4. **Tooltips**: Detailed info on hover
5. **Battle Speed Control**: Fast-forward option
6. **History Replay**: Review past actions
7. **Save Battle State**: Pause and resume
8. **Multiplayer UI**: Split-screen or network play

## Debugging Tips

1. **Print Current State**:
   ```python
   print(f"UI State: in_submenu={ui_state.in_submenu}, targeting={ui_state.targeting}")
   ```

2. **Check Menu Items**:
   ```python
   for i, item in enumerate(menu.items):
       print(f"{i}: {item.text} (enabled={item.enabled})")
   ```

3. **Monitor Battle State**:
   ```python
   print(f"Battle State: {battle.state.__class__.__name__}")
   if isinstance(battle.state, SelectingCommands):
       print(f"Action selected: {battle.state.action_selected}")
   ```

4. **Track Input Events**:
   ```python
   print(f"Key pressed: {pygame.key.name(event.key)}")
   ```

## Common Issues and Solutions

**Issue**: Menus not updating
- **Solution**: Ensure `setup_*_menu()` is called when state changes

**Issue**: Action executes twice
- **Solution**: Check that `action_selected` flag is reset properly

**Issue**: Can't select disabled items
- **Solution**: Verify MP costs and item availability checks

**Issue**: Target menu shows dead characters
- **Solution**: Filter graveyard: `if character not in battle.graveyard`

**Issue**: UI elements overlap
- **Solution**: Check Rect coordinates in `BattleUI.__init__()`
