# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO
import numpy as np

def delay(input, delay_time, initial_value):
    # Placeholder for delay function implementation
    pass

class emission_sector:
    # miscellaneous variables
    dt = _ #! Var not assigned
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

    def __init__(self):
        self.investment_on_charging_stations_sector = None #Completed during execution
        self.vehicle_cost_sector = None #Completed during execution
        self.utility_function_sector = None #Completed during execution
        self.charging_station_cost_and_profitability_sector = None #Completed during execution
        self.vehicle_fleet_sector = None #Completed during execution
        self.Total_annual_emission_from_trucks__tank_to_wheel = (self.Annual_operational_emission_from_etrucks+self.Annual_operational_emission_from_diesel_trucks)
        """[kgCO2eq/Year]"""
        self.Annual_Total_Gov_Funds = self.investment_on_charging_stations_sector.Annual_gov_subsidy_on_charging+self.vehicle_cost_sector.Annual_gov_subsidy_on_vehicle_purchase_cost+self.utility_function_sector.annual_gov_funding_for_improving_etruck_technology
        """[SEK/Year]"""
        self.Annual_Emission__with_having_etrucks = self.Total_annual_emission_from_trucks__tank_to_wheel
        """[kgCO2eq/Year]"""
        self.Annual_Emission__without_any_etrucks = self.total_annual_amount_of_energy*self.Carbon_intensity_of_diesel_fuel_by_considering_biofuel
        """[kgCO2eq/Year]"""
        self.Annual_Gov_Funding_by_Five_Levers = -(self.investment_on_charging_stations_sector.Annual_gov_subsidy_on_charging+self.vehicle_cost_sector.Annual_gov_subsidy_on_vehicle_purchase_cost+self.utility_function_sector.annual_gov_funding_for_improving_etruck_technology+self.charging_station_cost_and_profitability_sector.annual_gov_fund_on_EL_price+self.vehicle_cost_sector.Annual_Gov_Fund_on_Diesel_Price)
        """[SEK/Year]"""
        self.Annual_carbon_cost = self.Total_annual_emission_from_trucks__tank_to_wheel*self.CARBON_SOCIETY_COST
        """[SEK/Year]"""
        self.annual_fuel_consumption__kWh__per_diesel_truck = self.vehicle_cost_sector.annual_fuel_consumption__Litr__per_diesel_truck*self.Kwh_to_Litre_converter
        """[kWh/(Vehicle*Year)]"""
        self.annual_fuel_consumption__kWh__for_diesel_fleet = self.annual_fuel_consumption__kWh__per_diesel_truck*self.vehicle_cost_sector.Diesel_Truck_Fleet_Size
        """[kWh/Year]"""
        self.Annual_operational_emission_from_diesel_trucks = self.annual_fuel_consumption__kWh__for_diesel_fleet*self.Carbon_intensity_of_diesel_fuel_by_considering_biofuel*self.factor_for_correction_emission
        """[kgCO2eq/Year]"""
        self.Annual_operational_emission_from_etrucks = self.charging_station_cost_and_profitability_sector.charging_consumption_per_etruck_per_year*self.vehicle_fleet_sector.Etruck_Fleet_Size(0)*self.Carbon_intensity_of_electricity__fuel #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[kgCO2eq/Year]"""
        self.emission_reduction_based_on_previous_regulation = min(1, (1.7606*self.time_for_emission_reduction-3534.5)/100 if (self.time_for_emission_reduction <= 2021) else (4.4667*self.time_for_emission_reduction-9000.5)/100 )
        """[Dmnl]"""
        self.emission_reduction_based_on_new_regulation = self.emission_reduction_based_on_new_regulation_func(self.time_for_emission_reduction)
        """[Dmnl]"""
        self.Biofuel_share = min(1, self.emission_reduction_based_on_previous_regulation/(1-self.Carbon_intensity_of_biofuel/self.Carbon_intensity_of_diesel)) if self.SWICH_FOR_NEW_REGULATION_EFFECT == 0 else min(1, self.emission_reduction_based_on_new_regulation/(1-self.Carbon_intensity_of_biofuel/self.Carbon_intensity_of_diesel)) 
        """[Dmnl]"""
        self.Carbon_intensity_of_diesel_fuel_by_considering_biofuel = (self.Biofuel_share*self.Carbon_intensity_of_biofuel+(1-self.Biofuel_share)*self.Carbon_intensity_of_diesel)/self.Kwh_to_Litre_converter
        """[kgCO2eq/kWh]"""
        self.Emission_per_kwh__annually = self.Total_annual_emission_from_trucks__tank_to_wheel/self.total_annual_amount_of_energy
        """[kgCO2eq/kWh]"""
        self.Gov_total_fund_per_vehicle = self.total_Gov_Funds(0)/self.vehicle_fleet_sector.etruck_Fleet_Size(0) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[SEK/Vehicle]"""
        self.Saving_emission_by_transit_to_electrification = self.cumulative_Emission_without_any_etrucks(0)-self.cumulative_Emission_with_having_etrucks(0) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[kgCO2eq]"""
        self.Saving_emission_converted_to_money_due_to_electrification = self.Saving_emission_by_transit_to_electrification*self.CARBON_SOCIETY_COST
        """[SEK]"""
        self.Monetarized_saving_emissions_per_investment_unit_in_electrification = self.Saving_emission_converted_to_money_due_to_electrification/self.Total_Gov_Funds
        """[Dmnl]"""
        self.Share_of_diesel_truck_in_total_fleet_size = self.vehicle_cost_sector.Diesel_Truck_Fleet_Size/self.vehicle_fleet_sector.total_Truck_Fleet_Size(0) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[Dmnl]"""
        self.total_annual_amount_of_energy = self.vehicle_cost_sector.Diesel_Truck_Fleet_Size*self.annual_fuel_consumption__kWh__per_diesel_truck+self.vehicle_fleet_sector.etruck_Fleet_Size(0)*self.charging_station_cost_and_profitability_sector.charging_consumption_per_etruck_per_year #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[kWh/Year]"""

    def emission_reduction_based_on_new_regulation_func(self, time_for_emission_reduction):
        if (time_for_emission_reduction >= 2024): 
            return 0.06 
        elif ((time_for_emission_reduction == 2022) or (time_for_emission_reduction == 2023)):
            return 0.305 
        else: 
            return (1.7606*time_for_emission_reduction-3534.5)/100

    # Time functions
    def government_Fund_Balance_by_Five_Levers(self, t):
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_Gov_Funding_by_Five_Levers) * self.dt
        else:
            res = self.government_Fund_Balance_by_Five_Levers(t - self.dt) + (self.Annual_Gov_Funding_by_Five_Levers) * self.dt
        return res

    def cumulative_Emission_without_any_etrucks(self, t):
        """small initial value near to zero [kgCO2eq]"""
        if t <= 0:
            res = 10^-9 + (self.Annual_Emission__without_any_etrucks) * self.dt
        else:
            res = self.cumulative_Emission_without_any_etrucks(t - self.dt) + (self.Annual_Emission__without_any_etrucks) * self.dt
        return res

    def cumulative_Emission_with_having_etrucks(self, t):
        """small initial value near to zero [kgCO2eq]"""
        if t <= 0:
            res = 10^-9 + (self.Annual_Emission__with_having_etrucks) * self.dt
        else:
            res = self.cumulative_Emission_with_having_etrucks(t - self.dt) + (self.Annual_Emission__with_having_etrucks) * self.dt
        return res

    def total_Gov_Funds(self, t):
        """small initial value near to zero [SEK]"""
        if t <= 0:
            res = 10^-9 + (self.Annual_Total_Gov_Funds) * self.dt
        else: 
            res = self.total_Gov_Funds(t - self.dt) + (self.Annual_Total_Gov_Funds) * self.dt
        return res


