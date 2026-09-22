import time
from abc import ABC, abstractmethod


class Sleeper(ABC):
    @abstractmethod
    def sleep(self, delay_seconds: float) -> None:
        pass


class RealSleeper(Sleeper):
    def sleep(self, delay_seconds: float) -> None:
        time.sleep(delay_seconds)
