"""Модуль с интерфейсом и реализацией кликера"""

from abc import ABC, abstractmethod
from random import randint


class AbstractClicker(ABC):
    """Интерфейс для кликера"""

    @abstractmethod
    def __init__(self) -> None:
        """Абстрактный метод инициализации кликера"""

    @abstractmethod
    def click(self) -> None:
        """Абстрактный метод клика: основная логика кликера"""

    @property
    @abstractmethod
    def income_per_click(self) -> int:
        """
        Абстрактное свойство для доступа к количеству
        заработанных монет

        :return: количество заработанных монет
        """


class MyRandomClicker(AbstractClicker):
    """Кликер, за каждое нажатие приносящий случайный доход"""

    def __init__(self, min_income: int, max_income: int) -> None:
        """
        Метод инициализации, задающий границы дохода за одно нажатие

        :param min_income: минимальный доход за клик
        :param max_income: максимальный доход за клик
        """
        self.__min_income = min_income
        self.__max_income = max_income
        self._last_income: int = 0

    def click(self) -> None:
        """Логика клика: определяет случайный доход за это нажатие"""
        self._last_income = randint(self.__min_income, self.__max_income)

    @property
    def income_per_click(self) -> int:
        """
        Свойство для доступа к количеству заработанных монет

        :return: количество монет, заработанных за последний клик
        """
        return self._last_income
