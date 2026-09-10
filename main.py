# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO
import numpy as np

def delay(input, delay_time, initial_value):
    # Placeholder for delay function implementation
    pass

class Model:
    def __init__(self, t0, dt):
        self.t = t0
        self.dt = dt
        self.emission = emission_sector(self)
        self.vehicle_fleet = vehicle_fleet_sector(self)
        self.vehicle_cost = vehicle_cost_sector(self)
        self.utility_function = utility_function_sector(self)
        self.charg_cost_and_profitability = charging_station_cost_and_profitability_sector(self)
        self.charg_availability = charging_station_availability_sector(self)
        self.investment_on_stations = investment_on_charging_stations_sector(self)

    def advance(self):
        self.t += self.dt


class emission_sector:
    # miscellaneous variables
    time_for_carbon_cost = _ #! Var not assigned
    time_for_emission_reduction = _ #! Var not assigned

    #emission sector static variables
    CARBON_SOCIETY_COST = 0.0336*time_for_carbon_cost-60.7712
    """[SEK/kgCO2eq]"""
    SWICH_FOR_NEW_REGULATION_EFFECT = 1
    """[Dmnl]"""
    Carbon_intensity_of_biofuel = 361/1000
    """[kgCO2eq/Litre]"""
    Carbon_intensity_of_diesel = 3424/1000
    """[kgCO2eq/Litre]"""
    Carbon_intensity_of_electricity__fuel = 0
    """driving carbon intensity equal to zero [kgCO2eq/kWh]"""
    factor_for_correction_emission = 0.612
    """Based on discussion with SCB (Statistikmyndigheten) experts"""
    Kwh_to_Litre_converter = 9.8
    """"Energy content in kWh per liter of diesel fuel Energy content in MJ per liter: 36 MJ Conversion factor: 1 MJ = 0.277778 kWh [kWh/Litre]"""

    def __init__(self, model):
        self.model = model

    def emission_reduction_based_on_new_regulation_func(self, time_for_emission_reduction):
        if (time_for_emission_reduction >= 2024): 
            return 0.06 
        elif ((time_for_emission_reduction == 2022) or (time_for_emission_reduction == 2023)):
            return 0.305 
        else: 
            return (1.7606*time_for_emission_reduction-3534.5)/100

    def annual_fuel_consumption__kWh__per_diesel_truck(self):
        """[kWh/(Vehicle*Year)]"""
        return self.model.vehicle_cost.annual_fuel_consumption__Litr__per_diesel_truck*self.Kwh_to_Litre_converter
    
    def emission_reduction_based_on_previous_regulation(self):
        """[Dmnl]"""
        return min(1, (1.7606*self.time_for_emission_reduction-3534.5)/100 if (self.time_for_emission_reduction <= 2021) else (4.4667*self.time_for_emission_reduction-9000.5)/100 )
    
    def emission_reduction_based_on_new_regulation(self):
        """[Dmnl]"""
        return self.emission_reduction_based_on_new_regulation_func(self.time_for_emission_reduction)
    
    def Biofuel_share(self):
        """[Dmnl]"""
        return min(1, self.emission_reduction_based_on_previous_regulation/(1-self.Carbon_intensity_of_biofuel/self.Carbon_intensity_of_diesel)) if self.SWICH_FOR_NEW_REGULATION_EFFECT == 0 else min(1, self.emission_reduction_based_on_new_regulation/(1-self.Carbon_intensity_of_biofuel/self.Carbon_intensity_of_diesel)) 
    
    def Carbon_intensity_of_diesel_fuel_by_considering_biofuel(self):
        """[kgCO2eq/kWh]"""
        return (self.Biofuel_share*self.Carbon_intensity_of_biofuel+(1-self.Biofuel_share)*self.Carbon_intensity_of_diesel)/self.Kwh_to_Litre_converter
    
    ##
    @property
    def Annual_Emission__without_any_etrucks(self): #
        """[kgCO2eq/Year]"""
        return self.total_annual_amount_of_energy*self.Carbon_intensity_of_diesel_fuel_by_considering_biofuel

    @property
    def annual_fuel_consumption__kWh__for_diesel_fleet(self): #
        """[kWh/Year]"""
        return self.annual_fuel_consumption__kWh__per_diesel_truck*self.model.vehicle_cost.Diesel_Truck_Fleet_Size

    @property
    def Annual_operational_emission_from_diesel_trucks(self): #
        """[kgCO2eq/Year]"""
        return self.annual_fuel_consumption__kWh__for_diesel_fleet*self.Carbon_intensity_of_diesel_fuel_by_considering_biofuel*self.factor_for_correction_emission
                
    @property
    def Annual_Gov_Funding_by_Five_Levers(self): #
        """[SEK/Year]"""
        return -(self.model.investment_on_stations.Annual_gov_subsidy_on_charging+self.model.vehicle_cost.Annual_gov_subsidy_on_vehicle_purchase_cost+self.model.utility_function.annual_gov_funding_for_improving_etruck_technology+self.model.charg_cost_and_profitability.annual_gov_fund_on_EL_price+self.model.vehicle_cost.Annual_Gov_Fund_on_Diesel_Price)

    @property
    def Annual_Total_Gov_Funds(self): #
        """[SEK/Year]"""
        return self.model.investment_on_stations.Annual_gov_subsidy_on_charging+self.model.vehicle_cost.Annual_gov_subsidy_on_vehicle_purchase_cost+self.model.utility_function.annual_gov_funding_for_improving_etruck_technology

    @property
    def Total_annual_emission_from_trucks__tank_to_wheel(self): #
        """[kgCO2eq/Year]"""
        return (self.Annual_operational_emission_from_etrucks+self.Annual_operational_emission_from_diesel_trucks)

    @property
    def Annual_Emission__with_having_etrucks(self): #
        """[kgCO2eq/Year]"""
        return self.Total_annual_emission_from_trucks__tank_to_wheel
               
    @property
    def Annual_carbon_cost(self): #
        """[SEK/Year]"""
        return self.Total_annual_emission_from_trucks__tank_to_wheel*self.CARBON_SOCIETY_COST
                
    @property
    def Saving_emission_converted_to_money_due_to_electrification(self): #
        """[SEK]"""
        return self.Saving_emission_by_transit_to_electrification*self.CARBON_SOCIETY_COST

    @property
    def Emission_per_kwh__annually(self): #
        """[kgCO2eq/kWh]"""
        return self.Total_annual_emission_from_trucks__tank_to_wheel/self.total_annual_amount_of_energy
                
    # Time dependent variables - DIRECT
    @property
    def Saving_emission_by_transit_to_electrification(self): #
        """[kgCO2eq]"""
        return self.cumulative_Emission_without_any_etrucks(self.model.t)-self.cumulative_Emission_with_having_etrucks(self.model.t)
                
    @property
    def Annual_operational_emission_from_etrucks(self): #
        """[kgCO2eq/Year]"""
        return self.model.charg_cost_and_profitability.charging_consumption_per_etruck_per_year*self.model.vehicle_fleet.etruck_Fleet_Size(self.model.t)*self.Carbon_intensity_of_electricity__fuel         

    @property
    def Gov_total_fund_per_vehicle(self): #
        """[SEK/Vehicle]"""
        return self.total_Gov_Funds(self.model.t)/self.model.vehicle_fleet.etruck_Fleet_Size(self.model.t)
                
    @property
    def total_annual_amount_of_energy(self): #
        """[kWh/Year]"""
        return self.model.vehicle_cost.Diesel_Truck_Fleet_Size*self.annual_fuel_consumption__kWh__per_diesel_truck+self.model.vehicle_fleet.etruck_Fleet_Size(self.model.t)*self.model.charg_cost_and_profitability.charging_consumption_per_etruck_per_year 

    @property
    def Share_of_diesel_truck_in_total_fleet_size(self): #
        """[Dmnl]"""
        return self.model.vehicle_cost.Diesel_Truck_Fleet_Size/self.model.vehicle_fleet.total_Truck_Fleet_Size(self.model.t)

    @property
    def Monetarized_saving_emissions_per_investment_unit_in_electrification(self): #
        """[Dmnl]"""
        return self.Saving_emission_converted_to_money_due_to_electrification/self.total_Gov_Funds(self.model.t)
                        
    # Time functions
    @property
    def government_Fund_Balance_by_Five_Levers(self, t): #
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_Gov_Funding_by_Five_Levers) * self.model.dt
        else:
            res = self.government_Fund_Balance_by_Five_Levers(t - self.model.dt) + (self.Annual_Gov_Funding_by_Five_Levers) * self.model.dt
        return res

    @property
    def cumulative_Emission_without_any_etrucks(self, t): #
        """small initial value near to zero [kgCO2eq]"""
        if t <= 0:
            res = 10^-9 + (self.Annual_Emission__without_any_etrucks) * self.model.dt
        else:
            res = self.cumulative_Emission_without_any_etrucks(t - self.model.dt) + (self.Annual_Emission__without_any_etrucks) * self.model.dt
        return res

    @property
    def cumulative_Emission_with_having_etrucks(self, t): #
        """small initial value near to zero [kgCO2eq]"""
        if t <= 0:
            res = 10^-9 + (self.Annual_Emission__with_having_etrucks) * self.model.dt
        else:
            res = self.cumulative_Emission_with_having_etrucks(t - self.model.dt) + (self.Annual_Emission__with_having_etrucks) * self.model.dt
        return res

    @property
    def total_Gov_Funds(self, t): #
        """small initial value near to zero [SEK]"""
        if t <= 0:
            res = 10^-9 + (self.Annual_Total_Gov_Funds) * self.model.dt
        else: 
            res = self.total_Gov_Funds(t - self.model.dt) + (self.Annual_Total_Gov_Funds) * self.model.dt
        return res


