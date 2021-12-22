from dataclasses import dataclass

@dataclass
class MonopolyState:
    stateType = None
    info = ""

@dataclass
class RegularMonopolyState(MonopolyState):
    playerInTurnId = 0
    playersInGame = []
    propertiesInGame = []

@dataclass
class OfferActionMonopolyState(MonopolyState):
    initialPlayer = None
    targetPlayer = None
    offerdProperties = []
    askedProperties = []
    moneyOffer = 0
    moneyAsked = 0
