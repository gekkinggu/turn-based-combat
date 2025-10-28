# Quick Start Guide - Turn-Based Combat UI System

## Installation

1. **Install pygame**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

### Basic Battle Simulation

```bash
python game.py
```

This starts a default battle with:
- **Party**: Warrior (Lv. 50), Mage (Lv. 50)
- **Enemies**: Goblin (Lv. 40), Orc (Lv. 45)

### Testing the System

```bash
python test_ui.py
```

This runs automated tests to verify the UI system is working correctly.

## Playing the Game

### Understanding the Interface

**Top Section**: Character status panels showing HP, MP, ATB, and status effects
- Left side: Your party members (blue)
- Right side: Enemy characters (red)

**Middle Section**: Battle log showing recent actions

**Bottom Section**: Interactive menus
- Left panel: Command selection (Attack, Abilities, Magic, Items)
- Middle panel: Action selection (specific moves)
- Right panel: Target selection (who to target)

### Controls

| Key | Action |
|-----|--------|
| ↑ or W | Move selection up |
| ↓ or S | Move selection down |
| Enter or Space | Confirm selection |
| Escape or Backspace | Cancel/Go back |

### How to Take a Turn

1. **Wait for your turn**: Watch the ATB gauge fill (turns yellow when ready)
2. **Select a Command**: Choose from Attack, Abilities, Magic, or Items
3. **Select an Action**: Pick a specific move (e.g., Fire spell, Heal spell)
4. **Select Target(s)**: Choose who to use the action on
5. **Action executes**: Watch the results in the battle log

### Tips

- **HP Bar Colors**: 
  - Green = Good health (>50%)
  - Yellow = Moderate damage (25-50%)
  - Red = Critical (<25%)
  
- **ATB Gauge**:
  - Blue = Filling
  - Yellow = Ready to act
  
- **Disabled Options**: Grayed-out actions can't be used (not enough MP, no items, etc.)

- **Multi-Target Actions**: Some actions (like "Fire All") automatically target all enemies

## Customization

### Create Custom Battles

Edit `game.py` and modify the main() function:

```python
# Create custom characters
hero = Character("Hero", 60)
wizard = Character("Wizard", 55)

# Create custom enemies  
dragon = Enemy("Dragon", 70)
slime = Enemy("Slime", 30)

# Start battle
game.start_battle(party=[hero, wizard], enemies=[dragon, slime])
```

### Adjust Character Stats

Edit `definitions/battlers.csv` to modify:
- Base stats (HP, MP, Strength, Defense, Magic, Speed)
- Available abilities and spells
- Elemental affinities

### Create New Actions

Edit `definitions/actions.csv` to add new attacks, spells, or abilities.

### Add Status Effects

Edit `definitions/statuses.csv` to create buffs, debuffs, and special effects.

## Troubleshooting

### "Module not found" errors
```bash
pip install pygame
```

### Game window doesn't appear
- Make sure pygame is installed correctly
- Check that no other application is blocking the window

### Menus not responding
- Make sure you're clicking inside the menu panels
- Use keyboard controls (Arrow keys or WASD + Enter)

### Battle never starts
- Check that CSV files exist in the `definitions/` folder
- Verify character names match entries in `battlers.csv`

## Next Steps

1. **Experiment with the battle system**: Try different character combinations
2. **Create custom characters**: Add new entries to `battlers.csv`
3. **Design new abilities**: Modify `actions.csv` with unique moves
4. **Implement custom AI**: Edit `behaviour.py` for smarter enemies
5. **Extend the UI**: Modify `ui.py` to add new visual elements

## Getting Help

- Read `README.md` for detailed documentation
- Check the code comments in each module
- Run `test_ui.py` to verify your setup

## Example Battle Flow

```
1. Battle starts → ATB gauges begin filling
2. First character reaches full ATB → SelectingCommands state
3. Player selects "Magic" command
4. Player chooses "Fire" spell
5. Player targets an enemy
6. Fire spell executes, dealing damage
7. Turn ends, ATB resets
8. Next character becomes ready...
9. Battle continues until Victory or Defeat
```

Enjoy your turn-based combat system! 🎮⚔️
