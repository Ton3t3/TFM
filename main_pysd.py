# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO
import pysd
import inspect
from pysd.py_backend.output import ModelOutput

class Model:
    def __init__(self, model):
        self.emission = emission_sector(model)
        self.vehicle_fleet = vehicle_fleet_sector(model)
        self.vehicle_cost = vehicle_cost_sector(model)
        self.utility_function = utility_function_sector(model)
        self.charg_cost_and_profitability = charging_station_cost_and_profitability_sector(model)
        self.charg_availability = charging_station_availability_sector(model)
        self.investment_on_stations = investment_on_charging_stations_sector(model)
        self.model = model.components


    @property
    def t(self):
        return self.model.time()
    
    @property    
    def t0(self):
        return self.model.initial_time()
    
    @property
    def tf(self):
        return self.model.final_time()
    
    @property
    def dt(self):
        return self.model.time_step() 


class emission_sector:
    #emission sector static variables
    DEFAULT = {
        "swich_for_new_regulation_effect" : 1, 
        #[Dmnl]
        "carbon_intensity_of_biofuel" : 361/1000, 
        #[kgCO2eq/Litre]
        "carbon_intensity_of_diesel" : 3424/1000, 
        #[kgCO2eq/Litre]
        "carbon_intensity_of_electricity_fuel" : 0, 
        #driving carbon intensity equal to zero [kgCO2eq/kWh]
        "factor_for_correction_emission" : 0.612, 
        #Based on discussion with SCB (Statistikmyndigheten) experts
        "kwh_to_litre_converter" : 9.8 
        #Energy content in kWh per liter of diesel fuel Energy content in MJ per liter: 36 MJ Conversion factor: 1 MJ = 0.277778 kWh [kWh/Litre]
    }

    STOCK_DEFAULTS = {
        "_integ_governmnet_fund_balance_by_five_levers" : 0,
        "_integ_cumulative_emission_without_any_etrucks" : 10^-9,
        "_integ_cumulative_emission_with_having_etrucks" : 10^-9,
        "_integ_total_gov_funds" : 10^-9
    }

    def __init__(self, model):
        self.model = model.components

    ##
    def time_for_carbon_cost(self):
        return self.model.time_for_carbon_cost()
    
    def time_for_emission_reduction(self):
        return self.model.time_for_emission_reduction()
        
    def CARBON_SOCIETY_COST(self):
        """[SEK/kgCO2eq]"""
        return self.model.carbon_society_cost()

    def annual_fuel_consumption__kWh__per_diesel_truck(self):
        """[kWh/(Vehicle*Year)]"""
        return self.model.annual_fuel_consumption_kwh_per_diesel_truck()
    
    def emission_reduction_based_on_previous_regulation(self):
        """[Dmnl]"""
        return self.model.emission_reduction_based_on_previous_regulation()
    
    def emission_reduction_based_on_new_regulation(self):
        """[Dmnl]"""
        return self.model.emission_reduction_based_on_new_regulation()
    
    def Biofuel_share(self):
        """[Dmnl]"""
        return self.model.biofuel_share()
    
    def Carbon_intensity_of_diesel_fuel_by_considering_biofuel(self):
        """[kgCO2eq/kWh]"""
        return self.model.carbon_intensity_of_diesel_fuel_by_considering_biofuel()
    
    ## DEPENDANT ON TIME - INDIRECT
    def annual_fuel_consumption__kWh__for_diesel_fleet(self): #
        """[kWh/Year]"""
        return self.model.annual_fuel_consumption_kwh_for_diesel_fleet()
    
    def Annual_operational_emission_from_diesel_trucks(self): #
        """[kgCO2eq/Year]"""
        return self.model.annual_operational_emission_from_diesel_trucks()
    
    def Total_annual_emission_from_trucks__tank_to_wheel(self): #
        """[kgCO2eq/Year]"""
        return (self.Annual_operational_emission_from_etrucks+self.Annual_operational_emission_from_diesel_trucks)
          
    def Annual_carbon_cost(self):
        """[SEK/Year]"""
        return self.model.annual_carbon_cost() 

    def Saving_emission_converted_to_money_due_to_electrification(self): #
        """[SEK]"""
        return self.model.saving_emission_converted_to_money_due_to_electrification()

    def Emission_per_kwh__annually(self): #
        """[kgCO2eq/kWh]"""
        return self.model.emission_per_kwh_annually()
    
    # DEPENDANT ON TIME - DIRECT
    def Saving_emission_by_transit_to_electrification(self): #
        """[kgCO2eq]"""
        return self.model.saving_emission_by_transit_to_electrification()
    
    def Annual_operational_emission_from_etrucks(self): #
        """[kgCO2eq/Year]"""
        return self.model.annual_operational_emission_from_etrucks()
    
    def Gov_total_fund_per_vehicle(self): #
        """[SEK/Vehicle]"""
        return self.model.gov_total_fund_per_vehicle()
     
    def total_annual_amount_of_energy(self): #
        """[kWh/Year]"""
        return self.model.total_annual_amount_of_energy()
    
    def Share_of_diesel_truck_in_total_fleet_size(self): #
        """[Dmnl]"""
        return self.model.share_of_diesel_truck_in_total_fleet_size()
    
    def Monetarized_saving_emissions_per_investment_unit_in_electrification(self): #
        """[Dmnl]"""
        return self.model.monetarized_saving_emissions_per_investment_unit_in_electrification()
    
    ## FLOWS
    # Inflows
    def Annual_Gov_Funding_by_Five_Levers(self): #
        """[SEK/Year]"""
        return self.model.annual_gov_funding_by_five_levers()

    def Annual_Emission__without_any_etrucks(self): #
        """[kgCO2eq/Year]"""
        return self.model.annual_emission_without_any_etrucks()

    def Annual_Emission__with_having_etrucks(self): #
        """[kgCO2eq/Year]"""
        return self.model.annual_emission_with_having_etrucks()

    def Annual_Total_Gov_Funds(self): #
        """[SEK/Year]"""
        return self.model.annual_total_gov_funds()
    
    ## STOCKS
    def government_Fund_Balance_by_Five_Levers(self): #
        """[SEK]"""
        return self.model._integ_governmnet_fund_balance_by_five_levers
    
    def cumulative_Emission_without_any_etrucks(self): #
        """small initial value near to zero [kgCO2eq]"""
        return self.model._integ_cumulative_emission_without_any_etrucks()
    
    def cumulative_Emission_with_having_etrucks(self): #
        """small initial value near to zero [kgCO2eq]"""
        return self.model._integ_cumulative_emission_with_having_etrucks()
    
    def total_Gov_Funds(self): #
        """small initial value near to zero [SEK]"""
        return self.model._integ_total_gov_funds()
    