class charging_station_cost_and_profitability_sector:
    # miscellaneous variables
    time_for_price_of_electricity = _ #! Var not assigned
    OPERATIONAL_AND_MAINTENANCE_COST = _ #! Var not assigned

    # charging_station_cost_and_profitability sector static variables
    time_unit = 1
    """Formulation of the unit for IRR is complicated. Thus we used this vriable to fix unit left and hand right problem. It doesn't change the model [Year]"""
    CONSTRUCTION_COST_PER_STATION = 1,80E+06
    """Construction cost per kW [SEK/Charging stations]"""
    LIFETIME_OF_A_STATION = 8
    """"Based on interviews, EU report page 204, and REEL project report European Commission. (2021). Impact Assessment: Proposal for a Regulation of the European Parliament and of the Council on the deployment of alternative fuels infrastructure, and repealing Directive 2014/94/EU of the European Parliament and of the Council. REEL. (2022). Regional Electrified Logistics. [Year]"""
    sensitivity_coefficient_for_CHARGING_SUBSIDY = 1
    """[Dmnl]"""
    sensitivity_coefficient_for_EL = 1
    """using only for sensitivity analysis [Dmnl]"""
    Ancillary_revenue = 0
    """[SEK/(Charging stations*Year)]"""
    AVERAGE_CONSUMPTION_PER_KM_FOR_ETRUCK = 1.5
    """[kWh/KM]"""
    AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR = 90000
    """[KM/(Vehicle*Year)]"""
    MARGIN_OF_CHARGING_PROVIDERS_FOR_ELECTRICITY_PRICE = 0.2
    """Based on interviews [Dmnl]"""
    DISCOUNT_RATE = 0.1
    """[Dmnl]"""
    MAX_NOMINAL_CAPACITY_OF_A_STATION_PER_YEAR = 350*8760
    """Charger Power (kw/station)* 8760 hour/year [kWh/(Year*Charging stations)]"""
    
    def __init__(self, model):
        self.model = model

    def PRICE_OF_ELECTRICITY(self):
        """[SEK/kWh]"""
        return (0.0415*self.time_for_price_of_electricity-83.286)*self.sensitivity_coefficient_for_EL
        
    def charging_consumption_per_etruck_per_year(self):
        """[kWh/(Vehicle*Year)]"""
        return self.AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR*self.AVERAGE_CONSUMPTION_PER_KM_FOR_ETRUCK

    def r__common_ratio_in_geometric_series(self):
        """[Dmnl]""" 
        return (1/(1+self.DISCOUNT_RATE))
        
    def operational_AND_maintenance_cost_of_a_station__based_on_percentage_of_capex(self):
        """The annual cost of operating and maintaining a charging station [SEK/(Charging stations*Year)]"""
        return 0.05*self.CONSTRUCTION_COST_PER_STATION
        
    def discount_factor_for_stations(self):
        """Geometric series formula [Year]"""
        return (self.r__common_ratio_in_geometric_series*(1-self.r__common_ratio_in_geometric_series^(self.LIFETIME_OF_A_STATION/self.time_unit))/(1-self.r__common_ratio_in_geometric_series))*self.time_unit

    ##
    @property
    def MAX_UTILIZATION_RATE_OF_A_STATION_percentage(self): #
        """[Dmnl]"""
        return self.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks*100

    @property
    def maximum_available_capacity_of_a_station_per_year(self): #
        """[kWh/(Year*Charging stations)]"""
        return self.MAX_NOMINAL_CAPACITY_OF_A_STATION_PER_YEAR*self.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks

    @property
    def construction_cost_per_station_paid_by_infra_providers(self):#
        """[SEK/Charging stations]"""
        return self.CONSTRUCTION_COST_PER_STATION*(1-self.GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS)

    @property
    def Construction_cost_paid_by_infra_providers_per_station_per_year__discounted(self): #
        """[SEK/(Charging stations*Year)]"""
        return self.construction_cost_per_station_paid_by_infra_providers/self.discount_factor_for_stations

    @property
    def CHARGE_RETAIL_PRICE(self): #
        """a ceil of 5*price of EL is considered to control the model in extreme test. [SEK/kWh]"""
        return min((((self.Construction_cost_paid_by_infra_providers_per_station_per_year__discounted+self.operation_cost_per_station_per_year)/self.utilized_capacity_of_a_station_per_year)*(1+self.MARGIN_OF_CHARGING_PROVIDERS_FOR_ELECTRICITY_PRICE)), 5*self.PRICE_OF_ELECTRICITY)

    @property
    def sale_revenue(self): #
        """[SEK/(Charging stations*Year)]"""
        return self.utilized_capacity_of_a_station_per_year*self.CHARGE_RETAIL_PRICE

    @property
    def revenue_per_station_per_year(self): #
        """[SEK/(Charging stations*Year)]"""
        return self.sale_revenue+self.Ancillary_revenue   
                
    @property
    def charging_station_profitability__Profitability_index_after_gov_subsidy(self): #
        """[Dmnl]"""
        return ((self.revenue_per_station_per_year-self.operation_cost_per_station_per_year)*self.discount_factor_for_stations)/self.construction_cost_per_station_paid_by_infra_providers
                       
    @property
    def annual_gov_subsidy_on_charging_2(self): #
        """[SEK/Year]"""
        return self.model.charg_availability.Building_Charging_Station*self.CONSTRUCTION_COST_PER_STATION*self.GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS      
        
    @property
    def utilization_in_total(self): #
        """[Dmnl]"""
        return self.total_consumption_of_electric_fleet/self.total_capacity_of_all_installed_station

    @property
    def utilization_in_total_percentage(self): #
        """[Dmnl]"""
        return self.utilization_in_total*100
            
    @property
    def utilization_rate_of_a_station(self): #
        """[Dmnl]"""
        return min(self.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks, self.Average_energy_demand_from_each_station_per_year/self.MAX_NOMINAL_CAPACITY_OF_A_STATION_PER_YEAR)

    @property
    def utilized_capacity_of_a_station_per_year(self): #
        """[kWh/(Year*Charging stations)]"""
        return self.MAX_NOMINAL_CAPACITY_OF_A_STATION_PER_YEAR*self.utilization_rate_of_a_station

    @property
    def cost_of_electricity_per_station_per_year(self): #
        """[SEK/(Charging stations*Year)]"""
        return self.utilized_capacity_of_a_station_per_year*self.PRICE_OF_ELECTRICITY

    @property
    def operation_cost_per_station_per_year(self): #
        """[SEK/(Charging stations*Year)]"""
        return (self.cost_of_electricity_per_station_per_year+self.OPERATIONAL_AND_MAINTENANCE_COST)

    @property
    def total_operational_cost_per_station__accumulated_over_lifetime_years(self): #
        """[SEK/Charging stations]"""
        return self.operation_cost_per_station_per_year*self.discount_factor_for_stations
              
    @property
    def GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS(self): #
        """Put a maximum to avoid to be more than 1! [Dmnl]"""
        return min(0.99, 0.7*(1-self.model.vehicle_fleet.share_of_electric_truck_in_total_fleet_size)*self.sensitivity_coefficient_for_CHARGING_SUBSIDY)      

    @property
    def max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks(self): #
        """"min of 0.1; max of 0.7 Based on interviews and Anders Grauers course Grauers, A. (2023). Electromobility: a system perspective [Course]. Swedish Electromobility Centre, Chalmers University of Technology. [Dmnl]"""
        return GRAPH(self.model.vehicle_fleet.share_of_electric_truck_in_total_fleet_size) Points: (0.000, 0.1000), (1.000, 0.7000) #! QUESTION: HOW TO REPRESENT THIS?

    @property
    def Charging_station_Capacity_to_demand_ratio_percentage(self): #
        """[Dmnl]"""
        return self.model.charg_availability.charging_station_capacity_to_demand_ratio*100
                
    # Time dependent variables - DIRECT
    @property
    def annual_gov_fund_on_EL_price(self): #
        """Positive amounts show that governments pay subsidies on EL; Negative amounts show that governments receive taxes on EL [SEK/Year]"""
        return (0.0415*self.time_for_price_of_electricity-83.286)*self.charging_consumption_per_etruck_per_year*self.model.vehicle_fleet.etruck_Fleet_Size(self.model.t)*(1-self.sensitivity_coefficient_for_EL) 
            
    @property
    def Annual_income_of_electricity__inflow(self): #
        """[SEK/Year]"""
        return self.charging_consumption_per_etruck_per_year*self.model.vehicle_fleet.etruck_Fleet_Size(self.model.t)*self.PRICE_OF_ELECTRICITY  

    @property
    def Average_energy_demand_from_each_station_per_year(self): #
        """to avoid being zero in the denominator [kWh/(Charging stations*Year)]"""
        return self.charging_consumption_per_etruck_per_year*self.model.vehicle_fleet.etruck_Fleet_Size(self.model.t)/max(10^-9, self.model.charg_availability.installed_Charging_Stations(self.model.t))   

    @property
    def Power_supply_per_etruck_per_year(self): #
        """[kWh/(Year*Vehicle)]"""
        return self.Total_power_supply_by_all_charging_station_per_year/self.model.vehicle_fleet.etruck_Fleet_Size(self.model.t)
                
    @property
    def total_consumption_of_electric_fleet(self): #
        """[kWh/Year]"""
        return self.charging_consumption_per_etruck_per_year*self.model.vehicle_fleet.etruck_Fleet_Size(self.model.t)
                
    @property
    def Total_power_supply_by_all_charging_station_per_year(self): #
        """[kWh/Year]"""
        return self.utilized_capacity_of_a_station_per_year*self.model.charg_availability.installed_Charging_Stations(self.model.t)
        
    @property
    def total_capacity_of_all_installed_station(self): #
        """[kWh/Year]"""
        return self.maximum_available_capacity_of_a_station_per_year*self.model.charg_availability.installed_Charging_Stations(self.model.t)
    

    # Time functions
    @property
    def income_of_electricity_stock(self, t): #
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_income_of_electricity__inflow) * self.model.dt
        else:
            res = self.income_of_electricity_stock(t - self.model.dt) + (self.Annual_income_of_electricity__inflow) * self.model.dt
        return res

    @property
    def gov_fund_on_EL_price_stock(self, t): #
        """[SEK]"""
        if t <= 0:
            res = (self.annual_gov_fund_on_EL_price) * self.model.dt
        else:
            res = self.gov_fund_on_EL_price_stock(t - self.model.dt) + (self.annual_gov_fund_on_EL_price) * self.model.dt
        return res

    @property
    def gov_Charging_subsidy_stock_2(self, t): #
        """[SEK]"""
        if t <= 0:
            res = ("annual_gov._subsidy_on_charging_2") * self.model.dt
        else:
            res = self.gov_Charging_subsidy_stock_2(t - self.model.dt) + ("annual_gov._subsidy_on_charging_2") * self.model.dt
        return res


