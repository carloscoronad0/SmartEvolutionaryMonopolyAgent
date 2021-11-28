from dataclasses import dataclass, field
# from Monopoly.models.PlayerModel import Player

MAX_IMPROVEMENTS = 5
MIN_IMPROVEMENTS = 0

@dataclass(order=True)
class BoardComponent:
    sort_index: int = field(init=False, repr=False)
    name: str
    index: int
    type: str

    def __post_init__(self):
        self.sort_index = self.index

@dataclass
class Property(BoardComponent):
    property_index: int
    cost: int
    mortgage: int
    free_mortgage: int
    rent: int
    owner = None
    mortgage_state: bool = False
    
    def _is_mortaged(self):
        return self.mortgage_state

    def _is_unmortgaged(self):
        return not self.mortgage_state

    def _change_owner(self, new_owner):
        self.owner = new_owner

@dataclass
class StreetProperty(Property):
    street_index: int = 0
    street_color: str = ""
    house_price: int = 0
    buildings: int = 0
    set_completed: bool = False

    def _can_build_house(self) -> bool:
        max_improved_issue = self.buildings < MAX_IMPROVEMENTS
        mortgage_issue = not self.mortgage_state 
        color_group_issue = self.set_completed

        return max_improved_issue & mortgage_issue & color_group_issue

    def _can_sell_house(self) -> bool:
        min_improved_issue = self.buildings > MIN_IMPROVEMENTS
        mortgage_issue = not self.mortgage_state

        return min_improved_issue & mortgage_issue

    def _is_unimproved(self) -> bool:
        return self.buildings == MIN_IMPROVEMENTS

    def _reset_buildings(self):
        self.buildings = MIN_IMPROVEMENTS

@dataclass
class Tax(BoardComponent):
    tax: int