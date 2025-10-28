from pathlib import Path
import random

from character_core import Character, Enemy
from battle import Battle, Waiting

def main():
    # Use fixtures without touching UI
    fixtures = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
    os_cwd = Path.cwd()
    try:
        # Read CSVs from fixtures
        import os
        os.chdir(fixtures)

        random.seed(42)

        hero = Character("Hero", level=10)
        slime = Enemy("Slime", level=10)
        b = Battle([hero], [slime])
        b.preparation()
        b.state = Waiting()

        steps = 0
        print("Start:", {"Hero": hero.hp, "Slime": slime.hp})
        while b.outcome is None and steps < 50:
            b.loop(0.5)
            steps += 1
            if steps % 2 == 0:
                print(f"t={steps/2:.1f}s state={b.state} ATB(H,S)=({hero.atb:.1f},{slime.atb:.1f}) HP(H,S)=({hero.hp},{slime.hp})")
        print("Outcome:", b.outcome or "None")
    finally:
        os.chdir(os_cwd)

if __name__ == "__main__":
    main()