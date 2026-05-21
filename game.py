import random
import os

# --- Global log buffer ---
log_buffer = []
MAX_LOG_LINES = 10  # Number of log lines to display


def add_log(message, color="yellow"):
    """Add a colored log message to the buffer"""
    color_codes = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    colored_message = f"{color_codes.get(color, '')}{message}{color_codes['reset']}"
    log_buffer.append(colored_message)


# --- Classes ---
class Food:
    def __init__(self, value, position):
        self.value = value
        self.position = position

    def __str__(self):
        return f"Food(value={self.value}, position={self.position})"


class Animal:
    def __init__(self, name, symbol=None):
        self.name = name
        self.under_attack = False
        self.health = 100
        self.defence = 100
        self.position = (random.randint(0, 14), random.randint(0, 14))
        self.symbol = symbol  # Player custom symbol or None

    def move(self, direction):
        x, y = self.position
        if direction == "up" and y < 14:
            self.position = (x, y + 1)
        elif direction == "down" and y > 0:
            self.position = (x, y - 1)
        elif direction == "left" and x > 0:
            self.position = (x - 1, y)
        elif direction == "right" and x < 14:
            self.position = (x + 1, y)
        add_log(f"{self.name} moved {direction} to {self.position}", "info")

    def radius(self):
        x, y = self.position
        return [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]

    def is_in_radius(self, target):
        return target.position in self.radius()

    def attack(self, target, damage):
        if isinstance(target, Animal):
            target.under_attack = True
            if self.is_in_radius(target):
                target.health -= damage
                color = "red" if target.symbol else "yellow"
                add_log(f"{self.name} attacks {target.name} for {damage:.1f} damage!", color)
                if target.symbol:
                    add_log(f"YOU HAVE BEEN ATTACKED! Lost {damage:.1f} health.", "red")
            else:
                add_log(f"{self.name} tried to attack {target.name}, but target is out of range", "yellow")

    def defend(self):
        if self.under_attack:
            loss = self.defence / 4
            self.health -= loss
            self.defence -= loss
            self.under_attack = False
            if self.symbol:
                add_log(f"YOU DEFENDED! Lost {loss:.1f} health/defence. Health: {self.health:.1f}, Defence: {self.defence:.1f}", "blue")
            else:
                add_log(f"{self.name} defends and loses {loss:.1f} health/defence.", "yellow")

    def consume_food(self, foods):
        for food in foods[:]:
            if food.position in self.radius():
                self.health += food.value
                foods.remove(food)
                if self.symbol:
                    add_log(f"YOU CONSUMED {food}! Gained {food.value} health. Total health: {self.health:.1f}", "green")
                else:
                    add_log(f"{self.name} consumed {food}.", "yellow")

    def distance_to(self, target):
        """Calculate Manhattan distance to a target"""
        x1, y1 = self.position
        x2, y2 = target.position
        return abs(x1 - x2) + abs(y1 - y2)
    
    def move_towards(self, target):
        """Move one step towards the target"""
        x1, y1 = self.position
        x2, y2 = target.position
        
        # Decide which direction brings us closer
        dx = x2 - x1
        dy = y2 - y1
        
        # Prioritize the larger distance (more aggressive pursuit)
        if abs(dx) > abs(dy):
            if dx > 0 and x1 < 14:
                self.move("right")
            elif dx < 0 and x1 > 0:
                self.move("left")
            elif dy > 0 and y1 < 14:
                self.move("up")
            elif dy < 0 and y1 > 0:
                self.move("down")
        else:
            if dy > 0 and y1 < 14:
                self.move("up")
            elif dy < 0 and y1 > 0:
                self.move("down")
            elif dx > 0 and x1 < 14:
                self.move("right")
            elif dx < 0 and x1 > 0:
                self.move("left")

    def __str__(self):
        return f"{self.name}(H:{self.health:.1f}, D:{self.defence:.1f}, Pos:{self.position})"


# --- Helper functions ---
def draw_board(animals, foods, player_goat, size=15):
    board = [["." for _ in range(size)] for _ in range(size)]

    # Place food first
    for food in foods:
        x, y = food.position
        if 0 <= x < size and 0 <= y < size:
            board[y][x] = "F"

    # Place animals (overwrite if same position)
    for animal in animals:
        x, y = animal.position
        if 0 <= x < size and 0 <= y < size:
            mark = animal.symbol or ("P" if "Predator" in animal.name else "G")
            # Only show the animal symbol, not concatenation
            board[y][x] = mark

    os.system("cls" if os.name == "nt" else "clear")

    # Display last logs
    print("---- Game Log ----")
    for line in log_buffer[-MAX_LOG_LINES:]:
        print(line)
    print("------------------\n")

    # Display player stats
    print(f"Player Stats: Name: {player_goat.name} | Health: {player_goat.health:.1f} | "
          f"Defence: {player_goat.defence:.1f} | Position: {player_goat.position}\n")

    # Print board
    for row in reversed(board):
        print(" ".join(row))
    print("\n")


