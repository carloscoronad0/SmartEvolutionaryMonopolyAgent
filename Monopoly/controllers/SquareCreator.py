from Monopoly.models.SquareModels import Square, SquareGo, SquareStreet, SquareTax, SquareJail, SquareJailVisit, SquareChance, SquareCommunity, SquareParking, SquareRailRoad, SquareUtility
from typing import Tuple
import Monopoly.models.BoardComponents as Properties

def create_go(data) -> Tuple[Square.Square, Properties.BoardComponent]:
    (name, index, element_type) = data
    go_component = Properties.BoardComponent(name, index, type=element_type)
    return (SquareGo.SquareGo(go_component), go_component)

def create_street(data) -> Tuple[Square.Square, Properties.BoardComponent]:
    (name, index, element_type, property_index, cost, mortgage, rent, street_index, street_color, house_price) = data
    street_property = Properties.StreetProperty(name=name, index=index, type=element_type, property_index=property_index, 
        cost=cost, mortgage=mortgage, free_mortgage=round(mortgage + (0.10 * mortgage)), rent=rent, 
        street_index=street_index, street_color=street_color, house_price=house_price)
    return (SquareStreet.SquareStreet(street_property), street_property)


def create_tax(data) -> Tuple[Square.Square, Properties.BoardComponent]:
    (name, index, element_type, tax_rent) = data
    tax = Properties.Tax(name=name, index=index, type=element_type, tax=tax_rent)
    return (SquareTax.TaxSquare(tax), tax)


def create_jail(data) -> Tuple[Square.Square, Properties.BoardComponent]:
    (name, index, element_type) = data
    jail_component = Properties.BoardComponent(name=name, index=index, type=element_type)
    return (SquareJail.SquareJail(jail_component), jail_component)


def create_chance(data) -> Tuple[Square.Square, Properties.BoardComponent]:
    (name, index, element_type, chance_cards) = data
    chance_component = Properties.ComponentToDrawCards(name=name, index=index, 
        type=element_type, cardList=chance_cards)
    return (SquareChance.SquareChance(chance_component), chance_component)


def create_community(data) -> Tuple[Square.Square, Properties.BoardComponent]:
    (name, index, element_type, community_cards) = data
    community_component = Properties.ComponentToDrawCards(name=name, index=index, 
        type=element_type, cardList=community_cards)
    return (SquareCommunity.SquareCommunity(community_component), community_component)


def create_jail_visit(data) -> Tuple[Square.Square, Properties.BoardComponent]:
    (name, index, element_type) = data
    jail_visit_component = Properties.BoardComponent(name=name, index=index, type=element_type)
    return (SquareJailVisit.SquareVisit(jail_visit_component), jail_visit_component)


def create_parking(data) -> Tuple[Square.Square, Properties.BoardComponent]:
    (name, index, element_type) = data
    parking_component = Properties.BoardComponent(name=name, index=index, type=element_type)
    return (SquareParking.SquareParking(parking_component), parking_component)


def create_railroad(data) -> Tuple[Square.Square, Properties.BoardComponent]:
    (name, index, element_type, property_index, cost, mortgage, rent) = data
    railroad_property = Properties.Property(name=name, index=index, type=element_type, property_index=property_index, 
        cost=cost, mortgage=mortgage, free_mortgage=round(mortgage + (0.10 * mortgage)), rent=rent)
    return (SquareRailRoad.SquareRailRoad(railroad_property), railroad_property)


def create_utility(data) -> Tuple[Square.Square, Properties.BoardComponent]:
    (name, index, element_type, property_index, cost, mortgage, rent) = data
    utility_property = Properties.Property(name=name, index=index, type=element_type, property_index=property_index, 
        cost=cost, mortgage=mortgage, free_mortgage=round(mortgage + (0.10 * mortgage)), rent=rent)
    return (SquareUtility.SquareUtility(utility_property), utility_property)