class investment_on_charging_stations_sector:
    # miscellaneous variables 
    TIME = _ #! Var not assigned
    timeframe_of_average = _ #! Var not assigned (MAYBE IS THE SAME AS "TIMEFRAME_OF_AVERAGE" CONSTANT VARIABLE)
    planning_horizon_in_year = _ #! Var not assigned
    look_up_profitability_index_to_private_investment = _ #! Var not assigned
    Deciding_not_to_invest__reluctance_to_invest = _ #! Var not assigned

    # investment_on_charging_stations sector static variables
    INITIAL_POTENTIAL_PUBLIC_FUNDS = 1,65E+06
    """according to the klimatklivet data: 1,648,000 kr [SEK]"""
    INITIAL_POTENTIAL_PRIVATE_FUNDS = 1,00E+06
    """[SEK]"""
    TIME_TO_INVESTMENT_FOR_PRIVATE_SECTOR = 1
    """Based on expert opinion [Year]"""
    TIME_TO_CLOSE_GAP_FOR_GOV = 4
    """Based on interview and inspired by the time distance between elections [Year]"""
    TIME_TO_CLOSE_GAP_FOR_PRIVATE_SECTOR = 1
    """Based on expert opinion [Year]"""
    EMISSION_LEVEL_IN_2010 = 4.73E+09
    """[kgCO2eq/Year]"""
    EMISSION_REDUCTION_GOAL_IN_2030 = 0.7
    """[Dmnl]"""
    EMISSION_REDUCTION_GOAL_IN_2045 = 1
    """[Dmnl]"""
    SWEDEN_ROAD_LENGHT = 579556
    """Road lenght: 579 556 [KM]"""
    ON_OFF_SWITCH_for_considering_future_charging_demand = 1
    """[Dmnl]"""
    PLANNING_HORIZON = 5
    """How many years we want to consider as future demand and bring it into our calculation. We calculated the average of three previous years and crossed it over to the planning horizon (5 years) to calculate the total demand for the three coming years. [Year]"""
    TIMEFRAME_OF_AVERAGE = 3
    """The average e-truck sales over a historical period (TIMEFRAME_OF_AVERAGE) are used to estimate the demand for a future time horizon (PLANNING_HORIZON). Thus, by analysing past sales trends, we can forecast potential demand for the upcoming period. [Year]"""
    IDEAL_DENSITY_OF_CHARGING_STATIONS_BASED_ON_EU_REGULATIONS = 0.02
    """"1 station for every 50 km. Based on interviews and Masterplan ACEA. (2022). [Charging stations/KM]"""
    
    def __init__(self, model):
        self.model = model

    def Goal_of_charging_stations_for_full_adoption_of_electric_trucks(self):
        """[Charging stations]"""
        return self.SWEDEN_ROAD_LENGHT*self.IDEAL_DENSITY_OF_CHARGING_STATIONS_BASED_ON_EU_REGULATIONS
        
    def goal_of_emission_level_in_2030(self):
        """[kgCO2eq/Year]"""
        return self.EMISSION_LEVEL_IN_2010*(1-self.EMISSION_REDUCTION_GOAL_IN_2030)
        
    def goal_of_emission_level_in_2045(self):
        """[kgCO2eq/Year]"""
        return self.EMISSION_LEVEL_IN_2010*(1-self.EMISSION_REDUCTION_GOAL_IN_2045)
        
    ##
    @property    
    def emission_reduction_factor_compared_to_2010_level(self): #
        """[Dmnl]"""
        return 1+(self.model.emission.Total_annual_emission_from_trucks__tank_to_wheel-self.EMISSION_LEVEL_IN_2010)/self.EMISSION_LEVEL_IN_2010
        
    @property
    def Sensitivity_of_private_investors_to_profitability_index(self): #
        """"Based on interviews. The sensitivity of private investors to the profitability index/how important a high profitability index is for investment decisions. PI > 1: The project is profitable. PI = 1: The project breaks even. PI < 1: The project is not profitable, as the costs exceed the returns. In the base scenario, investor sensitivity is moderate. When the profitability index reaches 4, investors are likely to invest at maximum level. [Dmnl]"""
        return GRAPH(self.model.charg_cost_and_profitability.charging_station_profitability__Profitability_index_after_gov_subsidy) Points: (0.00, 0.000), (1.00, 0.000), (5.00, 1.000), (10.00, 1.000) #! QUESTION: HOW TO REPRESENT THIS?
        
    @property
    def gov_portion_of_investment_per_station(self): #
        """[SEK/Charging stations]"""
        return self.model.charg_cost_and_profitability.CONSTRUCTION_COST_PER_STATION*self.model.charg_cost_and_profitability.GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS        
            
    @property
    def private_portion_of_investment_per_station(self): #
        """Capex*(1-alfa)+Opex [SEK/Charging stations]"""
        return self.model.charg_cost_and_profitability.CONSTRUCTION_COST_PER_STATION*(1-self.model.charg_cost_and_profitability.GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS)

    @property
    def ratio_of_gov_to_private_investment(self): #
        """[Dmnl]"""
        return self.gov_portion_of_investment_per_station/self.private_portion_of_investment_per_station
                
    @property
    def Addition_of_Private_Investment_in_Charging_Stations(self): #
        """[SEK/Year]"""
        return (self.market_gap_for_charging_stations*self.private_portion_of_investment_per_station*self.look_up_profitability_index_to_private_investment)/self.TIME_TO_CLOSE_GAP_FOR_PRIVATE_SECTOR
                
    @property
    def Annual_gov_subsidy_on_charging(self): #
        """[SEK/year]"""
        return self.Actual_Government_Investment_in_Charging_Stations
                
    @property
    def future_demand_of_charging_station(self): #
        """We used "e-truck sales" because we wanted to add future growth of demand to current demand, so we calculated how many new trucks will need charging stations. [Charging stations]"""
        return (SMTH1(self.model.vehicle_fleet.Etruck_Sales, self.timeframe_of_average)*self.model.charg_cost_and_profitability.charging_consumption_per_etruck_per_year*self.planning_horizon_in_year)/self.model.charg_cost_and_profitability.maximum_available_capacity_of_a_station_per_year #! QUESTION: Usage of SMTH1 function
                

    #Time dependent variables - DIRECT  
    @property
    def Actual_Government_Investment_in_Charging_Stations(self): #
        """if stock>0, public investment, otherwise 0 [SEK/year]"""
        return self.Actual_Private_Investment_in_Charging_Stations*self.ratio_of_gov_to_private_investment if (self.potential_Government_Investment_in_Charging_Stations(self.model.t) > 0) else 0

    @property
    def Addition_of_Government_Investment_in_Charging_Stations(self): #
        """[SEK/Year]"""
        if ((self.TIME <= 2030) & (self.model.emission.Total_annual_emission_from_trucks__tank_to_wheel <= self.goal_of_emission_level_in_2030)):
            return 0
        elif ((self.TIME <= 2045) & (self.model.emission.Total_annual_emission_from_trucks__tank_to_wheel <= self.goal_of_emission_level_in_2045)):
            return 0
        else: 
            return ((self.gap_of_number_of_charging_stations_based_on_regulation*self.gov_portion_of_investment_per_station)-self.potential_Government_Investment_in_Charging_Stations(self.model.t))/self.TIME_TO_CLOSE_GAP_FOR_GOV       

    @property        
    def Actual_Private_Investment_in_Charging_Stations(self): #
        """[SEK/year]"""
        return (self.potential_Private_Investment_in_Charging_Stations(self.model.t)/self.TIME_TO_INVESTMENT_FOR_PRIVATE_SECTOR)
                
    @property
    def gap_of_number_of_charging_stations_based_on_regulation(self): #
        """[Charging stations]"""
        return self.Goal_of_charging_stations_for_full_adoption_of_electric_trucks-self.model.charg_availability.installed_Charging_Stations(self.model.t)
                
    @property
    def demand_of_charging_station(self): #
        """[Charging stations]"""
        return (self.model.vehicle_fleet.etruck_Fleet_Size(self.model.t)*self.model.charg_cost_and_profitability.charging_consumption_per_etruck_per_year)/self.model.charg_cost_and_profitability.maximum_available_capacity_of_a_station_per_year

    @property
    def market_gap_for_charging_stations(self): #
        """[Charging stations]"""
        return max(0, self.demand_of_charging_station+(self.future_demand_of_charging_station*self.ON_OFF_SWITCH_for_considering_future_charging_demand)-self.model.charg_availability.installed_Charging_Stations(self.model.t))
                
    # Time functions
    @property
    def potential_Private_Investment_in_Charging_Stations(self, t): #
        """[SEK]"""
        if t <= 0:
            res = self.INITIAL_POTENTIAL_PRIVATE_FUNDS + (self.Addition_of_Private_Investment_in_Charging_Stations - self.Deciding_not_to_invest__reluctance_to_invest - self.Actual_Private_Investment_in_Charging_Stations) * self.model.dt
        else:
            res = self.potential_Private_Investment_in_Charging_Stations(t - self.model.dt) + (self.Addition_of_Private_Investment_in_Charging_Stations - self.Deciding_not_to_invest__reluctance_to_invest - self.Actual_Private_Investment_in_Charging_Stations) * self.model.dt
        return res

    @property
    def potential_Government_Investment_in_Charging_Stations(self, t): #
        """[SEK]"""
        if t <= 0:
            res = self.INITIAL_POTENTIAL_PUBLIC_FUNDS + (self.Addition_of_Government_Investment_in_Charging_Stations - self.Actual_Government_Investment_in_Charging_Stations) * self.model.dt
        else:
            res = self.potential_Government_Investment_in_Charging_Stations(t - self.model.dt) + (self.Addition_of_Government_Investment_in_Charging_Stations - self.Actual_Government_Investment_in_Charging_Stations) * self.model.dt
        return res
    
    @property
    def gov_Charging_subsidy_stock(self, t): #
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_gov_subsidy_on_charging) * self.model.dt
        else:
            res = self.gov_Charging_subsidy_stock(t - self.model.dt) + (self.Annual_gov_subsidy_on_charging) * self.model.dt
        return res


