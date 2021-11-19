#!/usr/bin/python3

import os
import time
import random
from pynput.keyboard import Key, Listener


class ObjectOnField(object):
    """Базовый класс объектов на игровом поле"""
    def __init__(self, pos_x, pos_y, char=' '):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.char = char

    def get_position(self):
        """Возвращает кортеж координат объекта"""
        return self.pos_x, self.pos_y

    def set_position(self, pos_x, pos_y):
        """Устанавливает координаты объекта"""
        self.pos_x = pos_x
        self.pos_y = pos_y

    def get_char(self):
        """Возвращает символ, обозначающий объект на игровом поле"""
        return self.char


class Food(ObjectOnField):
    """Класс еды для змейки"""

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 'O')

    def generate_new_food(self, game=None):
        """Генерация новых координатов еды на поле"""
        if game:
            self.pos_x = random.randint(0, game.field.get_height() - 1)
            self.pos_y = random.randint(0, game.field.get_width() - 1)

            # Координаты новой еды не должны совпадать с координатами
            # тела и головы змейки
            while (self.pos_x, self.pos_y) == game.head.get_position() or\
                    (self.pos_x, self.pos_y) in game.body.get_positions():
                self.pos_x = random.randint(0, game.field.get_height() - 1)
                self.pos_y = random.randint(0, game.field.get_width() - 1)


class Field(object):
    """Класс игрового поля"""
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.points = [[' '] * self.width for _ in range(self.height)]

    def show_field(self):
        """Вывод поля на экран"""
        print()
        print(f'{" " * 10}{"*" * (self.get_width() + 2)}')
        for row in self.points:
            print(f'{" " * 10}|{"".join(row)}|')
        print(f'{" " * 10}{"*" * (self.get_width() + 2)}')

    def update_points(self, head, body, food):
        """Обновление координат еды, головы и тела змеи на игровом поле"""
        self.points = [[' '] * self.width for _ in range(self.height)]
        x, y = head.get_position()
        self.points[x][y] = head.get_char()
        x, y = food.get_position()
        self.points[x][y] = food.get_char()
        for part in body.get_elements():
            x, y = part.get_position()
            self.points[x][y] = part.get_char()

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width


class SnakesHead(ObjectOnField):
    """Класс головы змеи"""
    def __init__(self, pos_x=15, pos_y=15):
        # Направление [0, 1] означает, что за один ход, координаты головы
        # змейки [x, y], изменятся на [+0, +1], соответственно
        self.direction = [0, 1]
        super().__init__(pos_x, pos_y, 'X')

    def get_next_position(self):
        """
        Возвращает следующее положение головы в зависимости от наравления
        движения змеи
        """
        return self.pos_x + self.direction[0], self.pos_y + self.direction[1]

    def change_direction(self, direction):
        """Изменение направления движения головы змеи"""
        if direction == 'up'and self.direction != [1, 0]:
            self.direction = [-1, 0]
        elif direction == 'down'and self.direction != [-1, 0]:
            self.direction = [1, 0]
        elif direction == 'left'and self.direction != [0, 1]:
            self.direction = [0, -1]
        elif direction == 'right'and self.direction != [0, -1]:
            self.direction = [0, 1]


class ElementOfSnakesBody(ObjectOnField):
    """Класс элемента тела змейки"""
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 'x')


class SnakesBody(object):
    """Класс тела змейки"""
    def __init__(self, pos_x_of_head=15, pos_y_of_head=15):
        self.body_elements = []
        for i in range(1, 4):
            self.body_elements.append(ElementOfSnakesBody(pos_x_of_head,
                                                          pos_y_of_head - i))

    def get_positions(self):
        """Возвращает множество координат элементов тела змейки"""
        return {part.get_position() for part in self.body_elements}

    def make_step(self, pos_x, pos_y, add_element=False):
        """Изменение координат элементов тела змейки в процессе шага змейки"""
        
        # Если голова съела еду
        if add_element:
            new_element =\
                ElementOfSnakesBody(*self.body_elements[-1].get_position())

        for i in range(len(self.body_elements) - 1, 0, -1):
            x, y = self.body_elements[i - 1].get_position()
            self.body_elements[i].set_position(x, y)
        self.body_elements[0].set_position(pos_x, pos_y)

        # Если голова съела еду
        if add_element:
            self.body_elements.append(new_element)

    def get_elements(self):
        """Возвращает список с экземплярами элементов тела змейки"""
        return self.body_elements


class GamePlay(object):
    """Класс игрового процесса"""
    def __init__(self, width=100, height=30):
        self.speed = 0.1
        self.food = Food(20, 20)
        self.field = Field(width, height)
        self.game_status = True
        self.head = SnakesHead()
        head_x, head_y = self.head.get_position()
        self.body = SnakesBody(head_x, head_y)

    def game_over(self, reason):
        """Функция окончания игры"""
        self.game_status = False
        print('Вы проиграли!!!')
        print(reason)

    def step_of_snake(self):
        """Функция шага змеи"""

        # Новые координаты головы змеи
        new_x, new_y = self.head.get_next_position()

        # Если змея укусила саму себя
        if (new_x, new_y) in self.body.get_positions():
            self.game_over('Ваша змея укусила сама себя.')

        # Если змея выползла за пределы поля
        elif new_x < 0 or new_y < 0 or new_x > self.field.get_height() - 1 or\
                new_y > self.field.get_width() - 1:
            self.game_over('Вы вышли за пределы игрового поля.')

        # Если змея съела цель
        elif (new_x, new_y) == self.food.get_position():
            self.body.make_step(new_x, new_y, True)
            self.head.set_position(new_x, new_y)
            self.food.generate_new_food(self)

        else:
            self.body.make_step(new_x, new_y, False)
            self.head.set_position(new_x, new_y)

        # Добавление тела змейки на игровое поле
        self.field.update_points(self.head, self.body, self.food)

    def mainloop(self):
        """Основной цикл игрового процесса"""
        last = time.time()
        cnt = 0
        while self.game_status:
            time.sleep(0.1)
            if time.time() - last > self.speed:
                cnt += 1
                self.step_of_snake()
                last = time.time()
                os.system('clear')
                self.field.show_field()
                print(f'Длина: {len(self.body.get_elements()) + 1}' + '\t|' +
                      f' Скорость: шаг за {self.speed} сек')

    def on_press(self, key):
        """Функция отслеживания нажатий на клавиши"""
        if key == Key.up:
            self.head.change_direction('up')
        elif key == Key.down:
            self.head.change_direction('down')
        elif key == Key.left:
            self.head.change_direction('left')
        elif key == Key.right:
            self.head.change_direction('right')
        time.sleep(0.1)

    def get_func_for_listener(self):
        """Возвращает функцию отслеживания нажатий на клавиши"""
        return self.on_press


if __name__ == '__main__':

    # Инициализация объекта игры
    snake = GamePlay(30, 80)

    # Активация отслеживания нажатий на клавиши
    listener = Listener(on_press=snake.get_func_for_listener())
    listener.start()

    # Активация игры
    snake.mainloop()
    print('Game over!!!')

    e