class charging_station_cost_and_profitability_sector:
    # charging_station_cost_and_profitability sector static variables
    DEFAULT = {
        "time_unit" : 1, 
        #Formulation of the unit for IRR is complicated. Thus we used this vriable to fix unit left and hand right problem. It doesn't change the model [Year]
        "construction_cost_per_station" : 1.80E+06, 
        #Construction cost per kW [SEK/Charging stations]
        "lifetime_of_a_station" : 8, 
        #Based on interviews, EU report page 204, and REEL project report European Commission. (2021). Impact Assessment: Proposal for a Regulation of the European Parliament and of the Council on the deployment of alternative fuels infrastructure, and repealing Directive 2014/94/EU of the European Parliament and of the Council. REEL. (2022). Regional Electrified Logistics. [Year]
        "sensitivity_coefficient_for_charging_subsidy" : 1, 
        #[Dmnl]
        "sensitivity_coefficient_for_price_of_electricity" : 1, 
        #using only for sensitivity analysis [Dmnl]
        "ancillary_revenue" : 0, 
        #[SEK/(Charging stations*Year)]
        "average_consumption_per_km_for_etruck" : 1.5, 
        #[kWh/KM]
        "average_mileage_per_vehicle_per_year" : 90000, 
        #[KM/(Vehicle*Year)]
        "margin_of_charging_providers_for_electricity_price" : 0.2, #Based on interviews [Dmnl]
        "discount_rate" : 0.1, 
        #[Dmnl]
        "max_nominal_capacity_of_a_station_per_year" : 350*8760, 
        #Charger Power (kw/station)* 8760 hour/year [kWh/(Year*Charging stations)]
    }

    STOCK_DEFAULTS = {
        "_integ_income_of_electricity_stock" : 0,
        "_integ_gov_fund_on_el_price_stock" : 0,
        "_integ_gov_charging_subsidy_stock_2" : 0
    }
    
    def __init__(self, model):
        self.model = model.components

    ##
    def time_for_price_of_electricity(self):
        return self.model.time_for_price_of_electricity()

    def PRICE_OF_ELECTRICITY(self):
        """[SEK/kWh]"""
        return self.model.price_of_electricity()

    def charging_consumption_per_etruck_per_year(self):
        """[kWh/(Vehicle*Year)]"""
        return self.model.price_of_electricity()
    
    def r__common_ratio_in_geometric_series(self):
        """[Dmnl]""" 
        return self.model.r_common_ratio_in_geometric_series()
        
    def operational_AND_maintenance_cost_of_a_station__based_on_percentage_of_capex(self):
        """The annual cost of operating and maintaining a charging station [SEK/(Charging stations*Year)]"""
        return self.model.operational_maintenance_cost_of_a_station_based_on_percentage_of_capex()
        
    def discount_factor_for_stations(self):
        """Geometric series formula [Year]"""
        return self.model.discount_factor_for_stations()
    
    ##
    def MAX_UTILIZATION_RATE_OF_A_STATION_percentage(self): #
        """[Dmnl]"""
        return self.model.max_possible_utilization_rate_of_a_stationpercentage()
    
    def maximum_available_capacity_of_a_station_per_year(self): #
        """[kWh/(Year*Charging stations)]"""
        return self.model.maximum_available_capacity_of_a_station_per_year()
    
    def construction_cost_per_station_paid_by_infra_providers(self):#
        """[SEK/Charging stations]"""
        return self.model.construction_cost_per_station_paid_by_infra_providers()
    
    def Construction_cost_paid_by_infra_providers_per_station_per_year__discounted(self): #
        """[SEK/(Charging stations*Year)]"""
        return self.model.construction_cost_paid_by_infra_providers_per_station_per_year_discounted()
    
    def CHARGE_RETAIL_PRICE(self): #
        """a ceil of 5*price of EL is considered to control the model in extreme test. [SEK/kWh]"""
        return self.model.charge_retail_price()

    def sale_revenue(self): #
        """[SEK/(Charging stations*Year)]"""
        return self.model.sale_revenue()
    
    def revenue_per_station_per_year(self): #
        """[SEK/(Charging stations*Year)]"""
        return self.model.revenue_per_station_per_year()
    
    def charging_station_profitability__Profitability_index_after_gov_subsidy(self): #
        """[Dmnl]"""
        return self.model.charging_station_profitability_index()
                
    def utilization_in_total(self): #
        """[Dmnl]"""
        return self.model.utilization_in_total()
    
    def utilization_in_total_percentage(self): #
        """[Dmnl]"""
        return self.utilization_in_total*100
            
    def utilization_rate_of_a_station(self): #
        """[Dmnl]"""
        return self.model.utilization_in_totalpercentage()

    def utilized_capacity_of_a_station_per_year(self): #
        """[kWh/(Year*Charging stations)]"""
        return self.model.utilized_capacity_of_a_station_per_year()
    
    def cost_of_electricity_per_station_per_year(self): #
        """[SEK/(Charging stations*Year)]"""
        return self.model.cost_of_electricity_per_station_per_year()

    def operation_cost_per_station_per_year(self): #
        """[SEK/(Charging stations*Year)]"""
        return self.model.operation_cost_per_station_per_year()
    
    def total_operational_cost_per_station__accumulated_over_lifetime_years(self): #
        """[SEK/Charging stations]"""
        return self.model.total_operational_cost_per_station_accumulated_over_lifetime_years()

    def GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS(self): #
        """Put a maximum to avoid to be more than 1! [Dmnl]"""
        return self.model.gov_subsidy_percentage_on_construction_cost_of_charging_stations()
    
    def max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks(self): #
        """"min of 0.1; max of 0.7 Based on interviews and Anders Grauers course Grauers, A. (2023). Electromobility: a system perspective [Course]. Swedish Electromobility Centre, Chalmers University of Technology. [Dmnl]"""
        # GRAPH(self.model.vehicle_fleet.share_of_electric_truck_in_total_fleet_size) Points: (0.000, 0.1000), (1.000, 0.7000)
        return self.model.max_possible_utilization_rate_of_a_station_lookup_number_of_etrucks()
    
    def Charging_station_Capacity_to_demand_ratio_percentage(self): #
        """[Dmnl]"""
        return self.model.charg_availability.charging_station_capacity_to_demand_ratio*100
                
    # Time dependent variables - DIRECT        
    def Average_energy_demand_from_each_station_per_year(self): #
        """to avoid being zero in the denominator [kWh/(Charging stations*Year)]"""
        return self.model.average_energy_demand_from_each_station_per_year()

    def Power_supply_per_etruck_per_year(self): #
        """[kWh/(Year*Vehicle)]"""
        return self.model.power_supply_per_etruck_per_year()
    
    def total_consumption_of_electric_fleet(self): #
        """[kWh/Year]"""
        return self.model.total_consumption_of_electric_fleet()
    
    def Total_power_supply_by_all_charging_station_per_year(self): #
        """[kWh/Year]"""
        return self.model.total_power_supply_by_all_charging_station_per_year()
    
    def total_capacity_of_all_installed_station(self): #
        """[kWh/Year]"""
        return self.model.total_capacity_of_all_installed_station()
    
    ## FLOWS
    # Inflows
    def Annual_income_of_electricity__inflow(self): #
        """[SEK/Year]"""
        return self.model.annual_income_of_electricity_inflow()
    
    def annual_gov_fund_on_EL_price(self): #
        """Positive amounts show that governments pay subsidies on EL; Negative amounts show that governments receive taxes on EL [SEK/Year]"""
        return self.model.annual_gov_fund_on_el_price()
    
    def annual_gov_subsidy_on_charging_2(self): #
        """[SEK/Year]"""
        return self.model.annual_gov_subsidy_on_charging_2()
    
    ## STOCKS
    def income_of_electricity_stock(self): #
        """[SEK]"""
        return self.model._integ_income_of_electricity_stock()
    
    def gov_fund_on_EL_price_stock(self): #
        """[SEK]"""
        return self.model._integ_gov_fund_on_el_price_stock()
    
    def gov_Charging_subsidy_stock_2(self): #
        """[SEK]"""
        return self.model._integ_gov_charging_subsidy_stock_2()

    
