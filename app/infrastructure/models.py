from uuid import UUID
from pydantic import BaseModel

class ContractData(BaseModel):
    """ Модель для создания calldata контракта """
    paymentId: UUID
    tariffId: UUID
    price: int