def get_player_move():
    move = input("Move your goat (w/a/s/d): ").strip().lower()
    mapping = {"w": "up", "s": "down", "a": "left", "d": "right"}
    return mapping.get(move, None)


def choose_player_symbol():
    while True:
        symbol = input("Choose a symbol for your goat (avoid G, P, F): ").strip()
        if symbol and symbol.upper() not in {"G", "P", "F"} and len(symbol) == 1:
            return symbol
        print("Invalid symbol. Please choose a single character not G, P, or F.")


# --- Game setup ---
foods = [Food(random.randint(5, 30), (random.randint(0, 14), random.randint(0, 14))) for _ in range(8)]
initial_food_count = len(foods)
predators = [Animal(f"Predator{i+1}") for i in range(4)]
player_symbol = choose_player_symbol()
player_goat = Animal("PlayerGoat", symbol=player_symbol)
other_goats = [Animal(f"Goat{i+1}") for i in range(2)]
all_animals = predators + [player_goat] + other_goats

player_food_consumed = 0

# --- Game loop ---
turn = 0
game_over = False

while not game_over:
    turn += 1
    print(f"--- Turn {turn} ---")

    # Draw board and logs
    draw_board(all_animals, foods, player_goat)

    # Player move
    move = None
    while move is None:
        move = get_player_move()
    player_goat.move(move)
    
    # Track player food consumption
    foods_before = len(foods)
    player_goat.consume_food(foods)
    foods_after = len(foods)
    player_food_consumed += (foods_before - foods_after)
    
    if player_goat.health <= 0:
        add_log("You have been defeated! Game over.", "red")
        game_over = True
        break

    # Other goats move randomly
    for goat in other_goats[:]:
        if goat.health > 0:
            move = random.choice(["up", "down", "left", "right"])
            goat.move(move)
            goat.consume_food(foods)
        if goat.health <= 0:
            add_log(f"{goat.name} has been defeated!", "red")
            all_animals.remove(goat)
            other_goats.remove(goat)

    # Predators move with hunting AI
    DETECTION_RADIUS = 5  # How far predators can "see"
    
    for predator in predators:
        # Find nearest goat within detection radius
        targets = [player_goat] + other_goats
        nearest_goat = None
        nearest_distance = float('inf')
        
        for goat in targets:
            if goat.health > 0:
                dist = predator.distance_to(goat)
                if dist <= DETECTION_RADIUS and dist < nearest_distance:
                    nearest_distance = dist
                    nearest_goat = goat
        
        # Chase if goat detected, otherwise move randomly
        if nearest_goat:
            add_log(f"{predator.name} spotted {nearest_goat.name} and is hunting!", "red")
            predator.move_towards(nearest_goat)
        else:
            move = random.choice(["up", "down", "left", "right"])
            predator.move(move)
        
        # Attack all goats in radius
        for goat in targets[:]:
            if goat.health > 0 and predator.is_in_radius(goat):
                add_log(f"DEBUG: {predator.name} at {predator.position} found {goat.name} at {goat.position} in radius!", "blue")
                damage = random.randint(5, 20)
                predator.attack(goat, damage)
                goat.defend()
                
                if goat.health <= 0:
                    add_log(f"{goat.name} has been defeated!", "red")
                    if goat == player_goat:
                        game_over = True
                        break
                    else:
                        all_animals.remove(goat)
                        if goat in other_goats:
                            other_goats.remove(goat)
        
        if game_over:
            break

    # Check win condition - player consumed all food
    if player_food_consumed >= initial_food_count:
        add_log("Congratulations! You consumed all the food. You win!", "green")
        game_over = True
        break
    
    # Check lose condition
    if player_goat.health <= 0:
        add_log("You have been killed by predators. Game over.", "red")
        game_over = True
        break

# Final board display
draw_board(all_animals, foods, player_goat)
print(f"\nGame ended after {turn} turns.")
print(f"You consumed {player_food_consumed}/{initial_food_count} food items.")