class investment_on_charging_stations_sector:
    # investment_on_charging_stations sector static variables
    DEFAULT = {
        "reluctance_to_invest_rate" : 0,
        #"""Percentage of investors that decide not to invest in the charging infrastructure even after all assessments. They are between 0 to 5 percent random number RANDOM NORMAL(0, 0.05 , 0 , 1 , 0 ) [1/Year]"""
        "time_to_investment_for_private_sector" : 1,
        # """Based on expert opinion [Year]"""
        "time_to_close_gap_for_gov" : 4,
        # """Based on interview and inspired by the time distance between elections [Year]"""
        "time_to_close_gap_for_private_sector" : 1,
        # """Based on expert opinion [Year]"""
        "emission_level_in_2010" : 4.73E+09,
        # """[kgCO2eq/Year]"""
        "emission_reduction_goal_in_2030" : 0.7,
        # """[Dmnl]"""
        "emission_reduction_goal_in_2045" : 1,
        # """[Dmnl]"""
        "sweden_road_lenght" : 579556,
        # """Road lenght: 579 556 [KM]"""
        "onoff_switch_for_considering_future_charging_demand" : 1,
        # """[Dmnl]"""
        "planning_horizon" : 5,
        # """How many years we want to consider as future demand and bring it into our calculation. We calculated the average of three previous years and crossed it over to the planning horizon (5 years) to calculate the total demand for the three coming years. [Year]"""
        "timeframe_of_average" : 3,
        # """The average e-truck sales over a historical period (TIMEFRAME_OF_AVERAGE) are used to estimate the demand for a future time horizon (PLANNING_HORIZON). Thus, by analysing past sales trends, we can forecast potential demand for the upcoming period. [Year]"""
        "ideal_density_of_charging_stations_based_on_eu_regulations" : 0.02,
        # """"1 station for every 50 km. Based on interviews and Masterplan ACEA. (2022). [Charging stations/KM]"""
        # INITIAL
        "initial_potential_private_fund" : 1.00E+06,
        # [SEK]
        "initial_potential_public_fund" : 1.65E+06
        # according to the klimatklivet data: 1,648,000 kr [SEK]
    }

    STOCK_DEFAULTS = {
        "_integ_gov_charging_subsidy_stock" : 0
    }

    def __init__(self, model):
        self.model = model.components
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
    def emission_reduction_factor_compared_to_2010_level(self): #
        """[Dmnl]"""
        return self.model.emission_reduction_factor_compared_to_2010_level()

    def Sensitivity_of_private_investors_to_profitability_index(self): #
        """"Based on interviews. The sensitivity of private investors to the profitability index/how important a high profitability index is for investment decisions. PI > 1: The project is profitable. PI = 1: The project breaks even. PI < 1: The project is not profitable, as the costs exceed the returns. In the base scenario, investor sensitivity is moderate. When the profitability index reaches 4, investors are likely to invest at maximum level. [Dmnl]"""
        # GRAPH(self.model.charg_cost_and_profitability.charging_station_profitability__Profitability_index_after_gov_subsidy) Points: (0.00, 0.000), (1.00, 0.000), (5.00, 1.000), (10.00, 1.000)
        return self.model.sensitivity_of_private_investors_to_profitability_index()

    def gov_portion_of_investment_per_station(self): #
        """[SEK/Charging stations]"""
        return self.model.gov_portion_of_investment_per_station()
    
    def private_portion_of_investment_per_station(self): #
        """Capex*(1-alfa)+Opex [SEK/Charging stations]"""
        return self.model.private_portion_of_investment_per_station()
    
    def ratio_of_gov_to_private_investment(self): #
        """[Dmnl]"""
        return self.model.ratio_of_gov_to_private_investment()
                          
    def future_demand_of_charging_station(self): #
        """We used "e-truck sales" because we wanted to add future growth of demand to current demand, so we calculated how many new trucks will need charging stations. [Charging stations]"""
        return self.model._smooth_future_demand_of_charging_stations 

    #Time dependent variables - DIRECT                 
    def gap_of_number_of_charging_stations_based_on_regulation(self): #
        """[Charging stations]"""
        return self.model.gap_of_number_of_charging_stations_based_on_regulation()

    def demand_of_charging_station(self): #
        """[Charging stations]"""
        return self.model.demand_of_charging_station()
    
    def market_gap_for_charging_stations(self): #
        """[Charging stations]"""
        return self.model.market_gap_for_charging_stations()
    
    ## FLOWS
    # Inflows
    def Addition_of_Private_Investment_in_Charging_Stations(self): #
        """[SEK/Year]"""
        # return (self.market_gap_for_charging_stations*self.private_portion_of_investment_per_station*self.look_up_profitability_index_to_private_investment)/self.TIME_TO_CLOSE_GAP_FOR_PRIVATE_SECTOR
        return self.model.addition_of_government_investment_in_charging_stations()
    
    def Addition_of_Government_Investment_in_Charging_Stations(self): #
        """[SEK/Year]"""
        return self.model.addition_of_government_investment_in_charging_stations()
    
    def Annual_gov_subsidy_on_charging(self): #
        """[SEK/year]"""
        return self.model.annual_gov_subsidy_on_charging()
    
    # Outflows
    def Actual_Private_Investment_in_Charging_Stations(self): #
        """[SEK/year]"""
        return self.model.actual_private_investment_in_charging_stations()

    def Deciding_not_to_invest__reluctance_to_invest(self):
        """This could be reluctance in investing in electric charging station and we can go for other refueling option instead (like hydogen, biofuel), based on the comment by Astrid in SD transport SIG [SEK/Year]"""
        return self.model.deciding_not_to_invest_reluctance_to_invest()

    def Actual_Government_Investment_in_Charging_Stations(self): #
        """if stock>0, public investment, otherwise 0 [SEK/year]"""
        return self.model.actual_government_investment_in_charging_stations()
    
    ## STOCKS
    def potential_Private_Investment_in_Charging_Stations(self): #
        """[SEK]"""
        return self.model._integ_potential_private_investment_in_charging_stations()
    
    def potential_Government_Investment_in_Charging_Stations(self): #
        """[SEK]"""
        return self.model._integ_potential_government_investment_in_charging_stations()
    
    def gov_Charging_subsidy_stock(self): #
        """[SEK]"""
        return self.model._integ_gov_charging_subsidy_stock()
    