class charging_station_cost_and_profitability_sector:
    # miscellaneous variables
    time_for_price_of_electricity = _ #! Var not assigned
    OPERATIONAL_AND_MAINTENANCE_COST = _ #! Var not assigned
    dt = _ #! Var not assigned

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
    PRICE_OF_ELECTRICITY = (0.0415*time_for_price_of_electricity-83.286)*sensitivity_coefficient_for_EL
    """[SEK/kWh]"""
    Ancillary_revenue = 0
    """[SEK/(Charging stations*Year)]"""
    AVERAGE_CONSUMPTION_PER_KM_FOR_ETRUCK = 1.5
    """[kWh/KM]"""
    AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR = 90000
    """[KM/(Vehicle*Year)]"""
    MARGIN_OF_CHARGING_PROVIDERS_FOR_ELECTRICITY_PRICE = 0.2
    """Based on interviews [Dmnl]"""
    charging_consumption_per_etruck_per_year = AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR*AVERAGE_CONSUMPTION_PER_KM_FOR_ETRUCK
    """[kWh/(Vehicle*Year)]"""
    DISCOUNT_RATE = 0.1
    """[Dmnl]"""
    r__common_ratio_in_geometric_series = (1/(1+DISCOUNT_RATE))
    """[Dmnl]"""
    MAX_NOMINAL_CAPACITY_OF_A_STATION_PER_YEAR = 350*8760
    """Charger Power (kw/station)* 8760 hour/year [kWh/(Year*Charging stations)]"""
    operational_AND_maintenance_cost_of_a_station__based_on_percentage_of_capex = 0.05*CONSTRUCTION_COST_PER_STATION
    """The annual cost of operating and maintaining a charging station [SEK/(Charging stations*Year)]"""

    def __init__(self):
        self.charging_station_availability_sector = None #Completed during execution
        self.vehicle_fleet_sector = None #Completed during execution
        self.annual_gov_fund_on_EL_price = (0.0415*self.time_for_price_of_electricity-83.286)*self.charging_consumption_per_etruck_per_year*self.vehicle_fleet_sector.etruck_Fleet_Size(0)*(1-self.sensitivity_coefficient_for_EL) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """Positive amounts show that governments pay subsidies on EL; Negative amounts show that governments receive taxes on EL [SEK/Year]"""
        self.Annual_income_of_electricity__inflow = self.charging_consumption_per_etruck_per_year*self.vehicle_fleet_sector.etruck_Fleet_Size(0)*self.PRICE_OF_ELECTRICITY #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[SEK/Year]"""
        self.GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS = min(0.99, 0.7*(1-self.vehicle_fleet_sector.share_of_electric_truck_in_total_fleet_size)*self.sensitivity_coefficient_for_CHARGING_SUBSIDY)
        """Put a maximum to avoid to be more than 1! [Dmnl]"""
        self.construction_cost_per_station_paid_by_infra_providers = self.CONSTRUCTION_COST_PER_STATION*(1-self.GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS)
        """[SEK/Charging stations]"""
        self.annual_gov_subsidy_on_charging_2 = self.charging_station_availability_sector.Building_Charging_Station*self.CONSTRUCTION_COST_PER_STATION*self.GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS
        """[SEK/Year]"""
        self.Average_energy_demand_from_each_station_per_year = (self.charging_consumption_per_etruck_per_year*self.vehicle_fleet_sector.etruck_Fleet_Size(0))/max(10^-9, self.charging_station_availability_sector.installed_Charging_Stations(0)) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """to avoid being zero in the denominator [kWh/(Charging stations*Year)]"""
        self.Construction_cost_paid_by_infra_providers_per_station_per_year__discounted = self.construction_cost_per_station_paid_by_infra_providers/self.discount_factor_for_stations
        """[SEK/(Charging stations*Year)]"""
        self.CHARGE_RETAIL_PRICE = min((((self.Construction_cost_paid_by_infra_providers_per_station_per_year__discounted+self.operation_cost_per_station_per_year)/self.utilized_capacity_of_a_station_per_year)*(1+self.MARGIN_OF_CHARGING_PROVIDERS_FOR_ELECTRICITY_PRICE)), 5*self.PRICE_OF_ELECTRICITY)
        """a ceil of 5*price of EL is considered to control the model in extreme test. [SEK/kWh]"""
        self.Charging_station_Capacity_to_demand_ratio_percentage = self.charging_station_availability_sector.charging_station_capacity_to_demand_ratio*100
        """[Dmnl]"""
        self.cost_of_electricity_per_station_per_year = self.utilized_capacity_of_a_station_per_year*self.PRICE_OF_ELECTRICITY
        """[SEK/(Charging stations*Year)]"""
        self.operation_cost_per_station_per_year = (self.cost_of_electricity_per_station_per_year+self.OPERATIONAL_AND_MAINTENANCE_COST)
        """[SEK/(Charging stations*Year)]"""
        self.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks = GRAPH(self.vehicle_fleet_sector.share_of_electric_truck_in_total_fleet_size) Points: (0.000, 0.1000), (1.000, 0.7000) #! QUESTION: HOW TO REPRESENT THIS?
        """"min of 0.1; max of 0.7 Based on interviews and Anders Grauers course Grauers, A. (2023). Electromobility: a system perspective [Course]. Swedish Electromobility Centre, Chalmers University of Technology. [Dmnl]"""
        self.MAX_UTILIZATION_RATE_OF_A_STATION_percentage = self.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks*100
        """[Dmnl]"""
        self.utilization_rate_of_a_station = min(self.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks, self.Average_energy_demand_from_each_station_per_year/self.MAX_NOMINAL_CAPACITY_OF_A_STATION_PER_YEAR)
        """[Dmnl]"""
        self.utilized_capacity_of_a_station_per_year = self.MAX_NOMINAL_CAPACITY_OF_A_STATION_PER_YEAR*self.utilization_rate_of_a_station
        """[kWh/(Year*Charging stations)]"""
        self.sale_revenue = self.utilized_capacity_of_a_station_per_year*self.CHARGE_RETAIL_PRICE
        """[SEK/(Charging stations*Year)]"""
        self.revenue_per_station_per_year = self.sale_revenue+self.Ancillary_revenue
        """[SEK/(Charging stations*Year)]"""
        self.discount_factor_for_stations = (self.r__common_ratio_in_geometric_series*(1-self.r__common_ratio_in_geometric_series^(self.LIFETIME_OF_A_STATION/self.time_unit))/(1-self.r__common_ratio_in_geometric_series))*self.time_unit
        """Geometric series formula [Year]"""
        self.charging_station_profitability__Profitability_index_after_gov_subsidy = ((self.revenue_per_station_per_year-self.operation_cost_per_station_per_year)*self.discount_factor_for_stations)/self.construction_cost_per_station_paid_by_infra_providers
        """[Dmnl]"""
        self.maximum_available_capacity_of_a_station_per_year = self.MAX_NOMINAL_CAPACITY_OF_A_STATION_PER_YEAR*self.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks
        """[kWh/(Year*Charging stations)]"""
        self.Total_power_supply_by_all_charging_station_per_year = self.utilized_capacity_of_a_station_per_year*self.charging_station_availability_sector.installed_Charging_Stations(0) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[kWh/Year]"""
        self.Power_supply_per_etruck_per_year = self.Total_power_supply_by_all_charging_station_per_year/self.vehicle_fleet_sector.Etruck_Fleet_Size(0) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[kWh/(Year*Vehicle)]"""
        self.total_capacity_of_all_installed_station = self.maximum_available_capacity_of_a_station_per_year*self.charging_station_availability_sector.installed_Charging_Stations(0) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[kWh/Year]"""
        self.total_consumption_of_electric_fleet = self.charging_consumption_per_etruck_per_year*self.vehicle_fleet_sector.Etruck_Fleet_Size(0) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[kWh/Year]"""
        self.total_operational_cost_per_station__accumulated_over_lifetime_years = self.operation_cost_per_station_per_year*self.discount_factor_for_stations
        """[SEK/Charging stations]"""
        self.utilization_in_total = self.total_consumption_of_electric_fleet/self.total_capacity_of_all_installed_station
        """[Dmnl]"""
        self.utilization_in_total_percentage = self.utilization_in_total*100
        """[Dmnl]"""

    def income_of_electricity_stock(self, t):
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_income_of_electricity__inflow) * self.dt
        else:
            res = self.income_of_electricity_stock(t - self.dt) + (self.Annual_income_of_electricity__inflow) * self.dt
        return res

    def gov_fund_on_EL_price_stock(self, t):
        """[SEK]"""
        if t <= 0:
            res = (self.annual_gov_fund_on_EL_price) * self.dt
        else:
            res = self.gov_fund_on_EL_price_stock(t - self.dt) + (self.annual_gov_fund_on_EL_price) * self.dt
        return res
    
    def gov_Charging_subsidy_stock_2(self, t):
        """[SEK]"""
        if t <= 0:
            res = ("annual_gov._subsidy_on_charging_2") * self.dt
        else:
            res = self.gov_Charging_subsidy_stock_2(t - self.dt) + ("annual_gov._subsidy_on_charging_2") * self.dt
        return res


