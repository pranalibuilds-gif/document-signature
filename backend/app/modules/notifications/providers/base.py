from abc import ABC, abstractmethod

class EmailProvider(ABC):
    @abstractmethod
    async def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """
        Sends an email and returns True if successful, False otherwise.
        Should raise exception if delivery fails in a way that needs logging.
        """
        pass
