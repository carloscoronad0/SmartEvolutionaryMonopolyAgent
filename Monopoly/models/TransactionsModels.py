import numpy as np

from dataclasses import dataclass, field

@dataclass
class Transaction:
    succesful: bool
    transaction_of_player: int # Who is the transaction for
    operation: str
    general_details: str
    money_used: int # Money used by player

@dataclass
class TradeTransaction(Transaction):
    target_player: int
    money_recieved: int # Money recieved from target player
    properties_offered: np.ndarray
    properties_asked: np.ndarray
    
@dataclass
class AuctionTransaction(Transaction):
    pass

@dataclass
class PropertyTransaction(Transaction):
    on_property: int
    specific_details: str