class investment_on_charging_stations_sector:
    # miscellaneous variables 
    TIME = _ #! Var not assigned
    dt = _ #! Var not assigned
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
    Goal_of_charging_stations_for_full_adoption_of_electric_trucks = SWEDEN_ROAD_LENGHT*IDEAL_DENSITY_OF_CHARGING_STATIONS_BASED_ON_EU_REGULATIONS
    """[Charging stations]"""
    goal_of_emission_level_in_2030 = EMISSION_LEVEL_IN_2010*(1-EMISSION_REDUCTION_GOAL_IN_2030)
    """[kgCO2eq/Year]"""
    goal_of_emission_level_in_2045 = EMISSION_LEVEL_IN_2010*(1-EMISSION_REDUCTION_GOAL_IN_2045)
    """[kgCO2eq/Year]"""

    def __init__(self):
        self.emission_sector = None #Completed during execution
        self.charging_station_cost_and_profitability_sector = None #Completed during execution
        self.vehicle_fleet_sector = None #Completed during execution
        self.charging_station_availability_sector = None #Completed during execution
        self.Actual_Private_Investment_in_Charging_Stations = (self.potential_Private_Investment_in_Charging_Stations(0)/self.TIME_TO_INVESTMENT_FOR_PRIVATE_SECTOR) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[SEK/year]"""
        self.Actual_Government_Investment_in_Charging_Stations =self.Actual_Private_Investment_in_Charging_Stations*self.ratio_of_gov_to_private_investment if (self.potential_Government_Investment_in_Charging_Stations(0) > 0) else 0 #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """if stock>0, public investment, otherwise 0 [SEK/year]"""
        self.Annual_gov_subsidy_on_charging = self.Actual_Government_Investment_in_Charging_Stations
        """[SEK/year]"""
        self.demand_of_charging_station = (self.vehicle_fleet_sector.Etruck_Fleet_Size*self.charging_station_cost_and_profitability_sector.charging_consumption_per_etruck_per_year)/self.charging_station_cost_and_profitability_sector.maximum_available_capacity_of_a_station_per_year
        """[Charging stations]"""
        self.future_demand_of_charging_station = (SMTH1(self.vehicle_fleet_sector.Etruck_Sales, self.timeframe_of_average)*self.charging_station_cost_and_profitability_sector.charging_consumption_per_etruck_per_year*self.planning_horizon_in_year)/self.charging_station_cost_and_profitability_sector.maximum_available_capacity_of_a_station_per_year #! QUESTION: Usage of SMTH1 function
        """We used "e-truck sales" because we wanted to add future growth of demand to current demand, so we calculated how many new trucks will need charging stations. [Charging stations]"""
        self.gap_of_number_of_charging_stations_based_on_regulation = self.Goal_of_charging_stations_for_full_adoption_of_electric_trucks-self.charging_station_availability_sector.installed_Charging_Stations(0) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[Charging stations]"""
        self.gov_portion_of_investment_per_station = self.charging_station_cost_and_profitability_sector.CONSTRUCTION_COST_PER_STATION*self.charging_station_cost_and_profitability_sector.GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS
        """[SEK/Charging stations]"""
        self.Addition_of_Government_Investment_in_Charging_Stations = 0 if (((self.TIME <= 2030) & (self.emission_sector.Total_annual_emission_from_trucks__tank_to_wheel <= self.goal_of_emission_level_in_2030)) or ((self.TIME <= 2045) & (self.emission_sector.Total_annual_emission_from_trucks__tank_to_wheel <= self.goal_of_emission_level_in_2045))) else ((self.gap_of_number_of_charging_stations_based_on_regulation*self.gov_portion_of_investment_per_station)-self.Potential_Government_Investment_in_Charging_Stations)/self.TIME_TO_CLOSE_GAP_FOR_GOV 
        """[SEK/Year]"""
        self.market_gap_for_charging_stations = max(0, self.demand_of_charging_station+(self.future_demand_of_charging_station*self.ON_OFF_SWITCH_for_considering_future_charging_demand)-self.charging_station_availability_sector.installed_Charging_Stations(0)) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[Charging stations]"""
        self.private_portion_of_investment_per_station = self.charging_station_cost_and_profitability_sector.CONSTRUCTION_COST_PER_STATION*(1-self.charging_station_cost_and_profitability_sector.GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS)
        """Capex*(1-alfa)+Opex [SEK/Charging stations]"""
        self.Addition_of_Private_Investment_in_Charging_Stations = (self.market_gap_for_charging_stations*self.private_portion_of_investment_per_station*self.look_up_profitability_index_to_private_investment)/self.TIME_TO_CLOSE_GAP_FOR_PRIVATE_SECTOR
        """[SEK/Year]"""
        self.ratio_of_gov_to_private_investment = self.gov_portion_of_investment_per_station/self.private_portion_of_investment_per_station
        """[Dmnl]"""
        self.emission_reduction_factor_compared_to_2010_level = 1+(self.emission_sector.Total_annual_emission_from_trucks__tank_to_wheel-self.EMISSION_LEVEL_IN_2010)/self.EMISSION_LEVEL_IN_2010
        """[Dmnl]"""
        self.Sensitivity_of_private_investors_to_profitability_index = GRAPH(self.charging_station_cost_and_profitability_sector.charging_station_profitability__Profitability_index_after_gov_subsidy) Points: (0.00, 0.000), (1.00, 0.000), (5.00, 1.000), (10.00, 1.000) #! QUESTION: HOW TO REPRESENT THIS?
        """"Based on interviews. The sensitivity of private investors to the profitability index/how important a high profitability index is for investment decisions. PI > 1: The project is profitable. PI = 1: The project breaks even. PI < 1: The project is not profitable, as the costs exceed the returns. In the base scenario, investor sensitivity is moderate. When the profitability index reaches 4, investors are likely to invest at maximum level. [Dmnl]"""

    def potential_Private_Investment_in_Charging_Stations(self, t):
        """[SEK]"""
        if t <= 0:
            res = self.INITIAL_POTENTIAL_PRIVATE_FUNDS + (self.Addition_of_Private_Investment_in_Charging_Stations - self.Deciding_not_to_invest__reluctance_to_invest - self.Actual_Private_Investment_in_Charging_Stations) * self.dt
        else:
            res = self.potential_Private_Investment_in_Charging_Stations(t - self.dt) + (self.Addition_of_Private_Investment_in_Charging_Stations - self.Deciding_not_to_invest__reluctance_to_invest - self.Actual_Private_Investment_in_Charging_Stations) * self.dt
        return res

    def potential_Government_Investment_in_Charging_Stations(self, t):
        """[SEK]"""
        if t <= 0:
            res = self.INITIAL_POTENTIAL_PUBLIC_FUNDS + (self.Addition_of_Government_Investment_in_Charging_Stations - self.Actual_Government_Investment_in_Charging_Stations) * self.dt
        else:
            res = self.potential_Government_Investment_in_Charging_Stations(t - self.dt) + (self.Addition_of_Government_Investment_in_Charging_Stations - self.Actual_Government_Investment_in_Charging_Stations) * self.dt
        return res

    def gov_Charging_subsidy_stock(self ,t):
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_gov_subsidy_on_charging) * self.dt
        else:
            res = self.gov_Charging_subsidy_stock(t - self.dt) + (self.Annual_gov_subsidy_on_charging) * self.dt
        return res


