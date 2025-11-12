import random
import json, urllib.request, urllib.parse

# --- run history storage ---
runs_log = []

def print_records():
    if not runs_log:
        print("No past attempts yet.")
        return
    print("\n=== Past Attempts ===")
    for i, r in enumerate(runs_log, 1):
        print(f"{i}. name={r.get('name')!s} | direction={r.get('direction')!s} | route={r.get('route')!s} | loot={r.get('loot')!s} | result={r.get('result')!s}")
    print("=====================\n")

def _get_json(url, params=None, timeout=5):
    try:
        if params:
            url = url + "?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None

def weather_gate_text():
    data = _get_json(
        "https://api.open-meteo.com/v1/forecast",
        {"latitude": 40.7128, "longitude": -74.0060, "current_weather": True},
    )
    if not data or "current_weather" not in data:
        return "The air is still. Water murmurs under the bridge."
    cw = data["current_weather"]
    wind = cw.get("windspeed", 0)
    code = cw.get("weathercode", 0)
    if wind >= 30:
        return "A violent storm lashes the bridge. Crossing looks risky."
    if code in {61, 63, 65}:
        return "Rain drums on the planks. A dark cave mouth glistens nearby."
    if code in {45, 48}:
        return "Fog blankets the river. Shapes move in silence."
    return "Clear skies reveal a distant tower. The bridge looks safe."

def random_monster_name():
    data = _get_json("https://creaturator.deno.dev/api/v1/1")
    # expected format: [{"name": "...", "description": "..."}]
    try:
        return data[0]["name"].strip() or "nameless horror"
    except Exception:
        return "nameless horror"

# --- main replay loop ---
while True:
    inventory = []

    name = input("Hey type your name: ")
    print(f"\nHello {name}, welcome to my game!\n")

    # start a new run record
    run = {"name": name, "direction": None, "route": None, "loot": None, "result": None}

    Should_we_play = input("Do you want to play? (yes/no or type 'records') ").lower()
    if Should_we_play == "records":
        print()
        print_records()
        continue
    play = Should_we_play == "yes"

    if Should_we_play == "y" or Should_we_play == "yes":
        print("\nWe are going to play!\n")
        direction = input("Do you want to go left or right? (left/right) ").lower()
        run["direction"] = direction
        
        if direction == "left":
            print("\nYou chose the path of death. A pit opens under your feet. Try Again :(\n")
            run["result"] = "pit death"

        elif direction == "right":
            print("\n" + weather_gate_text() + "\n")
            choice = input("You see a bridge in the distance. Would you like to swim under it or cross the bridge? (swim under/cross it) ").lower()
            if choice in ("swim under", "cross it"):
                run["route"] = choice
            
            if choice == "swim under":
                print("\nYou swim under the bridge and discover a waterfall with a cave behind it.\n")
                choice = input("Would you like to enter the waterfall? (yes/no) ").lower()
                
                if choice == "yes":
                    print("\nYou come across a mysterious chest.\n")
                    choice = input("Would you like to open the chest? (open it/don't open it) ").lower()
                    
                    if choice == "open it":
                        # 50/50 loot logic
                        loot = random.choice(["sword", "dragon scaled armor"])
                        inventory.append(loot)
                        run["loot"] = loot
                        print()
                        if loot == "sword":
                            print("You open the chest and find a gleaming Sword. It hums with ancient power.")
                            print("Item effect: Sword = heavier hits. Rolls ≥ 4 deal 2 damage instead of 1.")
                        else:
                            print("You open the chest and find Dragon Scaled Armor. It’s nearly indestructible.")
                            print("Item effect: Armor = more resilience. You start the boss fight with 4 HP instead of 3.")
                        print("\nFrom deeper in the cave you hear growling...\n")

                        choice = input("Would you like to investigate the growling? (investigate/don't investigate) ").lower()               
                        if choice == "investigate":
                            boss_name = random_monster_name()
                            print("\nYou have entered into a boss fight.")
                            print(f"A {boss_name} emerges from the shadows.")
                            
                            def roll_dice(sides=6):
                                return random.randint(1, sides)
                            
                            player_hp = 3
                            boss_hp = 3

                            if "dragon scaled armor" in inventory:
                                player_hp = 4
                                print("Your armor absorbs more hits. You have extra defense!")
                            elif "sword" in inventory:
                                print("Your sword cuts deeper. High rolls do extra damage!")

                            # show starting HP before any action
                            print(f"\nStarting HP — You: {player_hp} | {boss_name}: {boss_hp}\n")

                            while True:
                                input("Press ENTER to attack...")  # prompt line
                                roll = roll_dice()
                                print(f"You rolled a {roll}")
                                if "sword" in inventory and roll >= 4:
                                    boss_hp -= 2
                                    print(f"You slash fiercely! Boss HP: {boss_hp}")
                                elif roll >= 5:
                                    boss_hp -= 1
                                    print(f"You hit the {boss_name}! Boss HP: {boss_hp}")
                                else:
                                    print("Your attack missed!")

                                if boss_hp <= 0:
                                    print(f"\nYou defeated the {boss_name}! You win the game!")
                                    print("Congratulations, hero!\n")
                                    run["result"] = f"victory vs {boss_name}"
                                    break

                                input("Press ENTER to defend...")  # prompt line
                                roll = roll_dice()
                                print(f"{boss_name} rolled a {roll}")
                                if roll >= 5:
                                    player_hp -= 1
                                    print(f"The {boss_name} hits you! Your HP: {player_hp}")
                                else:
                                    print(f"The {boss_name} missed!")

                                if player_hp <= 0:
                                    print("\nYou were defeated. Game Over.\n")
                                    run["result"] = f"defeat vs {boss_name}"
                                    break

                        else:
                            print("\nYou wisely leave the cave. You survive, but never know what lurked inside...")
                            print("You live peacefully, though always wondering what could have been.\n")
                            run["result"] = "left cave survived"
                    
                    else:
                        print("\nYou walk away from the chest. Moments later, the cave collapses. You barely escape alive!")
                        print("At least you survived, but you’ll never know what was inside...\n")
                        run["result"] = "cave collapsed survived"
                
                else:
                    print("\nYou ignore the waterfall and keep swimming. Eventually, you tire out and drown. Game Over.\n")
                    run["result"] = "drowned"
            
            elif choice == "cross it":
                print("\nYou carefully cross the old wooden bridge and make it safely to the other side.")
                print("Ahead, you find a small island with smoke rising in the distance.\n")
                
                choice = input("Do you want to head toward the smoke? (yes/no) ").lower()
                
                if choice == "yes":
                    print("\nYou discover a friendly tribe. They welcome you, give you food, and offer you shelter.")
                    print("You live among them happily. You win by finding a new home!\n")
                    run["result"] = "tribe win"
                else:
                    print("\nYou wander the island alone. Without help, you eventually starve. Game Over.\n")
                    run["result"] = "starved"
        
        else:
            print("\nA secret pathway has been triggered!")
            print("You find a hidden tunnel filled with glowing crystals.")
            print("At the end, you discover a treasure hoard untouched for centuries. You live rich forever!")
            print("Secret ending unlocked. Well done!\n")
            run["result"] = "secret rich win"

    else:
        print("\nWe are not going to play.\n")
        run["result"] = "declined"

    # store the run record
    if run.get("result") is None:
        run["result"] = "ended"
    runs_log.append(run)

    # replay or records
    again = input("Play again? (yes/no or type 'records') ").lower()
    if again == "records":
        print()
        print_records()
        again = input("Play again? (yes/no) ").lower()

    if again not in ("yes", "y"):
        print("\nGoodbye.")
        break