from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
import Monopoly.models.BoardComponents as BCs

class ActionType(Enum):
    MakeTradeOffer = 1      # RA -> 0:61
    ContinueInAuction = 2   # TA -> [1:3]
    ImproveProperty = 3     # RA -> 61:83
    SellHouseOrHotel = 4    # RA -> 83:105
    MortgageProperty = 5    # RA -> 105:133
    FreeMortgage = 6        # RA -> 133:161
    ConcludeActions = 7     # RA -> 161
    UseGetOutOfJailCard = 8 # RA -> 162
    PayJailFine = 9         # RA -> 163
    AcceptTradeOffer = 10   # TA -> [0]
    BuyProperty = 11        # RA -> 164

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
