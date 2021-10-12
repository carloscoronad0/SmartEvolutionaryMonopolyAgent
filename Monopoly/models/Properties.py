from dataclasses import dataclass, field

@dataclass(order=True)
class BoardComponent:
    sort_index: int = field(init=False, repr=False)
    name: str
    index: str
    type: str

    def __post_init__(self):
        self.sort_index = self.index

@dataclass
class Property(BoardComponent):
    cost: int
    mortgage: int
    rent: int
    owner: int = 0
    mortgage_state: bool = False

@dataclass
class StreetProperty(Property):
    street_color: str = ""
    house_price: int = 0
    buildings: int = 0
    set_completed: bool = False

@dataclass
class Tax(BoardComponent):
    multiplier: int