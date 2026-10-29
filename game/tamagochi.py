"""Модуль с интерфейсом и реализациями класса тамагочи"""

import random
from abc import ABC, abstractmethod

from .models import Food, Medicine

# Пределы характеристик питомца
MAX_HUNGER: int = 100
MAX_FATIGUE: int = 100
MAX_ENERGY: int = 100
MAX_HP: int = 100

# Стартовые значения характеристик
INITIAL_HUNGER: int = 50
INITIAL_FATIGUE: int = 0
INITIAL_HP: int = 100
INITIAL_ENERGY: int = 100

# Изменения характеристик за одно действие
FEED_ENERGY_COST: int = 5
PLAY_ENERGY_COST: int = 20
PLAY_FATIGUE_GAIN: int = 10
PLAY_HUNGER_GAIN: int = 5
REST_ENERGY_RECOVER: int = 20

# Восстановление усталости за один отдых: здоров / болен
REST_FATIGUE_RECOVER: int = 30
REST_FATIGUE_RECOVER_SICK: int = 15

# Правила IDLE-тика (см. MyTamagochi.update)
IDLE_HUNGER_GAIN: int = 5
IDLE_FATIGUE_GAIN: int = 2
IDLE_ENERGY_LOSS: int = 2
HP_LOSS_ON_MAX_HUNGER: int = 10
HP_LOSS_WHEN_SICK: int = 5
SICK_FATIGUE_GAIN: int = 5
SICK_HUNGER_THRESHOLD: int = 70
SICK_CHANCE: float = 0.2
HP_LOSS_ON_NO_ENERGY: int = 2


class AbstractTamagochi(ABC):
    """Интерфейс логики тамагочи"""

    @abstractmethod
    def feed(self, food: Food) -> None:
        """
        Абстрактный метод для кормления тамагочи

        :param food: объект еды для кормления
        """

    @abstractmethod
    def play(self) -> None:
        """Абстрактный метод для игры с тамагочи"""

    @abstractmethod
    def rest(self) -> None:
        """Абстрактный метод для отдыха тамагочи"""

    @abstractmethod
    def heal(self, medicine: Medicine) -> None:
        """
        Абстрактный метод для лечения тамагочи

        :param medicine: лекарство для лечения
        """

    @property
    @abstractmethod
    def status(self) -> dict[str, int]:
        """
        Абстрактное свойство для доступа ко всем состояниям тамагочи

        :return: словарь со всеми состояниями тамагочи
        """

    @abstractmethod
    def is_alive(self) -> bool:
        """
        Абстрактный метод для проверки жив ли тамагочи

        :return: True если жив, иначе False
        """

    @abstractmethod
    def is_sick(self) -> bool:
        """
        Абстрактный метод для проверки, не заболел ли тамагочи

        :return: True если тамагочи болеет, иначе False
        """

    @abstractmethod
    def update(self) -> None:
        """
        Абстрактный метод для обновления состояний тамагочи.
        Должен использоваться после каждого взаимодействия с тамагочи
        """


class MyTamagochi(AbstractTamagochi):
    """Простая реализация тамагочи"""

    def __init__(self) -> None:
        """Метод инициализации начального состояния тамагочи"""
        self.__hunger: int = INITIAL_HUNGER
        self.__fatigue: int = INITIAL_FATIGUE
        self.__hp: int = INITIAL_HP
        self.__energy: int = INITIAL_ENERGY
        self.__is_sick: bool = False

    def feed(self, food: Food) -> None:
        """
        Метод для кормления тамагочи

        :param food: объект еды для кормления
        """
        self.__hunger = max(0, self.__hunger - food.satiety)
        self.__energy = max(0, self.__energy - FEED_ENERGY_COST)

    def play(self) -> None:
        """Метод для игры с тамагочи"""
        self.__energy = max(0, self.__energy - PLAY_ENERGY_COST)
        self.__fatigue = min(MAX_FATIGUE, self.__fatigue + PLAY_FATIGUE_GAIN)
        self.__hunger = min(MAX_HUNGER, self.__hunger + PLAY_HUNGER_GAIN)

    def rest(self) -> None:
        """
        Метод для отдыха тамагочи:
        болезнь снижает восстанавливаемую усталость вдвое
        """
        recover = (
            REST_FATIGUE_RECOVER_SICK
            if self.__is_sick
            else REST_FATIGUE_RECOVER
        )
        self.__fatigue = max(0, self.__fatigue - recover)
        self.__energy = min(MAX_ENERGY, self.__energy + REST_ENERGY_RECOVER)

    def heal(self, medicine: Medicine) -> None:
        """
        Метод для лечения тамагочи

        :param medicine: лекарство для лечения
        """
        self.__hp = min(MAX_HP, self.__hp + medicine.heal_hp)
        medicine.use()
        self.__is_sick = False

    @property
    def status(self) -> dict[str, int]:
        """
        Свойство для доступа ко всем состояниям тамагочи

        :return: словарь с текущими голодом, усталостью, здоровьем и энергией
        """
        return {
            'hunger': self.__hunger,
            'fatigue': self.__fatigue,
            'hp': self.__hp,
            'energy': self.__energy,
        }

    def is_alive(self) -> bool:
        """
        Проверка, жив ли тамагочи

        :return: True если здоровье больше нуля, иначе False
        """
        return self.__hp > 0

    def is_sick(self) -> bool:
        """
        Проверка, болеет ли тамагочи

        :return: True если тамагочи болеет, иначе False
        """
        return self.__is_sick

    def update(self) -> None:
        """
        IDLE-тик: обновление состояний после каждого действия.

        Правила тика:
        - голод +5, усталость +2, энергия -2;
        - при голоде на максимуме: здоровье -10;
        - при болезни: здоровье -5, усталость +5;
        - при голоде выше 70: шанс 20% заболеть;
        - при нулевой энергии: здоровье -2.
        """
        self.__hunger = min(MAX_HUNGER, self.__hunger + IDLE_HUNGER_GAIN)
        self.__fatigue = min(MAX_FATIGUE, self.__fatigue + IDLE_FATIGUE_GAIN)
        self.__energy = max(0, self.__energy - IDLE_ENERGY_LOSS)
        if self.__hunger >= MAX_HUNGER:
            self.__hp -= HP_LOSS_ON_MAX_HUNGER
        if self.__is_sick:
            self.__hp -= HP_LOSS_WHEN_SICK
            self.__fatigue = min(
                MAX_FATIGUE, self.__fatigue + SICK_FATIGUE_GAIN
            )
        if (
            self.__hunger > SICK_HUNGER_THRESHOLD
            and random.random() < SICK_CHANCE
        ):
            self.__is_sick = True
        if self.__energy == 0:
            self.__hp -= HP_LOSS_ON_NO_ENERGY
