import os
import random
import time
import json

import keyboard

from types import SimpleNamespace


def cls():
    os.system('cls')


def main():
    game = GameInstance()


class Config:
    game_speed: int
    game_size: int
    score: int

    def __init__(self, game_size=20, game_speed=10,  score=0):
        self.game_size = game_size
        self.game_speed = game_speed
        self.score = score


class Vector2:
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector2(self.x * other.x, self.y * other.y)

    def __copy__(self):
        return Vector2(self.x, self.y)

    def __str__(self):
        return f"Vector2(x: {self.x}, y: {self.y})"

    @staticmethod
    def compare(vec1, vec2):
        if vec1.x == vec2.x and vec1.y == vec2.y:
            return True
        return False

    @staticmethod
    def compare_to_list(vec, vec_list: list):
        for member in vec_list:
            if Vector2.compare(member, vec):
                return True
        return False


class Fruit:
    fruit_position: Vector2

    def __init__(self, size: int, avoid_pos: list):
        legal_list = []
        for i in (n + 1 for n in range(size - 2)):
            for j in (n + 1 for n in range(size - 2)):
                test_vec = Vector2(i, j)
                if Vector2.compare_to_list(test_vec, avoid_pos) is False:
                    legal_list.append(test_vec)
        self.fruit_position = legal_list[random.randint(0, len(legal_list) - 1)]

    def self_check(self, position: Vector2):
        return Vector2.compare(self.fruit_position, position)


class Snake:
    head_position: Vector2

    tail = []

    def __init__(self):
        self.head_position = Vector2()
        self.tail = []

    def update_tail(self):
        old_pos = self.head_position.__copy__()
        for index in range(len(self.tail)):
            op = self.tail[index].__copy__()
            self.tail[index] = old_pos.__copy__()
            old_pos = op.__copy__()

    def move(self, pos: Vector2):
        self.update_tail()
        self.head_position = pos.__copy__()

    def eat(self):
        self.tail.append(self.head_position.__copy__())

    def check_self_collision(self, new_pos: Vector2):
        return Vector2.compare_to_list(new_pos, self.snake_body())

    def snake_body(self):
        body = self.tail.copy()
        body.append(self.head_position)
        return body


class HandleJson:

    @staticmethod
    def to_json(obj, file_name: str):
        json_string = json.dumps(obj, default=vars, sort_keys=True, indent=4)
        json_bytes = str.encode(json_string)
        with open(file_name, "wb") as file:
            file.write(json_bytes)

    @staticmethod
    def from_json(file_name: str):
        try:
            with open(file_name, "rb") as file:
                json_bytes = file.read()
                json_string = bytes(json_bytes).decode()
                result = json.loads(json_string, object_hook=lambda d: SimpleNamespace(**d))
                return result
        except FileNotFoundError:
            config = Config()
            HandleJson.to_json(config, "config.b")
            return config
        except IOError:
            config = Config()
            HandleJson.to_json(config, "config.b")
            return config
        except ValueError:
            config = Config()
            HandleJson.to_json(config, "config.b")
            return config


class GameInstance:
    game_opened: bool
    fruit: Fruit
    snake: Snake
    current_input = 'up'
    config: Config
    score = 0

    def __init__(self):
        print('Loading config...')
        time.sleep(0.3)
        self.config = self.get_config()
        print('Starting game...')
        time.sleep(0.3)
        self.start_game()

    def get_config(self):
        con = HandleJson.from_json("config.b")
        return con

    def save_config(self):
        HandleJson.to_json(self.config, "config.b")

    def get_input(self):
        if keyboard.is_pressed('up') and self.current_input != 'down':
            return 'up'
        if keyboard.is_pressed('down') and self.current_input != 'up':
            return 'down'
        if keyboard.is_pressed('right') and self.current_input != 'left':
            return 'right'
        if keyboard.is_pressed('left') and self.current_input != 'right':
            return 'left'

        return self.current_input

    def input_to_vector2(self, key: str):
        pos = Vector2()
        match key:
            case 'up':
                pos.x -= 1
                return pos
            case 'down':
                pos.x += 1
                return pos
            case 'left':
                pos.y -= 1
                return pos
            case 'right':
                pos.y += 1
                return pos
        return pos

    def manage_input(self):
        new_pos = self.snake.head_position.__copy__()
        new_pos += self.input_to_vector2(self.current_input)

        if self.snake.check_self_collision(new_pos):
            self.end_game()
            return new_pos

        if self.fruit.self_check(new_pos):
            self.snake.eat()
            self.fruit = Fruit(self.config.game_size, self.snake.snake_body())
            self.score += 1

        if new_pos.x >= self.config.game_size - 1:
            new_pos.x = 0
        elif new_pos.x <= 0:
            new_pos.x = self.config.game_size - 2

        if new_pos.y >= self.config.game_size - 1:
            new_pos.y = 0
        elif new_pos.y <= 0:
            new_pos.y = self.config.game_size - 2

        self.snake.move(new_pos)

    def draw_logo(self):
        title = '< S N A K E >'
        title = title.center(self.config.game_size * 2, '=')
        print(title)

    def draw_score(self):
        highscore = '< H I G H S C O R E : ' + str(self.config.score) + ' >'
        score = '< S C O R E : ' + str(self.score) + ' >'
        score = score.center(self.config.game_size * 2, '=')
        highscore = highscore.center(self.config.game_size * 2, '=')
        print(highscore + '\n' + score + '\n')

    def draw_window(self):
        self.draw_logo()
        for i in range(self.config.game_size):
            for j in range(self.config.game_size):
                if i == 0 or i == self.config.game_size - 1 or j == 0 or j == self.config.game_size - 1:
                    print('#',  end=' ')
                    continue

                current_pos = Vector2(i,  j)
                if Vector2.compare_to_list(current_pos, self.snake.tail):
                    print('\157', end=' ')
                    continue
                if Vector2.compare(current_pos, self.snake.head_position):
                    print('o', end=' ')
                    continue
                if Vector2.compare(current_pos, self.fruit.fruit_position):
                    print('x', end=' ')
                    continue
                print(' ', end=' ')
            print()
        self.draw_score()

    def start_game(self):
        self.game_opened = True
        self.snake = Snake()
        self.fruit = Fruit(self.config.game_size, self.snake.snake_body())
        while self.game_opened:
            self.loop()

    def loop(self):
        self.manage_input()
        self.draw_window()
        checked_input = list()
        for i in range(self.config.game_speed):
            checked_input.append(self.get_input())
            time.sleep(0.005)
        checked_input.reverse()
        for member in checked_input:
            if member != self.current_input:
                self.current_input = member
                break
        checked_input.clear()
        cls()

    def end_game(self):
        if self.config.score < self.score:
            self.config.score = self.score
        self.save_config()
        self.game_opened = False


if __name__ == '__main__':
    main()
