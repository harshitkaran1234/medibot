from abc import ABC, abstractmethod


class IntegrationClient(ABC):
    client = None

    @abstractmethod
    def init(self, *args, **kwargs):
        pass

    @abstractmethod
    def close(self):
        self.client = None
