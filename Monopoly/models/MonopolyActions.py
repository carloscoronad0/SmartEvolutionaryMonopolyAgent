from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
import Monopoly.models.BoardComponents as BCs

class ActionType(Enum):
    MakeTradeOffer = 1
    ContinueInAuction = 2
    ImproveProperty = 3
    SellHouseOrHotel = 4
    MortgageProperty = 5
    FreeMortgage = 6
    ConcludeActions = 7
    UseGetOutOfJailCard = 8
    PayJailFine = 9
    AcceptTradeOffer = 10
    BuyProperty = 11

class ActionInitializationType(Enum):
    InitiatedByPlayer = 1
    InitiatedByOtherEntity = 2

PRE_ROLL_ACTIONS: List[ActionType] = [ActionType.ConcludeActions, ActionType.MakeTradeOffer, ActionType.ImproveProperty,
        ActionType.SellHouseOrHotel, ActionType.MortgageProperty, ActionType.FreeMortgage]

PRE_ROLL_ACTIONS_IN_JAIL: List[ActionType] = [ActionType.ConcludeActions, ActionType.MakeTradeOffer, 
        ActionType.ImproveProperty, ActionType.SellHouseOrHotel, ActionType.MortgageProperty, ActionType.FreeMortgage,
        ActionType.UseGetOutOfJailCard, ActionType.PayJailFine]

POST_ROLL_ACTIONS: List[ActionType] = [ActionType.ConcludeActions, ActionType.SellHouseOrHotel, 
        ActionType.MortgageProperty, ActionType.FreeMortgage]

POST_ROLL_COUTING_PROPERTY_ACTIONS: List[ActionType] = [ActionType.ConcludeActions, ActionType.SellHouseOrHotel, 
        ActionType.MortgageProperty, ActionType.FreeMortgage, ActionType.BuyProperty]

OUT_OF_TURN_ACTIONS: List[ActionType] = [ActionType.ConcludeActions, ActionType.MakeTradeOffer, 
        ActionType.ImproveProperty, ActionType.SellHouseOrHotel, ActionType.MortgageProperty, ActionType.FreeMortgage]

class PropertyType(Enum):
    Property = 1
    Street = 2
    Neither = 3

@dataclass
class ActionStructure:
    actionType: ActionType

@dataclass
class TradeActionStructure(ActionStructure):
    """
    Here is worth noting that the propertyOffer and propertyAsked attributes DO NOT REPRESENT a
    binary array, example:

        [1, 0, 1, 1, 0, 0, ...]

    The lists should contain only the indexes of the properties, example:

        [1, 5, 8, 9]

    It's not relevant if the list is sorted
    """
    propertyOffer: List[int]
    propertyAsked: List[int]
    moneyOffered: int
    moneyAsked: int
    targetPlayerId: int

@dataclass
class AuctionActionStructure(ActionStructure):
    continueInAuction: bool
    moneyOffer: int

@dataclass
class PropertyActionStructure(ActionStructure):
    """
    Here is worth noting that the associatedPropertyList attribute DO NOT REPRESENT a
    binary array, example:

        [1, 0, 1, 1, 0, 0, ...]

    The list should contain only the indexes of the properties, example:

        [1, 5, 8, 9]

    It's not relevant if the list is sorted
    """
    associatedPropertyList: List[int]
    propertyType: PropertyType

@dataclass
class BinaryActionStructure(ActionStructure):
    response: bool # To represent Accept / Reject