class charging_station_availability_sector: 
    # charging_station_availability sector static variables
    DEFAULT = {
        "time_to_build_a_charging_station" : 2,
        #""""Based on interviews and REEL project report REEL. (2022). Regional Electrified Logistics. [Year]"""
        # INITIAL
        "initial_charging_stations_under_construction" : (3*90000*1.5)/(0.1*350*8760),
        # """There is a 3 truck difference between 2017 and 2018, and we calculated the demand for initial charging staions based on 350 KW chargers. [Charging stations]"""
        "initial_charging_stations" : (0.5*90000*1.5)/(0.1*350*8760)
        # """There is 1 truck in the year 2017, and we calculated the demand for initial charging staions based on 350 KW chargers. [Charging stations]"""    
    }

    STOCK_DEFAULTS = {}

    def __init__(self, model):
        self.model = model.components

    ##    
    def availability_of_charging_station(self): #
        """[Dmnl]"""
        return self.model.availability_of_charging_station()
     
    # Time dependent variables - DIRECT
    def charging_station_capacity_to_demand_ratio(self): #
        """[Dmnl]"""
        return self.model.charging_station_capacity_to_demand_ratio()
    
    def ratio_etruck_to_charging_station(self): #
        """[Vehicle/Charging stations]"""
        return self.model.ratio_etruck_to_charging_station()
    
    ## FLOWS
    # Infows
    def Building_Charging_Station(self): #
        """[Charging stations/Year]"""
        return self.model.building_charging_station()
    
    # In-betweenflows
    def Finishing_Charging_Station(self): #
        """[Charging stations/Year]"""
        return self.model.finishing_charging_station()
    
    # Outflows
    def Decaying_Charging_Station(self): #
        """[Charging stations/Year]"""
        return self.model._delayfixed_decaying_charging_station()        

    ## STOCKS
    def installed_Charging_Stations(self): #
        """[Charging stations]"""
        return self.model._integ_installed_charging_stations()

    def charging_Stations_under_construction(self): #
        """[Charging stations]"""
        return self.model._integ_charging_stations_under_construction()