class charging_station_availability_sector: 
    # charging_station_availability sector static variables
    INITIAL_CHARGING_STATIONS_UNDER_CONSTRUCTION = (3*90000*1.5)/(0.1*350*8760)
    """There is a 3 truck difference between 2017 and 2018, and we calculated the demand for initial charging staions based on 350 KW chargers. [Charging stations]"""
    INITIAL_CHARGING_STATIONS = (0.5*90000*1.5)/(0.1*350*8760)
    """There is 1 truck in the year 2017, and we calculated the demand for initial charging staions based on 350 KW chargers. [Charging stations]"""
    TIME_TO_BUILD_A_CHARGING_STATION = 2
    """"Based on interviews and REEL project report REEL. (2022). Regional Electrified Logistics. [Year]"""

    def __init__(self, model):
        self.model = model

    ##
    @property
    def Building_Charging_Station(self): #
        """[Charging stations/Year]"""
        return (self.model.investment_on_stations.Actual_Private_Investment_in_Charging_Stations+self.model.investment_on_sstations.Actual_Government_Investment_in_Charging_Stations)/self.model.charg_cost_and_profitability.CONSTRUCTION_COST_PER_STATION
        
    @property
    def Decaying_Charging_Station(self): #
        """[Charging stations/Year]"""
        return delay(self.Finishing_Charging_Station, self.model.charg_cost_and_profitability.LIFETIME_OF_A_STATION, self.INITIAL_CHARGING_STATIONS/self.model.charg_cost_and_profitability.LIFETIME_OF_A_STATION)

    @property
    def availability_of_charging_station(self): #
        """[Dmnl]"""
        return max(0, min(100*1000, (self.charging_station_capacity_to_demand_ratio*100*1000)))
                
    # Time dependent variables - DIRECT
    @property
    def Finishing_Charging_Station(self): #
        """[Charging stations/Year]"""
        return self.charging_Stations_under_construction(self.model.t)/self.TIME_TO_BUILD_A_CHARGING_STATION

    @property
    def charging_station_capacity_to_demand_ratio(self): #
        """[Dmnl]"""
        return self.installed_Charging_Stations(self.model.t)/self.model.investment_on_stations.demand_of_charging_station

    @property
    def ratio_etruck_to_charging_station(self): #
        """[Vehicle/Charging stations]"""
        return self.model.vehicle_fleet.etruck_Fleet_Size(self.model.t)/max(10**-9, self.installed_Charging_Stations(self.model.t))
            
    # Time functions
    @property
    def installed_Charging_Stations(self, t): #
        """[Charging stations]"""
        if t <= 0:
            res = self.INITIAL_CHARGING_STATIONS
        else:
            res = self.installed_Charging_Stations(t - self.model.dt)
        return res

    @property
    def charging_Stations_under_construction(self, t): #
        """[Charging stations]"""
        if t <= 0:
            res = self.INITIAL_CHARGING_STATIONS_UNDER_CONSTRUCTION + (self.Building_Charging_Station - self.Finishing_Charging_Station) * self.model.dt
        else:
            res = self.charging_Stations_under_construction(t - self.model.dt) + (self.Building_Charging_Station - self.Finishing_Charging_Station) * self.model.dt
        return res


