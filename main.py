# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO
import numpy as np

def delay(input, delay_time, initial_value):
    # Placeholder for delay function implementation
    pass

class charging_station_cost_and_profitability_sector:
    # charging_station_cost_and_profitability sector static variables
    CONSTRUCTION_COST_PER_STATION = _
    LIFETIME_OF_A_STATION = _
    def __init__(self):


class investment_on_charging_stations_sector:
    def __init__(self):
        self.Actual_Private_Investment_in_Charging_Stations = _
        self.Actual_Government_Investment_in_Charging_Stations = _
        self.demand_of_charging_station = _


class charging_station_availability_sector:
    # charging_station_availability sector static variables
    INITIAL_CHARGING_STATIONS_UNDER_CONSTRUCTION = (3*90000*1.5)/(0.1*350*8760)
    """There is a 3 truck difference between 2017 and 2018, and we calculated the demand for initial charging staions based on 350 KW chargers. [Charging stations]"""
    INITIAL_CHARGING_STATIONS = (0.5*90000*1.5)/(0.1*350*8760)
    """There is 1 truck in the year 2017, and we calculated the demand for initial charging staions based on 350 KW chargers. [Charging stations]"""
    TIME_TO_BUILD_A_CHARGING_STATION = 2
    """"Based on interviews and REEL project report REEL. (2022). Regional Electrified Logistics. [Year]"""

    def __init__(self):
        self.investment_on_charging_stations_sector = None #Completed during execution
        self.charging_station_cost_and_profitability_sector = None #Completed during execution
        self.vehicle_fleet_sector = None #Completed during execution
        self.dt = 1
        self.charging_station_capacity_to_demand_ratio = self.installed_Charging_Stations(0)/self.investment_on_charging_stations_sector.demand_of_charging_station
        """[Dmnl]"""
        self.availability_of_charging_station = max(0, min(100*1000, (self.charging_station_capacity_to_demand_ratio*100*1000)))
        """[Dmnl]"""
        self.Building_Charging_Station = (self.investment_on_charging_stations_sector.Actual_Private_Investment_in_Charging_Stations+self.investment_on_charging_stations_sector.Actual_Government_Investment_in_Charging_Stations)/self.charging_station_cost_and_profitability_sector.CONSTRUCTION_COST_PER_STATION
        """[Charging stations/Year]"""
        self.Finishing_Charging_Station = self.charging_Stations_under_construction(0)/self.TIME_TO_BUILD_A_CHARGING_STATION #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[Charging stations/Year]"""
        self.Decaying_Charging_Station = delay(self.Finishing_Charging_Station, self.charging_station_cost_and_profitability_sector.LIFETIME_OF_A_STATION, self.INITIAL_CHARGING_STATIONS/self.charging_station_cost_and_profitability_sector.LIFETIME_OF_A_STATION)
        """[Charging stations/Year]"""
        self.ratio_e-truck_to_charging_station = self.vehicle_fleet_sector.Etruck_Fleet_Size/max(10**-9, self.installed_Charging_Stations(0)) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[Vehicle/Charging stations]"""
    
    def installed_Charging_Stations(self, t):
        """[Charging stations]"""
        if t <= 0:
            res = self.INITIAL_CHARGING_STATIONS
        else:
            res = self.installed_Charging_Stations(t - self.dt)
        return res

    def charging_Stations_under_construction(self, t):
        """[Charging stations]"""
        if t <= 0:
            res = self.INITIAL_CHARGING_STATIONS_UNDER_CONSTRUCTION + (self.Building_Charging_Station - self.Finishing_Charging_Station) * self.dt
        else:
            res = self.charging_Stations_under_construction(t - self.dt) + (self.Building_Charging_Station - self.Finishing_Charging_Station) * self.dt
        return res


class vehicle_fleet_sector:
    def __init__(self):
        self.Etruck_Sales = _
        self.share_of_electric_truck_in_total_fleet_size = _
        self.Total_Truck_Sales = _
        self.Etruck_Fleet_Size = _


class vehicle_cost_sector:
    DIESEL_TRUCK_LIFETIME = _
    PURCHASE_COST_OF_DIESEL_TRUCK = _

    def __init__(self):
        self.Purchase_Cost_of_Etrucks = _
        self.diesel_truck_total_cost = _
        self.electric_truck_total_cost = _


class utility_function_sector:
    # miscellaneous variables
    TIME = _
    # utility_function sector static variables
    INITIAL_UTILITY_FUNCTION = 0.2
    """"initial value for utility function of e-trucks. Base on expert estimation [Dmnl]"""
    TIME_TO_PERCEIVED_UTILITY = 1
    """"The time it takes for users to recognize the benefits of adopting e-trucks. Base on expert estimation [Year]"""
    TIME_TO_SPEND_RD_FUNDS = 3
    """"The duration over which research and development funds are spent. Based on interviews [Year]"""
    TECHNOLOGY_IMPROVEMENT_PER_SEK_SPENT = 1/(7.5*10^9)
    """Based on interviews: 10 times the annual R&D budget - considering that the technology will be mature in 10 years. We summed the R&D investment from 2017 until 10 years. Maximum value for this variable, if we want to introduce "more" delay, then we decrease this further. [technology/SEK]"""
    FACTOR_OF_GOV_INVESTMENT_ON_THE_TECH_MATURITY = 1
    """"magnitude of the impact of government investment on improving e-truck technology maturity.Base scenario value [Dmnl]"""
    GOAL_OF_TECHNOLOGY_MATURITY_FUND = 1
    """maximum level of technology maturity [technology]"""
    MISTRUST_EFFECT = 0.02
    """"The percentage of awareness lost due to mistrust between freight companies. Based on the expert interview, we should consider a percentage of awareness that is ruined during the adoption. [Dmnl]"""
    BASED_UTILITY_FOR_DIESEL_TRUCK = 100
    """"The level of utility (attractiveness) of an d-truck. Based on the expert interview [Dmnl]"""
    WEIGHT_OF_AVAILABILITY = 0.45
    """"this variable represents the weight of the availability of infrastructure influence on the e-truck utility, in comparison with the other influences. Based on the expert interview [Dmnl]"""
    WEIGHT_OF_AWARENESS = 0.4
    """"this variable represents the weight of the awareness influence on the e-truck utility, in comparison with the other influences. Based on the expert interview [Dmnl]"""
    WEIGHT_OF_MATURITY = 0.15
    """"this variable represents the weight of the vehicle technology maturity influence on the e-truck utility, in comparison with the other influences. Based on the expert interview [Dmnl]"""

    def __init__(self):
        self.vehicle_cost_sector = None #Completed during execution
        self.vehicle_fleet_sector = None #Completed during execution
        self.charging_station_availability_sector = None #Completed during execution
        self.dt = 1
        #RATIO OF TECHNOLOGY MATURITY TO GOAL RELATED
        self.ratio_of_technology_maturity_to_goal = GRAPH("Technology_Maturity_of_E-truck"/self.GOAL_OF_TECHNOLOGY_MATURITY_FUND) Points: (0.000, 0.000), (1.000, 1.000) #! QUESTION: HOW TO REPRESENT THIS?
        """current technology maturity relative to its goal. [Dmnl]"""
        self.RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_DIESEL_TRUCKS = 0.015*(1-self.ratio_of_technology_maturity_to_goal)
        """"The portion of income from diesel vehicle sales invested in research and development. Based on interviews with Scania experts, we assume that 1,5% of the income from diesel vehicle sales will be invested on R&D for improving technology maturity of electric vehicles. [Dmnl]"""
        self.STOP_INVESTING_SWITCH = 0 if ((self.TIME >= 2040) & (self.vehicle_fleet_sector.share_of_electric_truck_in_total_fleet_size <= 0.1)) else 1
        """if we are in the year 2040 and we have a lower than 10% market share of electric trucks, that shows that the electric truck project failed, and we should stop investing in this project, then we stop investing from the income of diesel trucks. It helps model in extreme conditions: when we don't have any e-truck sales, we don't have any technology maturity! [Dmnl]"""
        self.RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_ETRUCKS = 0.035*(1-self.ratio_of_technology_maturity_to_goal)
        """"The portion of income from electric vehicle sales invested in research and development. Based on interviews with Scania experts, we assume that 3,5% of the income from electric vehicle sales will be invested on R&D for improving technology maturity of electric vehicles. [Dmnl]"""
        ##
        self.awareness_coefficient = 100*1000*(1-self.MISTRUST_EFFECT)
        """a coefficient to implement the mistruct effect [Dmnl]"""
        self.awareness_of_the_technology = min(self.awareness_coefficient*self.vehicle_fleet_sector.share_of_electric_truck_in_total_fleet_size, 100*1000)
        """Equivalent to the notion of "word of mouth"/"willingness-to-consider"/"knowledge and awareness of technology" within the Technological Innovation System (TIS) framework (Ortt & Kamp, 2022). [Dmnl]"""
        self.awareness_of_the_technology_percentage = self.awareness_of_the_technology/1000
        """the percentage of awareness of technology [Dmnl]"""
        self.effect_of_utility_to_cost = GRAPH(self.U2P_ratio) Points: (0.000, 0.000), (1.000, 1.000) #! QUESTION: HOW TO REPRESENT THIS?
        """rate of utility to cost of e-truck to d-truck scaled between 0 and 1 [Dmnl]"""
        self.Annual_Gov_Tech_Maturity_Fund = self.annual_gov_funding_for_improving_etruck_technology
        """The annual public investment in technology maturity of e-trucks [SEK/year]"""
        self.rD_Investment = self.annual_gov_funding_for_improving_etruck_technology + self.total_annual_RD_investment__corporates
        """Funds allocated to improve e-truck technology and innovation per year [SEK/year]"""
        self.annual_gov_funding_for_improving_etruck_technology = self.total_annual_RD_investment__corporates*self.FACTOR_OF_GOV_INVESTMENT_ON_THE_TECH_MATURITY*(1-self.ratio_of_technology_maturity_to_goal)
        """Annual public investment to improve e-truck technology [SEK/year]"""
        self.effect_of_technology_maturity = min(100*1000, self.ratio_of_technology_maturity_to_goal*100*1000)
        """level of vehicle technology maturity [Dmnl]"""
        self.Effect_of_technology_maturity_percentage = self.effect_of_technology_maturity/1000
        """level of vehicle technology maturity in percentage [Dmnl]"""
        self.rD_Spending = self.rD_Fund_of_Etrucks(0) / self.TIME_TO_SPEND_RD_FUNDS #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """Expenditure on research and development [SEK/year]"""
        self.Technology_Development_of_Etruck = self.rD_Spending * self.TECHNOLOGY_IMPROVEMENT_PER_SEK_SPENT
        """The process of acquiring knowledge and improvements in e-truck technology [technology/year]"""
        self.perceived_etruck_utility_function__attractiveness = (self.charging_station_availability_sector.availability_of_charging_station^self.WEIGHT_OF_AVAILABILITY*self.awareness_of_the_technology^self.WEIGHT_OF_AWARENESS*self.effect_of_technology_maturity^self.WEIGHT_OF_MATURITY)/1000
        """Cobb-Douglas Utility Function (very common to calculate utility in economics), also use for production function [Dmnl]"""
        self.Change_In_Utility = max(0, (self.perceived_etruck_utility_function__attractiveness - self.utility_Function_of_Etruck(0)) / self.TIME_TO_PERCEIVED_UTILITY) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """The rate of annual change for the utility function [Dmnl/year]"""
        #DIESEL
        self.diesel_truck_sale = self.vehicle_fleet_sector.Total_Truck_Sales-self.vehicle_fleet_sector.Etruck_Sales
        """Number of new diesel trucks that are sold in each year [Vehicle/Year]"""
        self.annual_RD_investment_from_diesel_truck_earnings = self.diesel_truck_sale*self.vehicle_cost_sector.PURCHASE_COST_OF_DIESEL_TRUCK*self.RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_DIESEL_TRUCKS*self.STOP_INVESTING_SWITCH
        """Investment allocated to research and development from diesel vehicle sales revenue. [SEK/year]"""
        self.utility_to_cost_of_diesel_truck = self.BASED_UTILITY_FOR_DIESEL_TRUCK/self.vehicle_cost_sector.diesel_truck_total_cost
        """the utility devided by total cost of d-trucks [Dmnl*Vehicle/SEK]"""
        #E-TRUCK
        self.annual_RD_investment_from_etruck_earnings = self.vehicle_fleet_sector.Etruck_Sales*self.vehicle_cost_sector.Purchase_Cost_of_Etrucks*self.RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_ETRUCKS
        """Investment allocated to research and development from electric vehicle sales revenue. [SEK/year]"""
        self.Availability_of_charging_station_percentage = self.charging_station_availability_sector.availability_of_charging_station/1000
        """"The proportion that charging stations are functional and ready for use by electric vehicles. [Dmnl]"""
        self.utility_to_cost_of_etruck = self.utility_Function_of_Etruck(0)/(self.vehicle_cost_sector.electric_truck_total_cost) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """the utility devided by total cost of e-trucks [Dmnl*Vehicle/SEK]"""
        #TOTAL
        self.total_annual_RD_investment__corporates = self.annual_RD_investment_from_etruck_earnings + self.annual_RD_investment_from_diesel_truck_earnings
        """Funds allocated by private sector to research and development activities to improve technology and innovation per year. [SEK/year]"""
        self.U2P_ratio = max(10^-9, self.utility_to_cost_of_etruck)/max(10^-9, self.utility_to_cost_of_diesel_truck)
        """to prevent denominator from being negative in the extreme test [Dmnl]"""

    def utility_Function_of_Etruck(self, t):
        """The level of utility (attractiveness) of an e-truck [Dmnl]"""
        if t <= 0:
            res = self.INITIAL_UTILITY_FUNCTION + (self.Change_In_Utility) * self.dt
        else:
            res = self.utility_Function_of_Etruck(t - self.dt) + (self.Change_In_Utility) * self.dt
        return res

    def technology_Maturity_of_Etruck(self, t):
        """"The level of advancement and development of electric truck technology, indicating how close it is to reaching its full potential and goals. [technology]"""
        if t <= 0:
            res = (self.Technology_Development_of_Etruck) * self.dt
        else:
            res = self.technology_Maturity_of_Etruck(t - self.dt) + (self.Technology_Development_of_Etruck) * self.dt
        return res

    def rD_Fund_of_Etrucks(self, t):
        """Total funds available for electric trucks research and development. [SEK]"""
        if t <= 0:
            res = 1.6e+8 + (self.rD_Investment - self.rD_Spending) * self.dt
        else:
            res = self.rD_Fund_of_Etrucks(t - self.dt) + (self.rD_Investment - self.rD_Spending) * self.dt
        return res

    def gov_Tech_Maturity_Fund_Stock(self, t):
        """The accumulation of public funds contributes to the technological maturity of electric trucks. [SEK]"""
        if t <= 0:
            res = (self.Annual_Gov_Tech_Maturity_Fund) * self.dt
        else:
            res = self.gov_Tech_Maturity_Fund_Stock(t - self.dt) + (self.Annual_Gov_Tech_Maturity_Fund) * self.dt
        return res