class vehicle_cost_sector:
    # vehicle_cost sector static variables
    DEFAULT = {
        "maintenance_cost_per_km_for_diesel_truck" : 1.32*0,
        # """[SEK/KM]"""
        "maintenance_cost_per_km_for_etruck" : 0.99*0,
        # """[SEK/KM]"""
        "diesel_truck_lifetime" : 12,
        # """[Year]"""
        "sensitivity_coefficient_for_vehicle_subsidy" : 1,
        # """Only use for sensitivity analysis [Dmnl]"""
        "sensitivity_coefficient_for_diesel" : 1,
        # """Only use for sensitivity analysis [Dmnl]"""
        "purchase_cost_of_diesel_truck" : 1.76E+06,
        # """EV: 5,513,100 SEK/vehicle Diesel: 1,759,500 SEK/vehicle EV: 470,000 EURO/vehicle Diesel: 150,000 EURO/vehicle EUR to SEK: 11.73 (14 May 2024) [SEK/Vehicle]"""
        "learning_effect_delay" : 2,
        # """Based on expert opinion [Year]"""
        "average_consumption_per_km_for_diesel_truck" : 0.25,
        # """100 km, 27 litre ICCT report, table 1 page 9 = 0.27 [Litre/KM]"""
        # INITIAL
        "initial_purchase_cost_of_etrucks" : 5.5131e+06
    }

    STOCK_DEFAULTS = {
        "_integ_income_of_diesel_stock" : 0,
        "_integ_gov_fund_on_diesel_price" : 0,
        "_integ_gov_vehicle_subsidy_stock" : 0            
    }

    def __init__(self, model):
        self.model = model.components

    ##
    def time_for_diesel_price(self):
        return self.model.time_for_diesel_price()

    def DIESEL_RETAIL_PRICE(self):
        """"swedish diesel price energimyndigheten [SEK/Litre]"""
        return self.model.diesel_retail_price()
    
    def DIESEL_RETAIL_PRICE__SEK_per_kWh(self):
        """[SEK/kWh]"""
        return self.model.diesel_retail_price_sekkwh()

    ##
    def GOV_SUBSIDY_PERCENTAGE_ON_DIFFERENCE_BETWEEN_ETRUCK_AND_DIESEL_TRUCK_PURCHASE_COSTS(self): #
        """Klimatklivet:Funding 40% of the additional cost compared to a similar conventional truck. [Dmnl]"""
        return self.model.gov_subsidy_percentage_on_difference_between_etruck_diesel_truck_purchase_costs()
    ##
    def cost_of_diesel_fuel_per_km(self):
        """[SEK/KM]"""
        return self.model.cost_of_diesel_fuel_per_km()
    
    def annual_fuel_consumption__Litr__per_diesel_truck(self):
        """[Litre/(Vehicle*Year)]"""
        return self.model.annual_fuel_consumption_litr_per_diesel_truck()
    
    def annual_operation_cost__Opex__of_each_diesel_truck(self):
        """[SEK/(Vehicle*Year)]"""
        return self.model.annual_operation_cost_opex_of_each_diesel_truck()
    
    def discount_factor_for_diesel_truck(self):
        """[Year]"""
        return self.model.discount_factor_for_diesel_truck()
    
    def diesel_truck_discounted_total_opex(self):
        """[SEK/Vehicle]"""
        return self.model.diesel_truck_discounted_total_opex()
    
    def diesel_truck_total_cost(self):
        """[SEK/Vehicle]"""
        return self.model.diesel_truck_total_cost()
    
    def discount_factor_for_etruck(self):
        """[Year]"""
        return self.model.discount_factor_for_etruck()

    ##
    def cost_of_electricity_per_km(self): #
        """[SEK/KM]"""
        return self.model.cost_of_electricity_per_km()
    
    def annual_operation_cost__opex__of_each_etruck(self): #
        """[SEK/(Vehicle*Year)]"""
        return self.model.annual_operation_cost_opex_of_each_etruck()
    
    def etruck_discounted_total_Opex(self): #
        """[SEK/Vehicle]"""
        return self.model.etruck_discounted_total_opex()
                              
    #Time function dependant - DIRECT
    def purchase_cost_gap(self): #
        """[SEK/Vehicle]"""
        return self.model.purchase_cost_gap()
    
    def purchase_cost_paid_by_freight_companies(self): #
        """Price e-truck - Subsidy percentage* (Diffference between electric and regular) [SEK/Vehicle]"""
        return self.model.purchase_cost_paid_by_freight_companies()
    
    def electric_truck_total_cost(self): #
        """[SEK/Vehicle]"""
        return self.model.electric_truck_total_cost()
    
    ## FLOWS
    # Inflows
    def Annual_Income_of_Diesel__inflow(self): #
        """[SEK/Year]"""
        return self.model.annual_income_of_diesel_inflow()
    
    def Annual_Gov_Fund_on_Diesel_Price(self): #
        """Positive amounts show that governments pay subsidies on DIESEL Negative amounts show that governments receive taxes on DIESEL"""
        return self.model.annual_gov_fund_on_diesel_price()
    
    def Annual_gov_subsidy_on_vehicle_purchase_cost(self): #
        """[SEK/Year]"""
        return self.model.annual_gov_subsidy_on_vehicle_purchase_cost()

    # Outflows
    def Decrease_in_purchase_cost_of_etruck(self): #
        """[SEK/(Year*Vehicle)]"""
        return self.model.decrease_in_purchase_cost_of_etruck()

    # XTRA (Using two previous stocks)
    def Diesel_Truck_Fleet_Size(self): #
        """[Vehicle]"""
        return self.model.diesel_truck_fleet_size()
    
    ## STOCKS
    def purchase_Cost_of_Etrucks(self): #
        """EV: 5,513,100 SEK/vehicle Diesel: 1,759,500 SEK/vehicle EV: 470,000 EURO/vehicle Diesel: 150,000 EURO/vehicle EUR to SEK: 11.73 (14 May 2024) [SEK/Vehicle]"""
        return self.model._integ_purchase_cost_of_etrucks()
    
    def income_of_Diesel__Stock(self): #
        """[SEK]"""
        return self.model._integ_income_of_diesel_stock()
    
    def gov_Fund_on_Diesel_Price(self): #
        """[SEK]"""
        return self.model._integ_gov_fund_on_diesel_price()
    
    def gov_vehicle_subsidy_stock(self): #
        """[SEK]"""
        return self.model._integ_gov_vehicle_subsidy_stock()
    