class vehicle_cost_sector:
    # miscellaneous variables
    time_for_diesel_price = _ #! Var not assigned
    MAINTENANCE_COST_PER_KM_FOR_DIESEL_TRUCK = _ #! Var not assigned
    MAINTENANCE_COST_PER_KM_FOR_ETRUCK = _ #! Var not assigned

    # vehicle_cost sector static variables
    DIESEL_TRUCK_LIFETIME = 12
    """[Year]"""
    sensitivity_coefficient_for_VEHICLE_SUBSIDY = 1
    """Only use for sensitivity analysis [Dmnl]"""
    sensitivity_coefficient_for_DIESEL = 1
    """Only use for sensitivity analysis [Dmnl]"""
    PURCHASE_COST_OF_DIESEL_TRUCK = 1.76E+06
    """EV: 5,513,100 SEK/vehicle Diesel: 1,759,500 SEK/vehicle EV: 470,000 EURO/vehicle Diesel: 150,000 EURO/vehicle EUR to SEK: 11.73 (14 May 2024) [SEK/Vehicle]"""
    LEARNING_EFFECT_DELAY = 2
    """Based on expert opinion [Year]"""
    AVERAGE_CONSUMPTION_PER_KM_FOR_DIESEL_TRUCK = 0.25
    """100 km, 27 litre ICCT report, table 1 page 9 = 0.27 [Litre/KM]"""

    def __init__(self, model):
        self.model = model

    def DIESEL_RETAIL_PRICE(self):
        """"swedish diesel price energimyndigheten [SEK/Litre]"""
        return (0.286*self.time_for_diesel_price-562.16)*self.sensitivity_coefficient_for_DIESEL

    def cost_of_diesel_fuel_per_km(self):
        """[SEK/KM]"""
        return self.AVERAGE_CONSUMPTION_PER_KM_FOR_DIESEL_TRUCK*self.DIESEL_RETAIL_PRICE
        
    def DIESEL_RETAIL_PRICE__SEK_per_kWh(self):
        """[SEK/kWh]"""
        return self.DIESEL_RETAIL_PRICE/self.model.emission.Kwh_to_Litre_converter
    
    def annual_fuel_consumption__Litr__per_diesel_truck(self):
        """[Litre/(Vehicle*Year)]"""
        return self.model.charg_cost_and_profitability.AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR*self.AVERAGE_CONSUMPTION_PER_KM_FOR_DIESEL_TRUCK
    
    def annual_operation_cost__Opex__of_each_diesel_truck(self):
        """[SEK/(Vehicle*Year)]"""
        return (self.cost_of_diesel_fuel_per_km+self.MAINTENANCE_COST_PER_KM_FOR_DIESEL_TRUCK)*self.model.charg_cost_and_profitability.AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR
    
    def discount_factor_for_diesel_truck(self):
        """[Year]"""
        return self.model.charg_cost_and_profitability.r__common_ratio_in_geometric_series*(1-self.model.charg_cost_and_profitability.r__common_ratio_in_geometric_series^(self.DIESEL_TRUCK_LIFETIME/self.model.charg_cost_and_profitability.time_unit))/(1-self.model.charg_cost_and_profitability.r__common_ratio_in_geometric_series)*self.model.charg_cost_and_profitability.time_unit
    
    def diesel_truck_discounted_total_opex(self):
        """[SEK/Vehicle]"""
        return self.annual_operation_cost__Opex__of_each_diesel_truck*self.discount_factor_for_diesel_truck
    
    def diesel_truck_total_cost(self):
        """[SEK/Vehicle]"""
        return self.PURCHASE_COST_OF_DIESEL_TRUCK+self.diesel_truck_discounted_total_opex
    
    def discount_factor_for_etruck(self):
        """[Year]"""
        self.model.charg_cost_and_profitability.r__common_ratio_in_geometric_series*(1-self.model.charg_cost_and_profitability.r__common_ratio_in_geometric_series^(self.model.vehicle_fleet.ETRUCK_LIFETIME/self.model.charg_cost_and_profitability.time_unit))/(1-self.model.charg_cost_and_profitability.r__common_ratio_in_geometric_series)*self.model.charg_cost_and_profitability.time_unit
    
    ##
    @property
    def cost_of_electricity_per_km(self): #
        """[SEK/KM]"""
        return self.model.charge_cost_and_profitability.AVERAGE_CONSUMPTION_PER_KM_FOR_ETRUCK*self.model.charg_cost_and_profitability.CHARGE_RETAIL_PRICE   

    @property
    def annual_operation_cost__opex__of_each_etruck(self): #
        """[SEK/(Vehicle*Year)]"""
        return (self.cost_of_electricity_per_km+self.MAINTENANCE_COST_PER_KM_FOR_ETRUCK)*self.model.charg_cost_and_profitability.AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR

    @property
    def etruck_discounted_total_Opex(self): #
        """[SEK/Vehicle]"""
        return self.annual_operation_cost__opex__of_each_etruck*self.discount_factor_for_etruck
                    
    @property
    def GOV_SUBSIDY_PERCENTAGE_ON_DIFFERENCE_BETWEEN_ETRUCK_AND_DIESEL_TRUCK_PURCHASE_COSTS(self): #
        """Klimatklivet:Funding 40% of the additional cost compared to a similar conventional truck. [Dmnl]"""
        return 0.4*(1-self.model.vehicle_fleet.share_of_electric_truck_in_total_fleet_size)*self.sensitivity_coefficient_for_VEHICLE_SUBSIDY

    @property
    def Decrease_in_purchase_cost_of_etruck(self): #
        """[SEK/(Year*Vehicle)]"""
        return self.model.utility_function.ratio_of_technology_maturity_to_goal*self.purchase_cost_gap/self.LEARNING_EFFECT_DELAY

    @property
    def Annual_Gov_Fund_on_Diesel_Price(self): #
        """Positive amounts show that governments pay subsidies on DIESEL Negative amounts show that governments receive taxes on DIESEL"""
        return (0.286*self.time_for_diesel_price-562.16)*self.annual_fuel_consumption__Litr__per_diesel_truck*self.Diesel_Truck_Fleet_Size*(1-self.sensitivity_coefficient_for_DIESEL)
                
    @property
    def Annual_Income_of_Diesel__inflow(self): #
        """[SEK/Year]"""
        return self.annual_fuel_consumption__Litr__per_diesel_truck*self.Diesel_Truck_Fleet_Size*self.DIESEL_RETAIL_PRICE
                           
    #Time function dependant - DIRECT
    @property
    def purchase_cost_gap(self): #
        """[SEK/Vehicle]"""
        return self.purchase_Cost_of_Etrucks(self.model.t)-self.PURCHASE_COST_OF_DIESEL_TRUCK
                
    @property
    def Annual_gov_subsidy_on_vehicle_purchase_cost(self): #
        """[SEK/Year]"""
        self.GOV_SUBSIDY_PERCENTAGE_ON_DIFFERENCE_BETWEEN_ETRUCK_AND_DIESEL_TRUCK_PURCHASE_COSTS*(self.purchase_Cost_of_Etrucks(self.model.t)-self.PURCHASE_COST_OF_DIESEL_TRUCK)*self.model.vehicle_fleet.Etruck_Sales

    @property
    def purchase_cost_paid_by_freight_companies(self): #
        """Price e-truck - Subsidy percentage* (Diffference between electric and regular) [SEK/Vehicle]"""
        return self.purchase_Cost_of_Etrucks(self.model.t)-(self.GOV_SUBSIDY_PERCENTAGE_ON_DIFFERENCE_BETWEEN_ETRUCK_AND_DIESEL_TRUCK_PURCHASE_COSTS*(self.purchase_Cost_of_Etrucks(self.model.t)-self.PURCHASE_COST_OF_DIESEL_TRUCK))

    @property
    def electric_truck_total_cost(self): #
        """[SEK/Vehicle]"""
        return (self.purchase_cost_paid_by_freight_companies+self.etruck_discounted_total_Opex)

    @property
    def Diesel_Truck_Fleet_Size(self): #
        """[Vehicle]"""
        return self.model.vehicle_fleet.total_Truck_Fleet_Size(self.model.t)-self.model.vehicle_fleet.etruck_Fleet_Size(self.model.t)
                 
    # Time functions
    @property
    def purchase_Cost_of_Etrucks(self, t): #
        """EV: 5,513,100 SEK/vehicle Diesel: 1,759,500 SEK/vehicle EV: 470,000 EURO/vehicle Diesel: 150,000 EURO/vehicle EUR to SEK: 11.73 (14 May 2024) [SEK/Vehicle]"""
        if t <= 0:
            res = 5.5131e+06 + ( - self.Decrease_in_purchase_cost_of_etruck) * self.model.dt
        else:
            res = self.purchase_Cost_of_Etrucks(t - self.model.dt) + ( - self.Decrease_in_purchase_cost_of_etruck) * self.model.dt
        return res

    @property
    def income_of_Diesel__Stock(self, t): #
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_Income_of_Diesel__inflow) * self.model.dt
        else: 
            res = self.income_of_Diesel__Stock(t - self.model.dt) + (self.Annual_Income_of_Diesel__inflow) * self.model.dt
        return res

    @property
    def gov_Fund_on_Diesel_Price(self, t): #
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_Gov_Fund_on_Diesel_Price) * self.model.dt
        else:
            res = self.gov_Fund_on_Diesel_Price(t - self.model.dt) + (self.Annual_Gov_Fund_on_Diesel_Price) * self.model.dt
        return res

    @property
    def gov_vehicle_subsidy_stock(self, t): #
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_gov_subsidy_on_vehicle_purchase_cost) * self.model.dt
        else:
            res = self.gov_vehicle_subsidy_stock(t - self.model.dt) + (self.Annual_gov_subsidy_on_vehicle_purchase_cost) * self.model.dt
        return res


