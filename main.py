"""Точка входа в игру: игровой цикл тамагочи-кликера"""

import os

from game.clicker import MyRandomClicker
from game.exceptions import NotEnoughMoney, TamagochiIsGone
from game.game import MyGame
from game.models import Food, Medicine
from game.tamagochi import MyTamagochi

MENU_COMMANDS: dict[str, str] = {
    '1': 'Пойти на работу',
    '2': 'Купить еду',
    '3': 'Купить лекарство',
    '4': 'Покормить',
    '5': 'Вылечить',
    '6': 'Играть',
    '7': 'Отдых',
    '0': 'Выход',
}


def main() -> None:
    """
    Точка входа в игру: создаёт питомца, кликер и игру,
    затем запускает игровой цикл обработки команд
    """
    all_food = [
        Food(name='Бургер', satiety=20, price=40),
        Food(name='Салат', satiety=10, price=20),
        Food(name='Яблоко', satiety=10, price=15)
    ]

    all_medicine = [
        Medicine(name='Ибупрофен', price=30, heal_hp=20, number_of_uses=2)
    ]

    tamagochi = MyTamagochi()
    clicker = MyRandomClicker(10, 20)
    game = MyGame(
        tamagochi, clicker, all_food=all_food, all_medicine=all_medicine,
    )

    print('Добро пожаловать в Тамагочи-кликер!')
    output = ''

    while True:
        print(output)
        print(f'Сумка с едой: {game.food}')
        print(f'Сумка с лекарствами: {game.medicine}')

        status = game.get_status()
        print(
            f'\nСтатус: голод {status["hunger"]}, здоровье {status["hp"]}, '
            f'энергия {status["energy"]}, усталость {status["fatigue"]}, '
            f'монет {status["coins"]}\n'
        )
        if status['sick']:
            print('Тамагочи болеет')
            print('Отдых действует менее эффективно')
        menu = (f'{cmd}. {text}' for cmd, text in MENU_COMMANDS.items())
        print('\n'.join(menu))

        try:
            match input('Выберите действие: '):
                case '1':
                    output = f'Вы заработали {game.work()} монет'
                case '2':
                    output = game.buy_food()
                case '3':
                    output = game.buy_medicine()
                case '4':
                    output = game.feed_tamagochi()
                case '5':
                    output = game.heal_tamagochi()
                case '6':
                    output = game.play_with_tamagochi()
                case '7':
                    output = game.rest_tamagochi()
                case '0':
                    # Выход до очистки экрана
                    break
                case _:
                    output = 'Неверная команда'
        except NotEnoughMoney:
            output = 'Не хватает монет'
        except TamagochiIsGone:
            print('Тамагочи умер. Игра окончена')
            break

        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    main()