class utility_function_sector:
    # utility_function sector static variables
    DEFAULT = {
        "time_to_perceived_utility" : 1,
        # """"The time it takes for users to recognize the benefits of adopting e-trucks. Base on expert estimation [Year]"""
        "time_to_spend_rd_funds" : 3, #WHITE
        # """"The duration over which research and development funds are spent. Based on interviews [Year]"""
        "technology_improvement_per_sek_spent" : 1/(7.5*10**9),
        # """Based on interviews: 10 times the annual R&D budget - considering that the technology will be mature in 10 years. We summed the R&D investment from 2017 until 10 years. Maximum value for this variable, if we want to introduce "more" delay, then we decrease this further. [technology/SEK]"""
        "factor_of_gov_investment_on_the_tech_maturity" : 1,
        # """"magnitude of the impact of government investment on improving e-truck technology maturity.Base scenario value [Dmnl]"""
        "goal_of_technology_maturity_fund" : 1, #WHITE
        # """maximum level of technology maturity [technology]"""
        "mistrust_effect" : 0.02,
        # """"The percentage of awareness lost due to mistrust between freight companies. Based on the expert interview, we should consider a percentage of awareness that is ruined during the adoption. [Dmnl]"""
        "based_utility_for_diesel_truck" : 100,
        # """"The level of utility (attractiveness) of an d-truck. Based on the expert interview [Dmnl]"""
        "weight_of_availability" : 0.45,
        # """"this variable represents the weight of the availability of infrastructure influence on the e-truck utility, in comparison with the other influences. Based on the expert interview [Dmnl]"""
        "weight_of_awareness" : 0.4,
        # """"this variable represents the weight of the awareness influence on the e-truck utility, in comparison with the other influences. Based on the expert interview [Dmnl]"""
        "weight_of_maturity" : 0.15,
        # """"this variable represents the weight of the vehicle technology maturity influence on the e-truck utility, in comparison with the other influences. Based on the expert interview [Dmnl]"""
        # INITIAL
        "initial_utility_function" : 0.2
        # """"initial value for utility function of e-trucks. Base on expert estimation [Dmnl]"""        
    }

    STOCK_DEFAULTS = {
        "_integ_technology_maturity_of_etruck" : 0,
        "_integ_rd_fund_of_etrucks" : 1.6e+8,
        "_integ_gov_tech_maturity_fund_stock" : 0 
    }

    def __init__(self, model):
        self.model = model.components
     
    # (Green box) (still "constants")
    def RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_DIESEL_TRUCKS(self): #
        """"The portion of income from diesel vehicle sales invested in research and development. Based on interviews with Scania experts, we assume that 1,5% of the income from diesel vehicle sales will be invested on R&D for improving technology maturity of electric vehicles. [Dmnl]"""
        return self.model.rd_percentage_of_annual_earning_of_diesel_trucks()
    
    def RD_PERCENTAGE_OF_ANNUAL_EARNING_OF_ETRUCKS(self): #
        """"The portion of income from electric vehicle sales invested in research and development. Based on interviews with Scania experts, we assume that 3,5% of the income from electric vehicle sales will be invested on R&D for improving technology maturity of electric vehicles. [Dmnl]"""
        return self.model.rd_percentage_of_annual_earning_of_etrucks()

    # (No box) (still "constants")
    def STOP_INVESTING_SWITCH(self): #
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
    def effect_of_technology_maturity(self): #
        """level of vehicle technology maturity [Dmnl]"""
        return self.model.effect_of_technology_maturity()
    
    def Effect_of_technology_maturity_percentage(self): #
        """level of vehicle technology maturity in percentage [Dmnl]"""
        return self.model.effect_of_technology_maturitypercentage()
    
    def Availability_of_charging_station_percentage(self): #
        """"The proportion that charging stations are functional and ready for use by electric vehicles. [Dmnl]"""
        return self.model.availability_of_charging_stationpercentage()
    
    def annual_RD_investment_from_diesel_truck_earnings(self): #
        """Investment allocated to research and development from diesel vehicle sales revenue. [SEK/year]"""
        return self.model.annual_rd_investment_from_diesel_truck_earnings()
    
    def total_annual_RD_investment__corporates(self): #
        """Funds allocated by private sector to research and development activities to improve technology and innovation per year. [SEK/year]"""
        return self.model.total_annual_rd_investment_corporates()
    
    def annual_gov_funding_for_improving_etruck_technology(self): #
        """Annual public investment to improve e-truck technology [SEK/year]"""
        return self.model.annual_gov_funding_for_improving_etruck_technology()
    
    def awareness_of_the_technology(self): #
        """Equivalent to the notion of "word of mouth"/"willingness-to-consider"/"knowledge and awareness of technology" within the Technological Innovation System (TIS) framework (Ortt & Kamp, 2022). [Dmnl]"""
        return self.model.awareness_of_the_technology()

    def awareness_of_the_technology_percentage(self): #
        """the percentage of awareness of technology [Dmnl]"""
        return self.model.awareness_of_the_technologypercentage()
            
    def perceived_etruck_utility_function__attractiveness(self): #
        """Cobb-Douglas Utility Function (very common to calculate utility in economics), also use for production function [Dmnl]"""
        return self.model.perceived_etruck_utility_function_attractiveness()
    
    def U2P_ratio(self): #
        """to prevent denominator from being negative in the extreme test [Dmnl]"""
        return self.model.u2p_ratio()

    def effect_of_utility_to_cost(self): #
        """rate of utility to cost of e-truck to d-truck scaled between 0 and 1 [Dmnl]"""
        # GRAPH(self.U2P_ratio) Points: (0.000, 0.000), (1.000, 1.000) 
        return self.model.effect_of_utilitytocost()

    def diesel_truck_sale(self): #
        """Number of new diesel trucks that are sold in each year [Vehicle/Year]"""
        return self.model.diesel_truck_sale()

    # Time function dependent - DIRECT
    def ratio_of_technology_maturity_to_goal(self): #
        """current technology maturity relative to its goal. [Dmnl]"""
        # GRAPH(technology_Maturity_of_Etruck/self.GOAL_OF_TECHNOLOGY_MATURITY_FUND) Points: (0.000, 0.000), (1.000, 1.000) 
        return self.model.ratio_of_technology_maturity_to_goal()
    
    def annual_RD_investment_from_etruck_earnings(self): #
        """Investment allocated to research and development from electric vehicle sales revenue. [SEK/year]"""
        return self.model.annual_rd_investment_from_etruck_earnings()
    
    def utility_to_cost_of_etruck(self): #
        """the utility devided by total cost of e-trucks [Dmnl*Vehicle/SEK]"""
        return self.model.utilitytocost_of_etruck()
    
    ## FLOWS
    # Inflows
    def Change_In_Utility(self): #
        """The rate of annual change for the utility function [Dmnl/year]"""
        return self.model.change_in_utility()
    
    def Technology_Development_of_Etruck(self): #
        """The process of acquiring knowledge and improvements in e-truck technology [technology/year]"""
        return self.model.technology_development_of_etruck()
    
    def RD_Investment(self): #
        """Funds allocated to improve e-truck technology and innovation per year [SEK/year]"""  
        return self.model.rd_investment()
    
    def Annual_Gov_Tech_Maturity_Fund(self): #
        """The annual public investment in technology maturity of e-trucks [SEK/year]"""
        return self.model.annual_gov_tech_maturity_fund()
    
    # Outflows
    def RD_Spending(self): #
        """Expenditure on research and development [SEK/year]"""
        return self.model.rd_spending()
    
    ## STOCKS
    def utility_Function_of_Etruck(self): #
        """The level of utility (attractiveness) of an e-truck [Dmnl]"""
        return self.model._integ_utility_function_of_etruck()
    
    def technology_Maturity_of_Etruck(self): #
        """"The level of advancement and development of electric truck technology, indicating how close it is to reaching its full potential and goals. [technology]"""
        return self.model._integ_technology_maturity_of_etruck()
    
    def rD_Fund_of_Etrucks(self): #
        """Total funds available for electric trucks research and development. [SEK]"""
        return self.model._integ_rd_fund_of_etrucks()
    
    def gov_Tech_Maturity_Fund_Stock(self): #
        """The accumulation of public funds contributes to the technological maturity of electric trucks. [SEK]"""
        return self.model._integ_gov_tech_maturity_fund_stock()

   
