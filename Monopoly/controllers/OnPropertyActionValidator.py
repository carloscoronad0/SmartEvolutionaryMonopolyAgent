import Monopoly.models.Properties as p
from typing import List

MAX_IMPROVEMENTS = 5
MIN_IMPROVEMENTS = 0

class PropertyActionValidator:
    @staticmethod
    def _validate_street_improvement(money: int, street: p.StreetProperty, color_group: List[p.StreetProperty]) -> bool:
        money_issue = money >= street.house_price
        even_color_group_house_issue = all([street.buildings <= color_group[i].buildings for i in range(len(color_group))])
        street_validation = street._can_build_house()

        return money_issue & even_color_group_house_issue & street_validation

    @staticmethod
    def _validate_sell(property: p.Property) -> bool:
        if property.type is "street":
            return property._is_unimproved()
        else:
            return True

    @staticmethod
    def _validate_mortgage(property: p.Property) -> bool:
        mortgage_issue =  property._is_unmortgaged()

        if property.type is "street":
            return property._is_unimproved() & mortgage_issue
        else:
            return mortgage_issue

    @staticmethod
    def _validate_street_breakdown(street: p.StreetProperty, color_group: List[p.StreetProperty]) -> bool:
        even_color_group_house_issue = [street.buildings >= color_group[i].buildings for i in range(len(color_group))]
        street_validation = street._can_sell_house()

        return even_color_group_house_issue & street_validation

    @staticmethod
    def _validate_free_mortgage(money: int, property: p.Property) -> bool:
        money_issue = money >= property.free_mortgage
        mortgage_issue = property._is_mortaged()

        return money_issue & mortgage_issue