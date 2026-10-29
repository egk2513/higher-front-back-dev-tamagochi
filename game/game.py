"""Модуль с интерфейсом и реализацией класса игры"""

import copy
from abc import ABC, abstractmethod

from .clicker import AbstractClicker
from .exceptions import NotEnoughMoney, TamagochiIsGone
from .models import Food, Medicine
from .tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    """Интерфейс для логики игры"""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """
        Абстрактный метод инициализации класса игры

        :param tamagochi: экземпляр тамагочи
        :param clicker: экземпляр кликера
        :param all_food: все доступные варианты еды
        :param all_medicine: все доступные варианты лекарств
        """

    @abstractmethod
    def work(self) -> int:
        """
        Абстрактный метод для логики действия «пойти на работу»

        :return: количество заработанных монет
        """

    @abstractmethod
    def buy_food(self) -> str:
        """
        Абстрактный метод для покупки еды

        :return: сообщение о результате покупки
        """

    @abstractmethod
    def buy_medicine(self) -> str:
        """
        Абстрактный метод для покупки лекарства

        :return: сообщение о результате покупки
        """

    @abstractmethod
    def feed_tamagochi(self) -> str:
        """
        Абстрактный метод для кормления тамагочи

        :return: сообщение о результате кормления
        """

    @abstractmethod
    def heal_tamagochi(self) -> str:
        """
        Абстрактный метод для лечения тамагочи

        :return: сообщение о результате лечения
        """

    @abstractmethod
    def rest_tamagochi(self) -> str:
        """
        Абстрактный метод для отдыха тамагочи

        :return: сообщение о результате отдыха
        """

    @abstractmethod
    def play_with_tamagochi(self) -> str:
        """
        Абстрактный метод для игры с тамагочи

        :return: сообщение о результате игры
        """

    @abstractmethod
    def get_status(self) -> dict[str, int | bool]:
        """
        Абстрактный метод для получения статуса (всех характеристик)
        тамагочи

        :return: словарь со всеми характеристиками тамагочи
        """

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """
        Абстрактное свойство для доступа к сумке с едой

        :return: список с имеющимися (купленными) объектами еды
        """

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """
        Абстрактное свойство для доступа к сумке с лекарствами

        :return: список с имеющимися (купленными) объектами лекарств
        """


