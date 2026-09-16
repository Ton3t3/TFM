# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO

class utility_function_sector:
    # utility_function sector static variables
    DEFAULT = {
        "time_to_perceived_utility" : 1,
        "time_to_spend_rd_funds" : 3, #WHITE
        "technology_improvement_per_sek_spent" : 1/(7.5E+09),
        "factor_of_gov_investment_on_the_tech_maturity" : 1,
        "goal_of_technology_maturity_fund" : 1, #WHITE
        "mistrust_effect" : 0.02,
        "based_utility_for_diesel_truck" : 100,
        "weight_of_availability" : 0.45,
        "weight_of_awareness" : 0.4,
        "weight_of_maturity" : 0.15,
        # INITIAL
        "initial_utility_function" : 0.2
    }

    STOCK_DEFAULTS = {
        "_integ_technology_maturity_of_etruck" : 0,
        "_integ_rd_fund_of_etrucks" : 1.6e+8,
        "_integ_gov_tech_maturity_fund_stock" : 0 
    }

    # readable_name -> canonical key (DEFAULT key / PySD py_name)
    ALIASES = {
        "TIME_TO_PERCEIVED_UTILITY": "time_to_perceived_utility",
        "TIME_TO_SPEND_RD_FUNDS": "time_to_spend_rd_funds",
        "TECHNOLOGY_IMPROVEMENT_PER_SEK_SPENT": "time_to_spend_rd_funds",
        "FACTOR_OF_GOV_INVESTMENT_ON_THE_TECH_MATURITY": "factor_of_gov_investment_on_the_tech_maturity",
        "GOAL_OF_TECHNOLOGY_MATURITY_FUND": "goal_of_technology_maturity_fund",
        "MISTRUST_EFFECT": "mistrust_effect",
        "BASED_UTILITY_FOR_DIESEL_TRUCK": "based_utility_for_diesel_truck",
        "WEIGHT_OF_AVAILABILITY": "weight_of_availability",
        "WEIGHT_OF_AWARENESS": "weight_of_awareness",
        "WEIGHT_OF_MATURITY": "weight_of_maturity",
        #INITIAL
        "INITIAL_UTILITY_FUNCTION": "initial_utility_function",
        "INITIAL_TECHNOLOGY_MATURITY_OF_ETRUCK": "_integ_technology_maturity_of_etruck",
        "INITIAL_RD_FUND_OF_ETRUCKS": "_integ_rd_fund_of_etrucks",
        "INITIAL_GOV_TECH_MATURITY_FUND_STOCK": "_integ_gov_tech_maturity_fund_stock"
    }

    def __init__(self, model):
        self.model = model.components

    @property
    def TIME_TO_PERCEIVED_UTILITY(self):
        """The time it takes for users to recognize the benefits of adopting e-trucks. Base on expert estimation [Year]"""
        return self.model.time_to_perceived_utility()

    @property
    def TIME_TO_SPEND_RD_FUNDS(self):
        """The duration over which research and development funds are spent. Based on interviews [Year]"""
        return self.model.time_to_spend_rd_funds()

    @property
    def TECHNOLOGY_IMPROVEMENT_PER_SEK_SPENT(self):
        """Based on interviews: 10 times the annual R&D budget - considering that the technology will be mature in 10 years. We summed the R&D investment from 2017 until 10 years. Maximum value for this variable, if we want to introduce "more" delay, then we decrease this further. [technology/SEK]"""
        return self.model.time_to_spend_rd_funds()

    @property   
    def FACTOR_OF_GOV_INVESTMENT_ON_THE_TECH_MATURITY(self):
        """magnitude of the impact of government investment on improving e-truck technology maturity.Base scenario value [Dmnl]"""
        return self.model.factor_of_gov_investment_on_the_tech_maturity()

    @property
    def GOAL_OF_TECHNOLOGY_MATURITY_FUND(self):
        """maximum level of technology maturity [technology]"""
        return self.model.goal_of_technology_maturity_fund()

    @property
    def MISTRUST_EFFECT(self):
        """The percentage of awareness lost due to mistrust between freight companies. Based on the expert interview, we should consider a percentage of awareness that is ruined during the adoption. [Dmnl]"""
        return self.model.mistrust_effect()

    @property
    def BASED_UTILITY_FOR_DIESEL_TRUCK(self):
        """"The level of utility (attractiveness) of an d-truck. Based on the expert interview [Dmnl]"""
        return self.model.based_utility_for_diesel_truck()

    @property           
    def WEIGHT_OF_AVAILABILITY(self):
        """"this variable represents the weight of the availability of infrastructure influence on the e-truck utility, in comparison with the other influences. Based on the expert interview [Dmnl]"""
        return self.model.weight_of_availability()

    @property
    def WEIGHT_OF_AWARENESS(self):
        """"this variable represents the weight of the awareness influence on the e-truck utility, in comparison with the other influences. Based on the expert interview [Dmnl]"""
        return self.model.weight_of_awareness()

    @property
    def WEIGHT_OF_MATURITY(self):
        """"this variable represents the weight of the vehicle technology maturity influence on the e-truck utility, in comparison with the other influences. Based on the expert interview [Dmnl]"""
        return self.model.weight_of_maturity()

    @property
    def INITIAL_UTILITY_FUNCTION(self):
        """initial value for utility function of e-trucks. Base on expert estimation [Dmnl]""" 
        return self.model.initial_utility_function()
     
    # (Green box) (still "constants")
    def RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_DIESEL_TRUCKS(self): 
        """"The portion of income from diesel vehicle sales invested in research and development. Based on interviews with Scania experts, we assume that 1,5% of the income from diesel vehicle sales will be invested on R&D for improving technology maturity of electric vehicles. [Dmnl]"""
        return self.model.rd_percentage_of_annual_earning_of_diesel_trucks()
    
    def RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_ETRUCKS(self): 
        """"The portion of income from electric vehicle sales invested in research and development. Based on interviews with Scania experts, we assume that 3,5% of the income from electric vehicle sales will be invested on R&D for improving technology maturity of electric vehicles. [Dmnl]"""
        return self.model.rd_percentage_of_annual_earning_of_etrucks()

    # (No box) (still "constants")
    def STOP_INVESTING_SWITCH(self): 
        """if we are in the year 2040 and we have a lower than 10% market share of electric trucks, that shows that the electric truck project failed, and we should stop investing in this project, then we stop investing from the income of diesel trucks. It helps model in extreme conditions: when we don't have any e-truck sales, we don't have any technology maturity! [Dmnl]"""
        return self.model.stop_investing_switch()
    
    ## 
    def awareness_coefficient(self):
        """a coefficient to implement the mistruct effect [Dmnl]"""
        return self.model.awareness_coefficient()
    
    def utility_to_cost_of_diesel_truck(self):
        """the utility devided by total cost of d-trucks [Dmnl*Vehicle/SEK]"""
        return self.model.utilitytocost_of_diesel_truck()
    
    ##
    def effect_of_technology_maturity(self): 
        """level of vehicle technology maturity [Dmnl]"""
        return self.model.effect_of_technology_maturity()
    
    def Effect_of_technology_maturity_percentage(self): 
        """level of vehicle technology maturity in percentage [Dmnl]"""
        return self.model.effect_of_technology_maturitypercentage()
    
    def Availability_of_charging_station_percentage(self): 
        """"The proportion that charging stations are functional and ready for use by electric vehicles. [Dmnl]"""
        return self.model.availability_of_charging_stationpercentage()
    
    def annual_RD_investment_from_diesel_truck_earnings(self): 
        """Investment allocated to research and development from diesel vehicle sales revenue. [SEK/year]"""
        return self.model.annual_rd_investment_from_diesel_truck_earnings()
    
    def total_annual_RD_investment__corporates(self): 
        """Funds allocated by private sector to research and development activities to improve technology and innovation per year. [SEK/year]"""
        return self.model.total_annual_rd_investment_corporates()
    
    def annual_gov_funding_for_improving_etruck_technology(self): 
        """Annual public investment to improve e-truck technology [SEK/year]"""
        return self.model.annual_gov_funding_for_improving_etruck_technology()
    
    def awareness_of_the_technology(self): 
        """Equivalent to the notion of "word of mouth"/"willingness-to-consider"/"knowledge and awareness of technology" within the Technological Innovation System (TIS) framework (Ortt & Kamp, 2022). [Dmnl]"""
        return self.model.awareness_of_the_technology()

    def awareness_of_the_technology_percentage(self): 
        """the percentage of awareness of technology [Dmnl]"""
        return self.model.awareness_of_the_technologypercentage()
            
    def perceived_etruck_utility_function__attractiveness(self): 
        """Cobb-Douglas Utility Function (very common to calculate utility in economics), also use for production function [Dmnl]"""
        return self.model.perceived_etruck_utility_function_attractiveness()
    
    def U2P_ratio(self): 
        """to prevent denominator from being negative in the extreme test [Dmnl]"""
        return self.model.u2p_ratio()

    def effect_of_utility_to_cost(self): 
        """rate of utility to cost of e-truck to d-truck scaled between 0 and 1 [Dmnl]"""
        # GRAPH(self.U2P_ratio) Points: (0.000, 0.000), (1.000, 1.000) 
        return self.model.effect_of_utilitytocost()

    def diesel_truck_sale(self): 
        """Number of new diesel trucks that are sold in each year [Vehicle/Year]"""
        return self.model.diesel_truck_sale()

    # Time function dependent - DIRECT
    def ratio_of_technology_maturity_to_goal(self): 
        """current technology maturity relative to its goal. [Dmnl]"""
        # GRAPH(technology_Maturity_of_Etruck/self.GOAL_OF_TECHNOLOGY_MATURITY_FUND) Points: (0.000, 0.000), (1.000, 1.000) 
        return self.model.ratio_of_technology_maturity_to_goal()
    
    def annual_RD_investment_from_etruck_earnings(self): 
        """Investment allocated to research and development from electric vehicle sales revenue. [SEK/year]"""
        return self.model.annual_rd_investment_from_etruck_earnings()
    
    def utility_to_cost_of_etruck(self): 
        """the utility devided by total cost of e-trucks [Dmnl*Vehicle/SEK]"""
        return self.model.utilitytocost_of_etruck()
    
    ## FLOWS
    # Inflows
    def Change_In_Utility(self): 
        """The rate of annual change for the utility function [Dmnl/year]"""
        return self.model.change_in_utility()
    
    def Technology_Development_of_Etruck(self): 
        """The process of acquiring knowledge and improvements in e-truck technology [technology/year]"""
        return self.model.technology_development_of_etruck()
    
    def RD_Investment(self): 
        """Funds allocated to improve e-truck technology and innovation per year [SEK/year]"""  
        return self.model.rd_investment()
    
    def Annual_Gov_Tech_Maturity_Fund(self): 
        """The annual public investment in technology maturity of e-trucks [SEK/year]"""
        return self.model.annual_gov_tech_maturity_fund()
    
    # Outflows
    def RD_Spending(self): 
        """Expenditure on research and development [SEK/year]"""
        return self.model.rd_spending()
    
    ## STOCKS
    def utility_Function_of_Etruck(self): 
        """The level of utility (attractiveness) of an e-truck [Dmnl]"""
        return self.model._integ_utility_function_of_etruck()
    
    def technology_Maturity_of_Etruck(self): 
        """"The level of advancement and development of electric truck technology, indicating how close it is to reaching its full potential and goals. [technology]"""
        return self.model._integ_technology_maturity_of_etruck()
    
    def rD_Fund_of_Etrucks(self): 
        """Total funds available for electric trucks research and development. [SEK]"""
        return self.model._integ_rd_fund_of_etrucks()
    
    def gov_Tech_Maturity_Fund_Stock(self): 
        """The accumulation of public funds contributes to the technological maturity of electric trucks. [SEK]"""
        return self.model._integ_gov_tech_maturity_fund_stock()

   
