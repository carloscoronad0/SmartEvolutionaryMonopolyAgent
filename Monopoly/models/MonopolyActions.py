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

class EntityType(Enum):
    Player = 1
    OtherEntity = 2

class PropertyType(Enum):
    Property = 1
    Street = 2
    Neither = 3

class GamePhaseType(Enum):
    PreRoll = 1
    OutOfTurn = 2
    PostRoll = 3

@dataclass
class Action:
    """
    Determines the components that classify an action
    
    Used for determining which actions are posible for the player during the game

        There's going to be one Action instance for each of the ActionTypes, depending on the game 
        phase of a turn, the game is going to determine, based on it's rules, which actions are
        valid for the player to take.

    It's worth saying that this action representation is mainly to facilitate the flow of the program,
    it was not included because of Object Oriented Programming rules. 
    """
    type: ActionType
    initiatedBy: EntityType
    associatedProperties: PropertyType
    gamePhase: GamePhaseType
    responseExpectedDimension: int

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
    propertyOffer: List[BCs.Property]
    propertyAsked: List[BCs.Property]
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
    associatedPropertyList: List[BCs.Property]
    propertyType: PropertyType

@dataclass
class BinaryActionStructure(ActionStructure):
    response: bool # To represent Accept / Reject