class utility_function_sector:
    # miscellaneous variables
    TIME = _ #! Var not assigned

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

    def __init__(self, model):
        self.model = model

    def ratio_of_technology_maturity_to_goal(self):
        """current technology maturity relative to its goal. [Dmnl]"""
        return GRAPH("Technology_Maturity_of_E-truck"/self.GOAL_OF_TECHNOLOGY_MATURITY_FUND) Points: (0.000, 0.000), (1.000, 1.000) #! QUESTION: HOW TO REPRESENT THIS?
    
    def RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_DIESEL_TRUCKS(self):
        """"The portion of income from diesel vehicle sales invested in research and development. Based on interviews with Scania experts, we assume that 1,5% of the income from diesel vehicle sales will be invested on R&D for improving technology maturity of electric vehicles. [Dmnl]"""
        return 0.015*(1-self.ratio_of_technology_maturity_to_goal)
    
    def RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_ETRUCKS(self):
        """"The portion of income from electric vehicle sales invested in research and development. Based on interviews with Scania experts, we assume that 3,5% of the income from electric vehicle sales will be invested on R&D for improving technology maturity of electric vehicles. [Dmnl]"""
        return 0.035*(1-self.ratio_of_technology_maturity_to_goal)
    
    def awareness_coefficient(self):
        """a coefficient to implement the mistruct effect [Dmnl]"""
        return 100*1000*(1-self.MISTRUST_EFFECT)
    
    def effect_of_technology_maturity(self):
        """level of vehicle technology maturity [Dmnl]"""
        return min(100*1000, self.ratio_of_technology_maturity_to_goal*100*1000)
    
    def Effect_of_technology_maturity_percentage(self):
        """level of vehicle technology maturity in percentage [Dmnl]"""
        return self.effect_of_technology_maturity/1000
    
    def utility_to_cost_of_diesel_truck(self):
        """the utility devided by total cost of d-trucks [Dmnl*Vehicle/SEK]"""
        return self.BASED_UTILITY_FOR_DIESEL_TRUCK/self.model.vehicle_cost.diesel_truck_total_cost
    
    ##
    @property
    def Availability_of_charging_station_percentage(self): #
        """"The proportion that charging stations are functional and ready for use by electric vehicles. [Dmnl]"""
        return self.model.charg_availability.availability_of_charging_station/1000
        
    @property
    def STOP_INVESTING_SWITCH(self): #
        """if we are in the year 2040 and we have a lower than 10% market share of electric trucks, that shows that the electric truck project failed, and we should stop investing in this project, then we stop investing from the income of diesel trucks. It helps model in extreme conditions: when we don't have any e-truck sales, we don't have any technology maturity! [Dmnl]"""
        return 0 if ((self.TIME >= 2040) & (self.model.vehicle_fleet.share_of_electric_truck_in_total_fleet_size <= 0.1)) else 1

    @property
    def annual_RD_investment_from_diesel_truck_earnings(self): #
        """Investment allocated to research and development from diesel vehicle sales revenue. [SEK/year]"""
        return self.diesel_truck_sale*self.model.vehicle_cost.PURCHASE_COST_OF_DIESEL_TRUCK*self.RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_DIESEL_TRUCKS*self.STOP_INVESTING_SWITCH

    @property
    def total_annual_RD_investment__corporates(self): #
        """Funds allocated by private sector to research and development activities to improve technology and innovation per year. [SEK/year]"""
        return self.annual_RD_investment_from_etruck_earnings + self.annual_RD_investment_from_diesel_truck_earnings

    @property
    def annual_gov_funding_for_improving_etruck_technology(self): #
        """Annual public investment to improve e-truck technology [SEK/year]"""
        return self.total_annual_RD_investment__corporates*self.FACTOR_OF_GOV_INVESTMENT_ON_THE_TECH_MATURITY*(1-self.ratio_of_technology_maturity_to_goal)
    
    @property
    def rD_Investment(self): #
        """Funds allocated to improve e-truck technology and innovation per year [SEK/year]"""  
        return self.annual_gov_funding_for_improving_etruck_technology + self.total_annual_RD_investment__corporates

    @property
    def Annual_Gov_Tech_Maturity_Fund(self): #
        """The annual public investment in technology maturity of e-trucks [SEK/year]"""
        return self.annual_gov_funding_for_improving_etruck_technology       
        
    @property
    def awareness_of_the_technology(self): #
        """Equivalent to the notion of "word of mouth"/"willingness-to-consider"/"knowledge and awareness of technology" within the Technological Innovation System (TIS) framework (Ortt & Kamp, 2022). [Dmnl]"""
        return min(self.awareness_coefficient*self.model.vehicle_fleet.share_of_electric_truck_in_total_fleet_size, 100*1000)

    @property
    def awareness_of_the_technology_percentage(self): #
        """the percentage of awareness of technology [Dmnl]"""
        return self.awareness_of_the_technology/1000
            
    @property
    def perceived_etruck_utility_function__attractiveness(self): #
        """Cobb-Douglas Utility Function (very common to calculate utility in economics), also use for production function [Dmnl]"""
        return (self.model.charg_availability.availability_of_charging_station^self.WEIGHT_OF_AVAILABILITY*self.awareness_of_the_technology^self.WEIGHT_OF_AWARENESS*self.effect_of_technology_maturity^self.WEIGHT_OF_MATURITY)/1000

    @property
    def Technology_Development_of_Etruck(self): #
        """The process of acquiring knowledge and improvements in e-truck technology [technology/year]"""
        return self.rD_Spending * self.TECHNOLOGY_IMPROVEMENT_PER_SEK_SPENT
                
    @property
    def U2P_ratio(self): #
        """to prevent denominator from being negative in the extreme test [Dmnl]"""
        return max(10^-9, self.utility_to_cost_of_etruck)/max(10^-9, self.utility_to_cost_of_diesel_truck)

    @property
    def effect_of_utility_to_cost(self): #
        """rate of utility to cost of e-truck to d-truck scaled between 0 and 1 [Dmnl]"""
        return GRAPH(self.U2P_ratio) Points: (0.000, 0.000), (1.000, 1.000) #! QUESTION: HOW TO REPRESENT THIS?

    @property
    def diesel_truck_sale(self): #
        """Number of new diesel trucks that are sold in each year [Vehicle/Year]"""
        return self.model.vehicle_fleet.Total_Truck_Sales-self.model.vehicle_fleet.Etruck_Sales
                
    # Time function dependent - DIRECT
    @property
    def annual_RD_investment_from_etruck_earnings(self): #
        """Investment allocated to research and development from electric vehicle sales revenue. [SEK/year]"""
        return self.model.vehicle_fleet.Etruck_Sales*self.model.vehicle_cost.purchase_Cost_of_Etrucks(self.model.t)*self.RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_ETRUCKS

    @property
    def rD_Spending(self): #
        """Expenditure on research and development [SEK/year]"""
        return self.rD_Fund_of_Etrucks(self.model.t) / self.TIME_TO_SPEND_RD_FUNDS 
                
    @property
    def Change_In_Utility(self): #
        """The rate of annual change for the utility function [Dmnl/year]"""
        return max(0, (self.perceived_etruck_utility_function__attractiveness - self.utility_Function_of_Etruck(self.model.t)) / self.TIME_TO_PERCEIVED_UTILITY)

    @property
    def utility_to_cost_of_etruck(self): #
        """the utility devided by total cost of e-trucks [Dmnl*Vehicle/SEK]"""
        return self.utility_Function_of_Etruck(self.model.t)/(self.model.vehicle_cost.electric_truck_total_cost)
                           
    # Time functions
    @property
    def utility_Function_of_Etruck(self, t): #
        """The level of utility (attractiveness) of an e-truck [Dmnl]"""
        if t <= 0:
            res = self.INITIAL_UTILITY_FUNCTION + (self.Change_In_Utility) * self.model.dt
        else:
            res = self.utility_Function_of_Etruck(t - self.model.dt) + (self.Change_In_Utility) * self.model.dt
        return res

    @property
    def technology_Maturity_of_Etruck(self, t): #
        """"The level of advancement and development of electric truck technology, indicating how close it is to reaching its full potential and goals. [technology]"""
        if t <= 0:
            res = (self.Technology_Development_of_Etruck) * self.model.dt
        else:
            res = self.technology_Maturity_of_Etruck(t - self.model.dt) + (self.Technology_Development_of_Etruck) * self.model.dt
        return res

    @property
    def rD_Fund_of_Etrucks(self, t): #
        """Total funds available for electric trucks research and development. [SEK]"""
        if t <= 0:
            res = 1.6e+8 + (self.rD_Investment - self.rD_Spending) * self.model.dt
        else:
            res = self.rD_Fund_of_Etrucks(t - self.model.dt) + (self.rD_Investment - self.rD_Spending) * self.model.dt
        return res

    @property
    def gov_Tech_Maturity_Fund_Stock(self, t): #
        """The accumulation of public funds contributes to the technological maturity of electric trucks. [SEK]"""
        if t <= 0:
            res = (self.Annual_Gov_Tech_Maturity_Fund) * self.model.dt
        else:
            res = self.gov_Tech_Maturity_Fund_Stock(t - self.model.dt) + (self.Annual_Gov_Tech_Maturity_Fund) * self.model.dt
        return res


