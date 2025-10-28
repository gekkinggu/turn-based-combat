from pathlib import Path
import types
import pytest

from character_core import Character, Enemy
from action_core import Action
from battle import Battle, Waiting, SpeedTie, PrepareActor, ControlledTurn, AITurn, CheckingDeath

FIXTURES = Path(__file__).parent / "fixtures"

@pytest.fixture(autouse=True)
def cwd_to_fixtures(monkeypatch):
    monkeypatch.chdir(FIXTURES)

def fixed_randint(a, b):
    # 100% variance and no crit (100 > 15)
    if (a, b) == (85, 115):
        return 100
    return 100

def test_attack_reduces_hp(monkeypatch):
    # Make damage deterministic
    monkeypatch.setattr("action_core.random.randint", fixed_randint)

    hero = Character("Hero", level=10)
    slime = Enemy("Slime", level=10)
    battle = Battle([hero], [slime])
    battle.preparation()

    atk = Action("Attack")
    # Compute expected using the same formula the action uses
    expected = atk.damageFormula(hero.strength, slime.defense)
    start_hp = slime.hp

    atk.execute(hero, [slime], battle)

    assert slime.hp == start_hp - expected
    assert slime.hp >= 0

def test_waiting_to_prepare_actor(monkeypatch):
    # Deterministic prep: start all at ATB 0 and choose first on tie
    monkeypatch.setattr("battle.random.randint", lambda a, b: 0)
    monkeypatch.setattr("battle.random.choice", lambda seq: seq[0])

    hero = Character("Hero", level=10)
    slime = Enemy("Slime", level=10)
    battle = Battle([hero], [slime])
    battle.preparation()

    battle.state = Waiting()
    battle.loop(10.0)  # large dt to push both over READY_THRESHOLD

    assert isinstance(battle.state, SpeedTie)
    # Resolve tie
    battle.loop(0.0)
    assert isinstance(battle.state, PrepareActor)
    # Next step becomes player or AI turn depending on winner
    battle.loop(0.0)
    assert isinstance(battle.state, (ControlledTurn, AITurn))

def test_ai_turn_attacks(monkeypatch):
    # Deterministic choice and damage rolls
    monkeypatch.setattr("action_core.random.randint", fixed_randint)
    monkeypatch.setattr("behaviour_core.random.choice", lambda seq: seq[0])

    hero = Character("Hero", level=10)
    slime = Enemy("Slime", level=10)
    battle = Battle([hero], [slime])
    battle.preparation()

    start_hp = hero.hp
    battle.state = AITurn(slime)
    battle.loop(0.0)  # AI acts
    assert isinstance(battle.state, CheckingDeath)
    assert hero.hp < start_hp