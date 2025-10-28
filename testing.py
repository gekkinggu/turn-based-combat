from action_core import Action

attack = Action("Attack")

for key, value in vars(attack).items():
    print(f"{key}: {value}")
