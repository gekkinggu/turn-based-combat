# python
"""test_ui.py

Test script to verify the UI system integration.
"""

import pygame
from game import Game
from character import Character, Enemy

def test_ui_initialization():
    """Test that the UI initializes correctly."""
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    game = Game(screen)
    
    warrior = Character("Warrior", 50)
    mage = Character("Mage", 50)
    enemy1 = Enemy("Goblin", 40)
    enemy2 = Enemy("Orc", 45)
    
    try:
        game.start_battle(party=[warrior, mage], enemies=[enemy1, enemy2])
        print("UI initialization successful")
        print(f"Battle state: {game.battle.state}")
        print(f"Battle UI created: {game.battle_ui is not None}")
        print(f"Party size: {len(game.battle.party)}")
        print(f"Enemy count: {len(game.battle.enemies)}")
        return True
    except Exception as e:
        print(f"UI initialization failed: {e}")
        return False
    finally:
        pygame.quit()

def test_menu_creation():
    """Test that menus are created correctly."""
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    game = Game(screen)
    
    warrior = Character("Warrior", 50)
    enemy = Enemy("Goblin", 40)
    
    try:
        game.start_battle(party=[warrior], enemies=[enemy])
        game.battle_ui.setup_command_menu(warrior)
        
        print("Command menu created")
        print(f"Command count: {len(game.battle_ui.command_menu.items)}")
        
        for item in game.battle_ui.command_menu.items:
            print(f"  - {item.text} (enabled: {item.enabled})")
        
        return True
    except Exception as e:
        print(f"Menu creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

def test_battle_flow():
    """Test a few steps of battle flow."""
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    game = Game(screen)
    
    warrior = Character("Warrior", 50)
    enemy = Enemy("Goblin", 40)
    
    try:
        game.start_battle(party=[warrior], enemies=[enemy])
        
        print("Battle started")
        print(f"  Initial state: {game.battle.state}")
        
        # Simulate a few frames
        for i in range(10):
            game.update_battle(0.016)
            
        print(f"  State after 10 frames: {game.battle.state}")
        print(f"  Warrior ATB: {warrior.atb:.1f}/{game.battle.READY_THRESHOLD}")
        print(f"  Enemy ATB: {enemy.atb:.1f}/{game.battle.READY_THRESHOLD}")
        
        return True
    except Exception as e:
        print(f"Battle flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Turn-Based Combat UI System")
    print("=" * 50)
    print()
    
    tests = [
        ("UI Initialization", test_ui_initialization),
        ("Menu Creation", test_menu_creation),
        ("Battle Flow", test_battle_flow),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning test: {test_name}")
        print("-" * 50)
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! The UI system is ready.")
    else:
        print("\nSome tests failed. Please check the errors above.")