class charging_station_availability_sector:
    # miscellaneous variables
    dt = _ #! Var not assigned
    
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
        self.ratio_etruck_to_charging_station = self.vehicle_fleet_sector.Etruck_Fleet_Size/max(10**-9, self.installed_Charging_Stations(0)) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
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


class vehicle_cost_sector:
    # miscellaneous variables
    dt = _ #! Var not assigned
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
    DIESEL_RETAIL_PRICE = (0.286*time_for_diesel_price-562.16)*sensitivity_coefficient_for_DIESEL
    """"swedish diesel price energimyndigheten [SEK/Litre]"""
    PURCHASE_COST_OF_DIESEL_TRUCK = 1.76E+06
    """EV: 5,513,100 SEK/vehicle Diesel: 1,759,500 SEK/vehicle EV: 470,000 EURO/vehicle Diesel: 150,000 EURO/vehicle EUR to SEK: 11.73 (14 May 2024) [SEK/Vehicle]"""
    LEARNING_EFFECT_DELAY = 2
    """Based on expert opinion [Year]"""
    AVERAGE_CONSUMPTION_PER_KM_FOR_DIESEL_TRUCK = 0.25
    """100 km, 27 litre ICCT report, table 1 page 9 = 0.27 [Litre/KM]"""
    cost_of_diesel_fuel_per_km = AVERAGE_CONSUMPTION_PER_KM_FOR_DIESEL_TRUCK*DIESEL_RETAIL_PRICE
    """[SEK/KM]"""

    def __init__(self):
        self.vehicle_fleet_sector = None #Completed during execution
        self.utility_function_sector = None #Completed during execution
        self.charging_station_cost_and_profitability_sector = None #Completed during execution
        self.emission_sector = None #Completed during execution
        self.DIESEL_RETAIL_PRICE__SEK_per_kWh = self.DIESEL_RETAIL_PRICE/self.emission_sector.Kwh_to_Litre_converter
        """[SEK/kWh]"""
        self.annual_fuel_consumption__Litr__per_diesel_truck = self.charging_station_cost_and_profitability_sector.AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR*self.AVERAGE_CONSUMPTION_PER_KM_FOR_DIESEL_TRUCK
        """[Litre/(Vehicle*Year)]"""
        self.Diesel_Truck_Fleet_Size = self.vehicle_fleet_sector.total_Truck_Fleet_Size(0)-self.vehicle_fleet_sector.etruck_Fleet_Size(0) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[Vehicle]"""
        self.Annual_Gov_Fund_on_Diesel_Price = (0.286*self.time_for_diesel_price-562.16)*self.annual_fuel_consumption__Litr__per_diesel_truck*self.Diesel_Truck_Fleet_Size*(1-self.sensitivity_coefficient_for_DIESEL)
        """Positive amounts show that governments pay subsidies on DIESEL Negative amounts show that governments receive taxes on DIESEL"""
        self.Annual_Income_of_Diesel__inflow = self.annual_fuel_consumption__Litr__per_diesel_truck*self.Diesel_Truck_Fleet_Size*self.DIESEL_RETAIL_PRICE
        """[SEK/Year]"""
        self.purchase_cost_gap = self.purchase_Cost_of_Etrucks(0)-self.PURCHASE_COST_OF_DIESEL_TRUCK #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[SEK/Vehicle]"""
        self.Decrease_in_purchase_cost_of_etruck = self.utility_function_sector.ratio_of_technology_maturity_to_goal*self.purchase_cost_gap/self.LEARNING_EFFECT_DELAY
        """[SEK/(Year*Vehicle)]"""
        self.GOV_SUBSIDY_PERCENTAGE_ON_DIFFERENCE_BETWEEN_ETRUCK_AND_DIESEL_TRUCK_PURCHASE_COSTS = 0.4*(1-self.vehicle_fleet_sector.share_of_electric_truck_in_total_fleet_size)*self.sensitivity_coefficient_for_VEHICLE_SUBSIDY
        """Klimatklivet:Funding 40% of the additional cost compared to a similar conventional truck. [Dmnl]"""
        self.Annual_gov_subsidy_on_vehicle_purchase_cost = self.GOV_SUBSIDY_PERCENTAGE_ON_DIFFERENCE_BETWEEN_ETRUCK_AND_DIESEL_TRUCK_PURCHASE_COSTS*(self.purchase_Cost_of_Etrucks(0)-self.PURCHASE_COST_OF_DIESEL_TRUCK)*self.vehicle_fleet_sector.Etruck_Sales #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """[SEK/Year]"""
        self.annual_operation_cost__Opex__of_each_diesel_truck = (self.cost_of_diesel_fuel_per_km+self.MAINTENANCE_COST_PER_KM_FOR_DIESEL_TRUCK)*self.charging_station_cost_and_profitability_sector.AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR
        """[SEK/(Vehicle*Year)]"""
        self.cost_of_electricity_per_km = self.charging_station_cost_and_profitability_sector.AVERAGE_CONSUMPTION_PER_KM_FOR_ETRUCK*self.charging_station_cost_and_profitability_sector.CHARGE_RETAIL_PRICE
        """[SEK/KM]"""
        self.annual_operation_cost__opex__of_each_etruck = (self.cost_of_electricity_per_km+self.MAINTENANCE_COST_PER_KM_FOR_ETRUCK)*self.charging_station_cost_and_profitability_sector.AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR
        """[SEK/(Vehicle*Year)]"""
        self.discount_factor_for_diesel_truck = self.charging_station_cost_and_profitability_sector.r__common_ratio_in_geometric_series*(1-self.charging_station_cost_and_profitability_sector.r__common_ratio_in_geometric_series^(self.DIESEL_TRUCK_LIFETIME/self.charging_station_cost_and_profitability_sector.time_unit))/(1-self.charging_station_cost_and_profitability_sector.r__common_ratio_in_geometric_series)*self.charging_station_cost_and_profitability_sector.time_unit
        """[Year]"""
        self.diesel_truck_discounted_total_opex = self.annual_operation_cost__Opex__of_each_diesel_truck*self.discount_factor_for_diesel_truck
        """[SEK/Vehicle]"""
        self.diesel_truck_total_cost = self.PURCHASE_COST_OF_DIESEL_TRUCK+self.diesel_truck_discounted_total_opex
        """[SEK/Vehicle]"""
        self.discount_factor_for_etruck = self.charging_station_cost_and_profitability_sector.r__common_ratio_in_geometric_series*(1-self.charging_station_cost_and_profitability_sector.r__common_ratio_in_geometric_series^(self.vehicle_fleet_sector.ETRUCK_LIFETIME/self.charging_station_cost_and_profitability_sector.time_unit))/(1-self.charging_station_cost_and_profitability_sector.r__common_ratio_in_geometric_series)*self.charging_station_cost_and_profitability_sector.time_unit
        """[Year]"""
        self.etruck_discounted_total_Opex = self.annual_operation_cost__opex__of_each_etruck*self.discount_factor_for_etruck
        """[SEK/Vehicle]"""
        self.purchase_cost_paid_by_freight_companies = self.purchase_Cost_of_Etrucks(0)-(self.GOV_SUBSIDY_PERCENTAGE_ON_DIFFERENCE_BETWEEN_ETRUCK_AND_DIESEL_TRUCK_PURCHASE_COSTS*(self.purchase_Cost_of_Etrucks(0)-self.PURCHASE_COST_OF_DIESEL_TRUCK)) #! QUESTION: SHOULD THIS FUNCTION DEPEND ON TIME?
        """Price e-truck - Subsidy percentage* (Diffference between electric and regular) [SEK/Vehicle]"""
        self.electric_truck_total_cost = (self.purchase_cost_paid_by_freight_companies+self.etruck_discounted_total_Opex)
        """[SEK/Vehicle]"""

    def purchase_Cost_of_Etrucks(self, t):
        """EV: 5,513,100 SEK/vehicle Diesel: 1,759,500 SEK/vehicle EV: 470,000 EURO/vehicle Diesel: 150,000 EURO/vehicle EUR to SEK: 11.73 (14 May 2024) [SEK/Vehicle]"""
        if t <= 0:
            res = 5.5131e+06 + ( - self.Decrease_in_purchase_cost_of_etruck) * self.dt
        else:
            res = self.purchase_Cost_of_Etrucks(t - self.dt) + ( - self.Decrease_in_purchase_cost_of_etruck) * self.dt
        return res

    def income_of_Diesel__Stock(self, t):
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_Income_of_Diesel__inflow) * self.dt
        else: 
            res = self.income_of_Diesel__Stock(t - self.dt) + (self.Annual_Income_of_Diesel__inflow) * self.dt
        return res

    def gov_Fund_on_Diesel_Price(self, t):
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_Gov_Fund_on_Diesel_Price) * self.dt
        else:
            res = self.gov_Fund_on_Diesel_Price(t - self.dt) + (self.Annual_Gov_Fund_on_Diesel_Price) * self.dt
        return res

    def gov_vehicle_subsidy_stock(self, t):
        """[SEK]"""
        if t <= 0:
            res = (self.Annual_gov_subsidy_on_vehicle_purchase_cost) * self.dt
        else:
            res = self.gov_vehicle_subsidy_stock(t - self.dt) + (self.Annual_gov_subsidy_on_vehicle_purchase_cost) * self.dt
        return res


class utility_function_sector:
    # miscellaneous variables
    TIME = _ #! Var not assigned
    dt = _ #! Var not assigned

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
    # miscellaneous variables
    dt = _ #! Var not assigned
    time_for_truck_sales = _ #! Var not assigned

    # vehicle_fleet sector static variables
    INITIAL_ETRUCK_FLEET_SIZE = 1
    """The starting number of electric trucks in the fleet [Vehicle]"""
    INITIAL_TOTAL_TRUCK_FLEET_SIZE = 83025
    """"The starting number of total trucks in the fleet [Vehicle]"""
    ETRUCK_LIFETIME = 12
    """The average operational lifespan of electric vehicles [Year]"""
    Total_Truck_Sales = 148.556*time_for_truck_sales-292712
    """Number of new trucks (both electric and diesel) that are sold in each year [Vehicle/Year]"""

    def __init__(self):
        self.utility_function_sector = None #Completed during execution 
        self.vehicle_cost_sector = None #Completed during execution
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