class vehicle_fleet_sector:
    # vehicle_fleet sector static variables
    DEFAULT = {
        "etruck_lifetime" : 12,
        # """The average operational lifespan of electric vehicles [Year]"""
        # INITIAL
        "initial_etruck_fleet_size" : 1,
        # """The starting number of electric trucks in the fleet [Vehicle]"""
        "initial_total_truck_fleet_size" : 83025
        # """"The starting number of total trucks in the fleet [Vehicle]"""
    }

    STOCK_DEFAULTS = {}

    def __init__(self, model):
        self.model = model.components
        
    def time_for_truck_sales(self):
        return self.model.time_for_truck_sales()

    ## OUTPUTS
    def share_of_electric_truck_in_new_sales(self): #
        """The proportion of the total truck fleet that is sold to the market [Dmnl]"""
        return self.model.etruck_share_in_new_sales()
                
    def share_of_electric_truck_in_total_fleet_size (self): #
        """The proportion of the total truck fleet that is electric [Dmnl]""" 
        return self.model.etruck_share_in_total_fleet()
    
    ## FLOWS
    # Inflows
    def Total_Truck_Sales(self):   
        """Number of new trucks (both electric and diesel) that are sold in each year [Vehicle/Year]"""
        return self.model.total_truck_sales()
    
    def Etruck_Sales(self):
        """Number of new electric trucks that are sold in each year [Vehicle/Year]"""
        return self.model.etruck_sales()
    
    # Outflows
    def Total_Truck_Decommission(self):
        """Number of total trucks that are removed from use in each year [Vehicle/Year]"""
        return self.model._delayfixed_total_truck_decommission()
                
    def Etruck_Decommission(self): #
        """Number of electric trucks that are removed from use in each year [Vehicle/Year]"""
        return self.model._delayfixed_etruck_decommission() 

    ## STOCKS 
    def etruck_Fleet_Size(self): #
        """The total number of electric trucks in the fleet [Vehicle]"""
        return self.model._integ_etruck_fleet_size()
    
    def total_Truck_Fleet_Size(self): #
        """The total number of trucks in the fleet [Vehicle]"""
        return self.model._integ_total_truck_fleet_size()