class vehicle_fleet_sector:
    # miscellaneous variables
    time_for_truck_sales = _ #! Var not assigned

    # vehicle_fleet sector static variables
    INITIAL_ETRUCK_FLEET_SIZE = 1
    """The starting number of electric trucks in the fleet [Vehicle]"""
    INITIAL_TOTAL_TRUCK_FLEET_SIZE = 83025
    """"The starting number of total trucks in the fleet [Vehicle]"""
    ETRUCK_LIFETIME = 12
    """The average operational lifespan of electric vehicles [Year]"""

    def __init__(self, model):
        self.model = model

    def Total_Truck_Sales(self):   
        """Number of new trucks (both electric and diesel) that are sold in each year [Vehicle/Year]"""
        return 148.556*self.time_for_truck_sales-292712
      
    def Total_Truck_Decommission(self):
        """Number of total trucks that are removed from use in each year [Vehicle/Year]"""
        return delay(self.Total_Truck_Sales, self.model.vehicle_cost.DIESEL_TRUCK_LIFETIME, self.INITIAL_TOTAL_TRUCK_FLEET_SIZE / self.model.vehicle_cost.DIESEL_TRUCK_LIFETIME)
        
    ##  
    @property
    def Etruck_Sales(self): #
        """Number of new electric trucks that are sold in each year [Vehicle/Year]"""
        return self.Total_Truck_Sales*self.model.utility_function.effect_of_utility_to_cost

    @property
    def Etruck_Decommission(self): #
        """Number of electric trucks that are removed from use in each year [Vehicle/Year]"""
        return delay(self.Etruck_Sales, self.ETRUCK_LIFETIME, self.INITIAL_ETRUCK_FLEET_SIZE / self.ETRUCK_LIFETIME) 

    @property
    def share_of_electric_truck_in_new_sales(self): #
        """The proportion of the total truck fleet that is sold to the market [Dmnl]"""
        return self.Etruck_Sales / self.Total_Truck_Sales
                
    # Time dependent variables - DIRECT
    @property 
    def share_of_electric_truck_in_total_fleet_size (self): #
        """The proportion of the total truck fleet that is electric [Dmnl]""" 
        return self.etruck_Fleet_Size(self.model.t) / self.total_Truck_Fleet_Size(self.model.t)

    # Time functions 
    @property   
    def etruck_Fleet_Size(self, t): #
        """The total number of electric trucks in the fleet [Vehicle]"""
        if t <= 0:
            res = self.INITIAL_ETRUCK_FLEET_SIZE + (self.Etruck_Sales - self.Etruck_Decommission) * self.model.dt
        else:
            res = self.etruck_Fleet_Size(t -self.model.dt) + (self.Etruck_Sales - self.Etruck_Decommission) * self.model.dt
        return res

    @property
    def total_Truck_Fleet_Size(self, t): #
        """The total number of trucks in the fleet [Vehicle]"""
        if t <= 0:
            res = self.INITIAL_TOTAL_TRUCK_FLEET_SIZE + (self.Total_Truck_Sales - self.Total_Truck_Decommission) * self.model.dt
        else:
            res = self.total_Truck_Fleet_Size(t - self.model.dt) + (self.Total_Truck_Sales - self.Total_Truck_Decommission) * self.model.dt
        return res