class MyGame(AbstractGame):
    """Реализация логики игры: менеджмент ресурсов (монеты, еда, лекарства)"""

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """
        Метод инициализации игры

        :param tamagochi: экземпляр тамагочи
        :param clicker: экземпляр кликера
        :param all_food: все доступные варианты еды
        :param all_medicine: все доступные варианты лекарств
        """
        self.tamagochi = tamagochi
        self.clicker = clicker
        self._all_food = all_food
        self._all_medicine = all_medicine
        self._food_bag: list[Food] = []
        self._medicine_bag: list[Medicine] = []
        self._coins: int = 0

    def work(self) -> int:
        """
        Логика действия «пойти на работу»: клик по кликеру,
        начисление монет и обновление состояния питомца

        :return: количество заработанных монет
        :raises TamagochiIsGone: если после обновления питомец умер
        """
        self.clicker.click()
        income = self.clicker.income_per_click
        self._coins += income
        self._tick()
        return income

    def buy_food(self) -> str:
        """
        Метод для покупки еды

        :return: сообщение о результате покупки
        :raises NotEnoughMoney: если монет на балансе не хватает
        """
        return self._buy(self._all_food, self._food_bag)

    def buy_medicine(self) -> str:
        """
        Метод для покупки лекарства

        :return: сообщение о результате покупки
        :raises NotEnoughMoney: если монет на балансе не хватает
        """
        return self._buy(self._all_medicine, self._medicine_bag)

    def feed_tamagochi(self) -> str:
        """
        Метод для кормления тамагочи

        :return: сообщение о результате кормления
        :raises TamagochiIsGone: если после обновления питомец умер
        """
        if not self._food_bag:
            return 'Сумка с едой пуста'
        index = self._choose_index(self._food_bag)
        if index is None:
            return 'Неверный выбор'
        food = self._food_bag.pop(index)
        self.tamagochi.feed(food)
        self._tick()
        return 'Питомец покормлен'

    def heal_tamagochi(self) -> str:
        """
        Метод для лечения тамагочи

        :return: сообщение о результате лечения
        :raises TamagochiIsGone: если после обновления питомец умер
        """
        # Лечить можно только лекарствами с оставшимися применениями
        available = [
            medicine for medicine in self._medicine_bag
            if not medicine.is_empty()
        ]
        if not available:
            return 'Сумка с лекарствами пуста'
        index = self._choose_index(available)
        if index is None:
            return 'Неверный выбор'
        medicine = available[index]
        self.tamagochi.heal(medicine)
        if medicine.is_empty():
            self._medicine_bag.remove(medicine)
        self._tick()
        return 'Питомец вылечен'

    def rest_tamagochi(self) -> str:
        """
        Метод для отдыха тамагочи

        :return: сообщение о результате отдыха
        :raises TamagochiIsGone: если после обновления питомец умер
        """
        self.tamagochi.rest()
        self._tick()
        return 'Питомец отдохнул'

    def play_with_tamagochi(self) -> str:
        """
        Метод для игры с тамагочи

        :return: сообщение о результате игры
        :raises TamagochiIsGone: если после обновления питомец умер
        """
        self.tamagochi.play()
        self._tick()
        return 'Вы поиграли с питомцем'

    def get_status(self) -> dict[str, int | bool]:
        """
        Метод для получения статуса игры

        :return: словарь со всеми характеристиками тамагочи,
        монетами и признаком болезни
        """
        return {
            **self.tamagochi.status,
            'coins': self._coins,
            'sick': self.tamagochi.is_sick(),
        }

    @property
    def food(self) -> list[Food]:
        """
        Свойство для доступа к сумке с едой

        :return: копия списка купленной еды
        """
        # Возврат копии для защиты от изменения
        return list(self._food_bag)

    @property
    def medicine(self) -> list[Medicine]:
        """
        Свойство для доступа к сумке с лекарствами

        :return: копия списка купленных лекарств
        """
        # Возврат копии для защиты от изменения
        return list(self._medicine_bag)

    def _buy(self, items: list, bag: list) -> str:
        """
        Общий алгоритм покупки: выбор товара, оплата и добавление в сумку

        :param items: список доступных товаров
        :param bag: сумка, в которую кладётся купленный товар
        :return: сообщение о результате покупки
        :raises NotEnoughMoney: если монет на балансе не хватает
        """
        index = self._choose_index(items)
        if index is None:
            return 'Неверный выбор'
        item = items[index]
        if self._coins < item.price:
            raise NotEnoughMoney(
                f'Недостаточно монет: нужно {item.price}, '
                f'есть {self._coins}'
            )
        self._coins -= item.price

        # Создаем копию объекта при покупке, чтобы избежать проблемы с общими ссылками
        bag.append(copy.deepcopy(item))
        return f'Куплено: {item.name}'

    def _choose_index(self, items: list) -> int | None:
        """
        Вспомогательный метод: печатает варианты и возвращает индекс
        выбранного элемента (нумерация вариантов начинается с единицы)

        :param items: список вариантов для выбора
        :return: индекс выбранного варианта или None при неверном вводе
        """
        variants = (
            f'{number}. {item}'
            for number, item in enumerate(items, start=1)
        )
        print('\n'.join(variants))
        try:
            number = int(input('Введите номер: '))
        except ValueError:
            return None
        index = number - 1
        return index if 0 <= index < len(items) else None

    def _tick(self) -> None:
        """
        Вспомогательный метод: обновляет состояние тамагочи
        и завершает игру, если питомец умер

        :raises TamagochiIsGone: если питомец умер
        """
        self.tamagochi.update()
        if not self.tamagochi.is_alive():
            raise TamagochiIsGone('Тамагочи умер')
