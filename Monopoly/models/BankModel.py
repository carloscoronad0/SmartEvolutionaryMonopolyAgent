import Monopoly.models.BoardComponents as BCs
import Monopoly.models.MonopolyActions as MAs
import numpy as np

from Monopoly.models.PlayerModel import Player
from Monopoly.models.MonopolyStates import RegularMonopolyState, OfferActionMonopolyState
from Monopoly.models.MonopolyActions import ActionInitializationType
from Monopoly.controllers.OnPropertyActionValidator import OnPropertyActionValidator as OPAV
from typing import List, Tuple, Dict

class Bank:
    def __init__(self, properties: List[BCs.Property], streets: List[BCs.StreetProperty], property_dic: Dict, 
        properties_data):
        """
        The properties list is important because the property_dic stores de property indexes

        A second purpose of the properties list, and the first one of the streets list, is to facilitate 
        the conversion from the index arrays contained in the Action Structures coming from the different
        players

        The property_dic function is to smooth the process of verifying and updating the values of the
        different properties, it facilitates the bank with the indexes in the property list of all the
        properties of a same set, it can be color set in the case of streets or just all the properties
        of a certain type

        The properties_data is there to smooth the process of updating a property values, independent if
        they are just a Property or a Street, contains all the data from the csv
        """

        self.properties = properties
        self.streets = streets
        self.property_dic = property_dic
        self.properties_data = properties_data

    def auction(self, initial_players_in_auction: List[Player], property_in_auction_index: int):
        """
        The logic behind the auction function is simple, given a property and a list of players the function
        iterates until there's only one player left. In each iteration it asks each player if the want to continue
        in the acution, if that's the case then the player will continue in the next iteration. 

        To continue in the auction a player must offer a higher bid than the previous one.
        """
        print("\n ---------------- IN AUCTION ------------------ \n")
        
        property_in_auction = self.properties[property_in_auction_index]
        # The initial list passed is copied because the one received as a parameter points to the princial
        # list saved in the MonopolyGame class
        players_in_auction = initial_players_in_auction.copy()

        # The auction starts with the first player in the list
        highest_bid_player = players_in_auction[0]
        highest_money_offer = 1

        # While there's more than one player in the auction
        while len(players_in_auction) > 1:
            # Temporary list to store the players who want to stay in the auction
            players_who_want_to_continue: List[Player] = []

            # For each player who is part of the auction
            for player in players_in_auction:
                # The state for the auction --------------------------------------------------------------------
                # The only relevant information is the property in auction, the highest money offer and it's own
                # properties
                state = OfferActionMonopolyState()
                state.stateType = ActionInitializationType.InitiatedByOtherEntity
                state.info = "From Bank in Auction process"
                state.targetPlayer = player
                state.offerdProperties = [property_in_auction]
                state.moneyAsked = highest_money_offer
                # ----------------------------------------------------------------------------------------------

                # Ask the player to take the specific auction decision based on the state passed
                aux = player.actions([MAs.ActionType.ContinueInAuction], state)
                decision: MAs.AuctionActionStructure = aux.pop(0)
                # Valdiate the decision parameters
                (valid, args) = OPAV._isAuctionDecisionValid(decision.moneyOffer, highest_money_offer, player.money)

                # If the player wish to continue 
                if decision.continueInAuction:
                    # If the player's bid is valid
                    if valid:
                        # Store the player's bid
                        highest_bid_player = player
                        highest_money_offer = decision.moneyOffer
                        players_who_want_to_continue.append(player)
                    
                    # Inform the player about the quality of their decision
                player.inform_decision_quality(state, [MAs.ActionType.ContinueInAuction], [(valid, [args])])

            # Update the list of players who will still be part of the auction
            players_in_auction = players_who_want_to_continue

        # Pay the transaction
        specifications: str = f"--Auction Concluded--\n\tPaying for property {property_in_auction.name} \n\tAt the price: {highest_money_offer}"
        highest_bid_player.pay_transaction(highest_money_offer, specifications)

        # Transfer the property
        self.transfer_property_bank_to_owner(property_in_auction, highest_bid_player)
        
    def trade_assets(self, property_offer_index: List[int], property_asked_index: List[int], money_offer: int, 
        money_asked: int, initial_player: Player, target_player: Player):
        """
        The logic behind the trade_assets function is that the whole process consits of two player decisions:
            
            The first decision is the one that initiates the process, a player identifies a target player and 
            formualtes an offer that may be of his liking. This offer has to be valid, the initial player cannot 
            offer properties that are not his, neither can he offer an amount of money he does not have.

            The target player has to meet the requirements too, he must posses the properties asked by the initial
            player, he must also have the amount of money asked. Once all these requirements are validated, the 
            target player now capable of taking a decision. In this case there isn't necessarily a correct one, 
            and the target player is onlly going to see changes if he accepts the trade offer (The same logic of the
            auction function).
        """
        
        (valid_properties_offer, not_valid_offered_properties) = self._get_indicated_properties(self.properties, initial_player.player_id, property_offer_index)
        (valid_properties_asked, not_valid_asked_properties) = self._get_indicated_properties(self.properties, target_player.player_id, property_asked_index)

        # Validate the initial player decision
        (valid, args) = OPAV._isTradeValid(valid_properties_offer, valid_properties_asked, not_valid_offered_properties,
            not_valid_asked_properties, money_offer, money_asked, initial_player.money, target_player.money)

        # If the decision is valid -> Must ask the target player if the trade is accepted
        if valid: 
            # Form the state of the trade environment 
            state = OfferActionMonopolyState()
            state.stateType = ActionInitializationType.InitiatedByOtherEntity
            state.info = "From Bank in trade process"
            state.initialPlayer = initial_player
            state.targetPlayer = target_player
            state.offerdProperties = valid_properties_offer
            state.askedProperties = valid_properties_asked
            state.moneyOffer = money_offer
            state.moneyAsked = money_asked

            aux = target_player.actions([MAs.ActionType.AcceptTradeOffer], state)
            decision: MAs.BinaryActionStructure = aux.pop(0)

            if decision.response:

                # Exchange Properties
                for prop in valid_properties_offer:
                    self.transfer_property_owner_to_owner(prop, initial_player, target_player)
                
                for prop in valid_properties_asked:
                    self.transfer_property_owner_to_owner(prop, target_player, initial_player)

                # Exchange Money
                initial_player_transfer_payment_details: str = (f"Trade accepted by player {target_player.player_id}\n" + 
                    f"\tTransfering offered money amount {money_offer}")
                intial_pay_amount = initial_player.pay_transaction(money_offer, initial_player_transfer_payment_details)

                target_player_receiving_details: str = (f"Receiving payment for trade action from player {initial_player.player_id}\n" + 
                    f"\tAmount to receive: {intial_pay_amount}")
                target_player.receive_payment(intial_pay_amount, target_player_receiving_details)

                target_player_transfer_payment_details: str = (f"Paying to the trade to player {initial_player.player_id}\n" + 
                    f"Asked amount: {money_asked}")
                target_pay_amount = target_player.pay_transaction(money_asked, target_player_transfer_payment_details)

                initial_player_receiving_details: str = (f"Receiving payment for trade action from player {target_player.player_id}\n" + 
                    f"\tAmount to receive: {target_pay_amount}")
                initial_player.receive_payment(target_pay_amount, initial_player_receiving_details)

                # Because Accept trade offer is only going to have effect when the player accepts the offer,
                # the player only receives the inform of the action when the response is accept
                # None arguments are passed because there's no possibilty of the player taking an invalid 
                # decision.
                target_player.inform_decision_quality(state, [MAs.ActionType.AcceptTradeOffer], None)

        return (valid, args)

    def player_on_bankruptcy(self, bankrupt_player: Player, target_player: Player, complete_list_of_players: List[Player]):
        """
        If a player is bankrupt then this function is called. There are two ocasions which a player may enter
        on bankruptcy:
            
            Owing anoher player, this may be because of rent after falling in of the oponents properties. In this
            case all the houses owned (hotels count as 5 houses) are sold by half the price back to the bank, then
            all the owned properties are transfered to the oponent and all the money (the amount previously had 
            and the amount obtained after selling all houses).

            Owing the bank. The resulting process is a bit larger, a reset is applied on each property to then
            be auctioned to the rest of players. It's considered larger because of all the auction process.
        """
        # List where the amount received by the selling of the properties will be stored
        house_sell_money: List[int] = [0]
        # Passing threw all the bankrupt player properties
        for prop in bankrupt_player.properties:
            # Update the rent back to the initial one (Part of the reset process)
            prop.rent = int(self.properties_data["rent_0"][prop.index])

            if prop.type == "street":
                # The only type of property that can have buildings are the streets
                house_sell_money.append(prop.buildings * (0.5 * prop.house_price))
                # Reseting the buildings bacl to the minimal
                prop._reset_buildings()
                # No street set is completed any longer
                prop.set_completed = False

            # Owner changed to a neutral one (Part of the reset process)
            prop._change_owner(None)

        # Removing the bankrupt player ----------------------------------------------------
        # In this case it's not necessary to make a copy because the player has to be removed from the group 
        # that continues active in the game
        complete_list_of_players.remove(bankrupt_player)

        # If the target player is None then bankrupt playe owes to the bank
        if target_player is None:
            print(f"Player in bankruptcy {bankrupt_player.player_id} with bank")
            for prop in bankrupt_player.properties:
                # Each one of his properties is put in auction
                self.auction(complete_list_of_players, prop.property_index)
        else: # If the target player is not null the the bankrupt player's debt is with an oponent
            print(f"Player in bankruptcy {bankrupt_player.player_id} with {target_player.player_id}")
            # All the money is transfered to the oponent
            total_money = bankrupt_player.money + sum(house_sell_money)
            target_player.receive_payment(total_money, f"Receiving {total_money} payment for bankrupting player {bankrupt_player.player_id}")

            # The oponent receives all the properties too
            for prop in bankrupt_player.properties:
                self.transfer_property_bank_to_owner(prop, target_player)

        # The bankrupt_player variable now points to nothing
        bankrupt_player.bankrupted = True
    
    #region TRANSACTIONS

    def salary_transaction(self, player: Player, salary_amount: int, specifications: str):
        player.receive_payment(salary_amount, specifications)

    def charge_transaction(self, player: Player, amount_to_charge: int, charging_entity: Player, charge_info: str, 
        payment_info: str, state: RegularMonopolyState):
        """
        The charge transaction is mandatory to the player. It's used when charging rents or taxes (Actions the
        player must fulfill). This is the only ocasion a player can enter bankruptcy. The function has three
        levels:
            
            First it asks the player if he has the amount necessary to pay, if that's the case then the amount 
            is discounted and the function ends there.

            In the second level, the function asks the player if he is bankrupted, if that's the case then the 
            player_on_bankruptcy function is called.

            In the third level, knowing that the player doesn't have the amount of money but has the net value,
            then the player is instructed to sell houses or to mortgage properties in order to fullfil the
            payment. After the property unimprovement or mortgages the function is called again.
        """
        
        if player.enough_money(amount_to_charge):
            # Receiving the amount from the charged player
            payment = player.pay_transaction(amount_to_charge, charge_info)
            
            if not (charging_entity is None):
                charging_entity.receive_payment(payment, payment_info)

        elif player.is_bankrupt(amount_to_charge):
            self.player_on_bankruptcy(player, charging_entity, state.playersInGame)

        else:
            # Because the player has the obligation to fulfill the impulsive action, he has to find the way
            # to get money, it has already been validated that the player is not in bankruptcy, so the only 
            # option is for him to sell houses or mortgage properties

            oportunties = 0
            while (not player.enough_money(amount_to_charge)) & (oportunties < 10):
                aux = player.actions([MAs.ActionType.SellHouseOrHotel, MAs.ActionType.MortgageProperty], state)
                sell_decision: MAs.PropertyActionStructure = aux[0]
                mortgage_decision: MAs.PropertyActionStructure = aux[1]

                # Mortgage transaction with mortgage decision
                mortgage_quality = self.mortgage_transaction(mortgage_decision.associatedPropertyList, player)

                # UnImprove transaction with sell decision
                unimprove_quality = self.unimprove_property_transaction(sell_decision.associatedPropertyList, player)

                player.inform_decision_quality(state, [MAs.ActionType.SellHouseOrHotel, MAs.ActionType.MortgageProperty], 
                    [unimprove_quality, mortgage_quality])

                # Update state after the actions
                
                # As a suposition, i believe th state updates by itself because of the pointers
                oportunties += 1

            if (oportunties < 10):
                self.charge_transaction(player, amount_to_charge, charging_entity, charge_info, payment_info, state)
            else:
                self.player_on_bankruptcy(player, charging_entity, state.playersInGame)

    def improve_property_transaction(self, associated_property_list: List[int], player: Player):
        (valid_streets, not_valid_streets) = self._get_indicated_properties(self.streets, player.player_id, associated_property_list)
        (valid, args) = OPAV._isBuyHouseValid(valid_streets, not_valid_streets, player.money)

        if valid:
            for street in valid_streets:
                street.buildings += 1
                rent_string = f"rent_{street.buildings}"
                street.rent = int(self.properties_data[rent_string][street.index])

        return (valid, args)

    def unimprove_property_transaction(self, associated_property_list: List[int], player: Player):
        (valid_streets, not_valid_streets) = self._get_indicated_properties(self.streets, player.player_id, associated_property_list)
        (valid, args) = OPAV._isSellHouseValid(valid_streets, not_valid_streets)

        if valid:
            for street in valid_streets:
                street.buildings -= 1
                rent_string = f"rent_{street.buildings}"
                street.rent = int(self.properties_data[rent_string][street.index])

        return (valid, args)

    def mortgage_transaction(self, associated_property_list: List[int], player: Player):
        (valid_properties, not_valid_properties) = self._get_indicated_properties(self.properties, player.player_id, associated_property_list)
        (valid, args) = OPAV._isMortgagePropertyValid(valid_properties, not_valid_properties)

        if valid:
            for prop in valid_properties:
                prop.mortgage_state = True
                player.receive_payment(prop.mortgage, f"Receiving {prop.mortgage} payment from {prop.name} mortgage")
        
        return (valid, args)

    def free_mortgage_transaction(self, associated_property_list: List[int], player: Player):
        (valid_properties, not_valid_properties) = self._get_indicated_properties(self.properties, player.player_id, associated_property_list)
        (valid, args) = OPAV._isFreePropertyFromMortgageValid(valid_properties, not_valid_properties, player.money)
        
        if valid:
            for prop in valid_properties:
                player.pay_transaction(prop.free_mortgage, f"Paying {prop.free_mortgage} to free property {prop.name} from mortgage")
                prop.mortgage_state = False
        
        return (valid, args)

    def buy_property_transaction(self, property_index: int, player_to_buy: Player):
        property_to_buy = self.properties[property_index]

        (valid, args) = OPAV._isBuyPropertyValid(property_to_buy.cost, player_to_buy.money)

        if valid:
            player_to_buy.pay_transaction(property_to_buy.cost, f"Paying {property_to_buy.cost} to buy {property_to_buy.name}")
            self.transfer_property_bank_to_owner(property_to_buy, player_to_buy)

        return (valid, args)

    def pay_jail_fine_transaction(self, player_in_jail: Player, jail_fine: int):
        money_issue = player_in_jail.money >= jail_fine
        valid = False

        if money_issue & player_in_jail.in_jail:
            valid = True
            
            player_in_jail.pay_transaction(jail_fine, f"Paying {jail_fine} to get out of jail")
            player_in_jail.in_jail = False

        args = [(money_issue, jail_fine)]
        return (valid, args)

    def use_get_out_of_jail_card(self, player_in_jail: Player):
        valid = False

        if player_in_jail.out_of_jail_card & player_in_jail.in_jail:
            valid = True

            player_in_jail.out_of_jail_card = False
            player_in_jail.in_jail = False

        args = [(player_in_jail.out_of_jail_card, player_in_jail.in_jail)]

        return (valid, args)

    #endregion TRASANCTIONS

    #region AUX_FUNCTIONS

    @staticmethod
    def _get_indicated_properties(properties: List[BCs.Property], player_id: int, properties_index: List[int]) -> Tuple[List[BCs.Property], List[int]]:
        valid_properties: BCs.Property = []
        not_valid_properties: int = [] # It's more convenient to administrate this list with just indexes

        # For each indicated property
        for i in properties_index:
            # If the owner is the player (Validating ownership)
            if properties[i].owner != None:
                if properties[i].owner.player_id == player_id:
                    # Add it to the valid list
                    valid_properties.append(properties[i])
                else: # Else add it to the not valids 
                    not_valid_properties.append(i)
            else:
                not_valid_properties.append(i)

        return (valid_properties, not_valid_properties)

    def transfer_property_owner_to_owner(self, property_to_transfer: BCs.Property, old_owner: Player, new_owner: Player):
        old_owner.remove_property(property_to_transfer)
        property_to_transfer._change_owner(new_owner)
        new_owner.add_property(property_to_transfer)

        if property_to_transfer.type == "street":
            self.street_transfer_color_set_check(property_to_transfer, old_owner, new_owner)
        else:
            self.property_transfer_set_check(property_to_transfer, old_owner, new_owner)

    def transfer_property_bank_to_owner(self, property_to_transfer: BCs.Property, new_owner: Player):
        property_to_transfer._change_owner(new_owner)
        new_owner.add_property(property_to_transfer)

        if property_to_transfer.type == "street":
            self.street_transfer_color_set_check(property_to_transfer, None, new_owner)
        else:
            self.property_transfer_set_check(property_to_transfer, None, new_owner)

    def property_transfer_set_check(self, property_transfered: BCs.Property, old_owner: Player, new_owner: Player):
        property_idxs = self.property_dic[property_transfered.type]
        belong_to_old_owner: List[int] = []
        belong_to_new_owner: List[int] = []

        for i in property_idxs:
            if self.properties[i].owner != None:
                if old_owner != None:
                    if self.properties[i].owner.player_id == old_owner.player_id:
                        belong_to_old_owner.append(i)
                elif self.properties[i].owner.player_id == new_owner.player_id:
                    belong_to_new_owner.append(i)

        older_owner_new_rent = f"rent_{len(belong_to_old_owner) - 1}"
        for n in belong_to_old_owner:
            self.properties[n].rent = self.properties_data[older_owner_new_rent][self.properties[n].index]

        new_owner_new_rent = f"rent_{len(belong_to_new_owner) - 1}"
        for m in belong_to_new_owner:
            self.properties[m].rent = self.properties_data[new_owner_new_rent][self.properties[m].index]

    def street_transfer_color_set_check(self, street_transfered: BCs.StreetProperty, old_owner: Player, new_owner: Player):
        streets_of_the_color_idxs: List[int] = self.property_dic[street_transfered.street_color]
        
        if street_transfered.set_completed:
            for i in streets_of_the_color_idxs:
                self.properties[i].set_completed = False
                self.properties[i].rent *= 0.5

            if old_owner != None:
                old_owner.sets_completed -= 1

        else:
            how_many_streets_of_the_color: int = 0
            for i in streets_of_the_color_idxs:
                if self.properties[i].owner != None:
                    if self.properties[i].owner.player_id == new_owner.player_id:
                        how_many_streets_of_the_color += 1

            if how_many_streets_of_the_color == len(streets_of_the_color_idxs):
                for i in streets_of_the_color_idxs:
                    self.properties[i].set_completed = True
                    self.properties[i].rent *= 2

                new_owner.sets_completed += 1

    #endregion AUX_FUNCTIONS
