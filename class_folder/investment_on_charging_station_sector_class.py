# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO

class investment_on_charging_stations_sector:
    # investment_on_charging_stations sector static variables
    DEFAULT = {
        "reluctance_to_invest_rate" : 0,
        # Percentage of investors that decide not to invest in the charging infrastructure even after all assessments. They are between 0 to 5 percent random number RANDOM NORMAL(0, 0.05 , 0 , 1 , 0 ) [1/Year]
        "time_to_investment_for_private_sector" : 1,
        # Based on expert opinion [Year]
        "time_to_close_gap_for_gov" : 4,
        # Based on interview and inspired by the time distance between elections [Year]
        "time_to_close_gap_for_private_sector" : 1,
        # Based on expert opinion [Year]
        "emission_level_in_2010" : 4.7313E+09,# 4.73E+09,
        # [kgCO2eq/Year]
        "emission_reduction_goal_in_2030" : 0.7,
        # [Dmnl]
        "emission_reduction_goal_in_2045" : 1,
        # [Dmnl]
        "sweden_road_lenght" : 579556,
        # Road lenght: 579 556 [KM]
        "onoff_switch_for_considering_future_charging_demand" : 1,
        # [Dmnl]
        "planning_horizon" : 5,
        # How many years we want to consider as future demand and bring it into our calculation. We calculated the average of three previous years and crossed it over to the planning horizon (5 years) to calculate the total demand for the three coming years. [Year]
        "timeframe_of_average" : 3,
        # The average e-truck sales over a historical period (TIMEFRAME_OF_AVERAGE) are used to estimate the demand for a future time horizon (PLANNING_HORIZON). Thus, by analysing past sales trends, we can forecast potential demand for the upcoming period. [Year]
        "ideal_density_of_charging_stations_based_on_eu_regulations" : 0.02,
        # 1 station for every 50 km. Based on interviews and Masterplan ACEA. (2022). [Charging stations/KM]
        # INITIAL
        "initial_potential_private_fund" : 1.00E+06,
        # [SEK]
        "initial_potential_public_fund" : 1.648E+06 # 1.65E+06
        # according to the klimatklivet data: 1,648,000 kr [SEK]
    }

    STOCK_DEFAULTS = {
        "_integ_gov_charging_subsidy_stock" : 0
    }

    ALIASES = {
        "RELUCTANCE_TO_INVEST_RATE": "reluctance_to_invest_rate",
        "TIME_TO_INVESTMENT_FOR_PRIVATE_SECTOR": "time_to_investment_for_private_sector",
        "TIME_TO_CLOSE_GAP_FOR_GOV": "time_to_close_gap_for_gov",
        "TIME_TO_CLOSE_GAP_FOR_PRIVATE_SECTOR": "time_to_close_gap_for_private_sector",
        "EMISSION_LEVEL_IN_2010": "emission_level_in_2010",
        "EMISSION_REDUCTION_GOAL_IN_2030": "emission_reduction_goal_in_2030",
        "EMISSION_REDUCTION_GOAL_IN_2045": "emission_reduction_goal_in_2045",
        "SWEDEN_ROAD_LENGHT": "sweden_road_lenght",
        "ON_OFF_SWITCH_for_considering_future_charging_demand": "onoff_switch_for_considering_future_charging_demand",
        "PLANNING_HORIZON": "planning_horizon",
        "TIMEFRAME_OF_AVERAGE": "timeframe_of_average",
        "IDEAL_DENSITY_OF_CHARGING_STATIONS_BASED_ON_EU_REGULATIONS": "ideal_density_of_charging_stations_based_on_eu_regulations",
        # INITIAL
        "INITIAL_POTENTIAL_PRIVATE_FUNDS": "initial_potential_private_fund",
        "INITIAL_POTENTIAL_PUBLIC_FUNDS": "initial_potential_public_fund",
        "INITIAL_GOV_CHARGING_SUBSIDY_STOCK": "_integ_gov_charging_subsidy_stock"
    }

    def __init__(self, model):
        self.model = model.components

    @property
    def RELUCTANCE_TO_INVEST_RATE(self):
        """Percentage of investors that decide not to invest in the charging infrastructure even after all assessments. They are between 0 to 5 percent random number RANDOM NORMAL(0, 0.05 , 0 , 1 , 0 ) [1/Year]"""
        return self.model.reluctance_to_invest_rate()

    @property
    def TIME_TO_INVESTMENT_FOR_PRIVATE_SECTOR(self):
        """Based on expert opinion [Year]"""
        return self.model.time_to_investment_for_private_sector()

    @property
    def TIME_TO_CLOSE_GAP_FOR_GOV(self):
        """Based on interview and inspired by the time distance between elections [Year]"""
        return self.model.time_to_close_gap_for_gov(self)

    @property
    def TIME_TO_CLOSE_GAP_FOR_PRIVATE_SECTOR(self):
        """Based on expert opinion [Year]"""
        return self.model.time_to_close_gap_for_private_sector(self)

    @property               
    def EMISSION_LEVEL_IN_2010(self):
        """[kgCO2eq/Year]"""
        return self.model.emission_level_in_2010()

    @property
    def EMISSION_REDUCTION_GOAL_IN_2030(self):
        """[Dmnl]"""
        return self.model.emission_reduction_goal_in_2030(self)

    @property
    def EMISSION_REDUCTION_GOAL_IN_2045(self):
        """[Dmnl]"""
        return self.model.emission_reduction_goal_in_2045(self)

    @property
    def SWEDEN_ROAD_LENGHT(self):
        """Road lenght: 579 556 [KM]"""
        return self.model.sweden_road_lenght(self)

    @property
    def ON_OFF_SWITCH_for_considering_future_charging_demand(self):
        """[Dmnl]"""
        return self.model.onoff_switch_for_considering_future_charging_demand(self)

    @property
    def PLANNING_HORIZON(self):
        """How many years we want to consider as future demand and bring it into our calculation. We calculated the average of three previous years and crossed it over to the planning horizon (5 years) to calculate the total demand for the three coming years. [Year]"""
        return self.model.planning_horizon(self)

    @property
    def TIMEFRAME_OF_AVERAGE(self):
        """The average e-truck sales over a historical period (TIMEFRAME_OF_AVERAGE) are used to estimate the demand for a future time horizon (PLANNING_HORIZON). Thus, by analysing past sales trends, we can forecast potential demand for the upcoming period. [Year]"""
        return self.model.timeframe_of_average(self)

    @property
    def IDEAL_DENSITY_OF_CHARGING_STATIONS_BASED_ON_EU_REGULATIONS(self):
        """"1 station for every 50 km. Based on interviews and Masterplan ACEA. (2022). [Charging stations/KM]"""
        return self.model.ideal_density_of_charging_stations_based_on_eu_regulations(self)

    @property            
    def INITIAL_POTENTIAL_PRIVATE_FUNDS(self):
        """[SEK]"""
        return self.model.initial_potential_private_fund(self)

    @property
    def INITIAL_POTENTIAL_PUBLIC_FUNDS(self):
        """according to the klimatklivet data: 1,648,000 kr [SEK]"""
        return self.model.initial_potential_public_fund(self)
                    
    ##
    def Goal_of_charging_stations_for_full_adoption_of_electric_trucks(self):
        """[Charging stations]"""
        return self.model.goal_of_charging_stations_for_full_adoption_of_electric_trucks()
    
    def goal_of_emission_level_in_2030(self):
        """[kgCO2eq/Year]"""
        return self.model.goal_of_emission_level_in_2030()
    
    def goal_of_emission_level_in_2045(self):
        """[kgCO2eq/Year]"""
        return self.model.goal_of_emission_level_in_2045()
    ##
    def emission_reduction_factor_compared_to_2010_level(self): 
        """[Dmnl]"""
        return self.model.emission_reduction_factor_compared_to_2010_level()

    def Sensitivity_of_private_investors_to_profitability_index(self): 
        """"Based on interviews. The sensitivity of private investors to the profitability index/how important a high profitability index is for investment decisions. PI > 1: The project is profitable. PI = 1: The project breaks even. PI < 1: The project is not profitable, as the costs exceed the returns. In the base scenario, investor sensitivity is moderate. When the profitability index reaches 4, investors are likely to invest at maximum level. [Dmnl]"""
        # GRAPH(self.model.charg_cost_and_profitability.charging_station_profitability__Profitability_index_after_gov_subsidy) Points: (0.00, 0.000), (1.00, 0.000), (5.00, 1.000), (10.00, 1.000)
        return self.model.sensitivity_of_private_investors_to_profitability_index()

    def gov_portion_of_investment_per_station(self): 
        """[SEK/Charging stations]"""
        return self.model.gov_portion_of_investment_per_station()
    
    def private_portion_of_investment_per_station(self): 
        """Capex*(1-alfa)+Opex [SEK/Charging stations]"""
        return self.model.private_portion_of_investment_per_station()
    
    def ratio_of_gov_to_private_investment(self): 
        """[Dmnl]"""
        return self.model.ratio_of_gov_to_private_investment()
                          
    def future_demand_of_charging_station(self): 
        """We used "e-truck sales" because we wanted to add future growth of demand to current demand, so we calculated how many new trucks will need charging stations. [Charging stations]"""
        return self.model._smooth_future_demand_of_charging_stations()
        # return self.model.future_demand_of_charging_station()

    #Time dependent variables - DIRECT                 
    def gap_of_number_of_charging_stations_based_on_regulation(self): 
        """[Charging stations]"""
        return self.model.gap_of_number_of_charging_stations_based_on_regulation()

    def demand_of_charging_station(self): 
        """[Charging stations]"""
        return self.model.demand_of_charging_station()
    
    def market_gap_for_charging_stations(self): 
        """[Charging stations]"""
        return self.model.market_gap_for_charging_stations()
    
    ## FLOWS
    # Inflows
    def Addition_of_Private_Investment_in_Charging_Stations(self): 
        """[SEK/Year]"""
        # return (self.market_gap_for_charging_stations*self.private_portion_of_investment_per_station*self.look_up_profitability_index_to_private_investment)/self.TIME_TO_CLOSE_GAP_FOR_PRIVATE_SECTOR
        return self.model.addition_of_government_investment_in_charging_stations()
    
    def Addition_of_Government_Investment_in_Charging_Stations(self): 
        """[SEK/Year]"""
        return self.model.addition_of_government_investment_in_charging_stations()
    
    def Annual_gov_subsidy_on_charging(self): 
        """[SEK/year]"""
        return self.model.annual_gov_subsidy_on_charging()
    
    # Outflows
    def Actual_Private_Investment_in_Charging_Stations(self): 
        """[SEK/year]"""
        return self.model.actual_private_investment_in_charging_stations()

    def Deciding_not_to_invest__reluctance_to_invest(self):
        """This could be reluctance in investing in electric charging station and we can go for other refueling option instead (like hydogen, biofuel), based on the comment by Astrid in SD transport SIG [SEK/Year]"""
        return self.model.deciding_not_to_invest_reluctance_to_invest()

    def Actual_Government_Investment_in_Charging_Stations(self): 
        """if stock>0, public investment, otherwise 0 [SEK/year]"""
        return self.model.actual_government_investment_in_charging_stations()
    
    ## STOCKS
    def potential_Private_Investment_in_Charging_Stations(self): 
        """[SEK]"""
        return self.model._integ_potential_private_investment_in_charging_stations()
    
    def potential_Government_Investment_in_Charging_Stations(self): 
        """[SEK]"""
        return self.model._integ_potential_government_investment_in_charging_stations()
    
    def gov_Charging_subsidy_stock(self):
        """[SEK]"""
        return self.model._integ_gov_charging_subsidy_stock()
    