class vehicle_fleet_sector:
    # vehicle_fleet sector static variables
    INITIAL_ETRUCK_FLEET_SIZE = 1
    """The starting number of electric trucks in the fleet [Vehicle]"""
    INITIAL_TOTAL_TRUCK_FLEET_SIZE = 83025
    """"The starting number of total trucks in the fleet [Vehicle]"""
    ETRUCK_LIFETIME = 12
    """The average operational lifespan of electric vehicles [Year]"""

    def __init__(self):
        self.utility_function_sector = None #Completed during execution 
        self.vehicle_cost_sector = None #Completed during execution
        self.dt = 1
        self.time_for_truck_sales = _ #! NOT ASSIGNED VALUE FOR THE VARIABLE
        self.Total_Truck_Sales = 148.556*self.time_for_truck_sales-292712
        """Number of new trucks (both electric and diesel) that are sold in each year [Vehicle/Year]"""
        self.Etruck_Sales = self.Total_Truck_Sales*self.utility_function_sector.effect_of_utility_to_cost
        """Number of new electric trucks that are sold in each year [Vehicle/Year]"""
        self.Etruck_Decommission = delay(self.Etruck_Sales, self.ETRUCK_LIFETIME, self.INITIAL_ETRUCK_FLEET_SIZE / self.ETRUCK_LIFETIME) 
        """Number of electric trucks that are removed from use in each year [Vehicle/Year]"""
        self.Total_Truck_Decommission = delay(self.Total_Truck_Sales, self.vehicle_cost_sector.DIESEL_TRUCK_LIFETIME, self.INITIAL_TOTAL_TRUCK_FLEET_SIZE / self.vehicle_cost_sector.DIESEL_TRUCK_LIFETIME)
        """Number of total trucks that are removed from use in each year [Vehicle/Year]"""
        self.share_of_electric_truck_in_new_sales = self.Etruck_Sales / self.Total_Truck_Sales
        """The proportion of the total truck fleet that is sold to the market [Dmnl]"""
    
    def share_of_electric_truck_in_total_fleet_size(self): #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """The proportion of the total truck fleet that is electric [Dmnl]"""
        return self.etruck_Fleet_Size(0) / self.total_Truck_Fleet_Size(0)
    
    def etruck_Fleet_Size(self, t):
        """The total number of electric trucks in the fleet [Vehicle]"""
        if t <= 0:
            res = self.INITIAL_ETRUCK_FLEET_SIZE + (self.Etruck_Sales - self.Etruck_Decommission) * self.dt
        else:
            res = self.etruck_Fleet_Size(t -self.dt) + (self.Etruck_Sales - self.Etruck_Decommission) * self.dt
        return res

    def total_Truck_Fleet_Size(self, t):
        """The total number of trucks in the fleet [Vehicle]"""
        if t <= 0:
            res = self.INITIAL_TOTAL_TRUCK_FLEET_SIZE + (self.Total_Truck_Sales - self.Total_Truck_Decommission) * self.dt
        else:
            res = self.total_Truck_Fleet_Size(t - self.dt) + (self.Total_Truck_Sales - self.Total_Truck_Decommission) * self.dt
        return res