def baseline_scenario():
    SECTORS = [emission_sector, vehicle_fleet_sector, vehicle_cost_sector, utility_function_sector, charging_station_cost_and_profitability_sector, charging_station_availability_sector,investment_on_charging_stations_sector]
    merged_def = {}
    merged_stocks_def = {}
    for sector_cls in SECTORS:
        merged_def.update(getattr(sector_cls, "DEFAULT", {}))
        merged_stocks_def.update(getattr(sector_cls, "STOCK_DEFAULTS", {}))
    return merged_def, merged_stocks_def

def apply_scenario(model, overrides=None, stock_overrides=None):
    baseline_defaults,baseline_stock_defaults = baseline_scenario()
    scenario = {**baseline_defaults, **(overrides or {})}
    model.set_components(scenario)

    init_scenario = {**baseline_stock_defaults, **(stock_overrides or {})}
    for stock_attr, value in init_scenario.items():
        stock = getattr(model.components, stock_attr)
        stock.init_func = lambda v=value: v   # v=value avoids late-binding bug in the loop
    

if __name__ == "__main__":

    model = pysd.read_vensim("C:/Users/tonoz/Desktop/KTH/TFM/Appendix1_Supplementary_material_Vensim_simulation_model.mdl", initialize=False)

    var = model.doc
    name_map = dict(zip(var["Real Name"], var["Py Name"]))
    # dupes = var[var["Py Name"].duplicated(keep=False)]
    # print(dupes[["Real Name", "Py Name"]])

    # print(inspect.getsource(model.components._integ_total_gov_funds.init_func))
    # print("hey")

    # var.to_csv("C:/Users/tonoz/Desktop/KTH/TFM/output.csv", index=False)

    # print(var.columns.tolist())

    ##
    # results = model.run()

    # print(results.head())

    # usage
    apply_scenario(model)
    output = ModelOutput()
    model.set_stepper(output, final_time=2060) #Original Vensim simulation from 2017 to 2060

    model_class = Model(model)

    print(model_class.charg_cost_and_profitability.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks())
    print("Time:", model_class.t)

    print("Initial time:", model_class.t0)
    print("Final time:", model_class.tf)
    print("Time step:", model_class.dt)
    # result = model.run(
    #     params={},
    #     return_timestamps=[2017, 2060]
    # )
    # print(result)

    model.step(1)
    print(model_class.charg_cost_and_profitability.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks())
    print("Time:", model_class.t)
