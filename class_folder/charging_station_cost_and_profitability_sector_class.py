# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO

class charging_station_cost_and_profitability_sector:
    # charging_station_cost_and_profitability sector static variables
    DEFAULT = {
        "time_unit" : 1, 
        "construction_cost_per_station" : 1.7997E+06, # 1.80E+06, 
        "lifetime_of_a_station" : 8, 
        "sensitivity_coefficient_for_charging_subsidy" : 1, 
        "sensitivity_coefficient_for_price_of_electricity" : 1, 
        "ancillary_revenue" : 0, 
        "average_consumption_per_km_for_etruck" : 1.5, 
        "average_mileage_per_vehicle_per_year" : 90000, 
        "margin_of_charging_providers_for_electricity_price" : 0.2, #Based on interviews [Dmnl]
        "discount_rate" : 0.1, 
        "max_nominal_capacity_of_a_station_per_year" : 350*8760,         
        "construction_cost_per_kw": 5142,
        "adj_time_of_power_of_charging_station": 5, 
        "maximum_average_power_of_charging_station": 350,
        "total_hours_in_a_year": 8760,
        "operation_and_maintenance_cost_per_kwh_utilized_capacity": 0.25,
        #Initial
        "initial_average_power_of_charging_station": 350

    }

    STOCK_DEFAULTS = {
        "_integ_income_of_electricity_stock" : 0,
        "_integ_gov_fund_on_el_price_stock" : 0,
        "_integ_gov_charging_subsidy_stock_2" : 0
    }

    ALIASES = {
        "time_unit": "time_unit",
        "CONSTRUCTION_COST_PER_STATION": "construction_cost_per_station",
        "LIFETIME_OF_A_STATION": "lifetime_of_a_station",
        "sensitivity_coefficient_for_CHARGING_SUBSIDY": "sensitivity_coefficient_for_charging_subsidy",
        "sensitivity_coefficient_for_EL": "sensitivity_coefficient_for_price_of_electricity",
        "Ancillary_revenue": "ancillary_revenue",
        "AVERAGE_CONSUMPTION_PER_KM_FOR_ETRUCK": "average_consumption_per_km_for_etruck",
        "AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR": "average_mileage_per_vehicle_per_year",
        "MARGIN_OF_CHARGING_PROVIDERS_FOR_ELECTRICITY_PRICE": "margin_of_charging_providers_for_electricity_price",
        "DISCOUNT_RATE": "discount_rate",
        "MAX_NOMINAL_CAPACITY_OF_A_STATION_PER_YEAR": "max_nominal_capacity_of_a_station_per_year",
        "CONSTRUCTION_COST_PER_KW": "construction_cost_per_kw",
        "ADJ_TIME_OF_POWER_OF_CHARGING_STATION": "adj_time_of_power_of_charging_station",
        "MAXIMUM_AVERAGE_POWER_OF_CHARGING_STATION": "maximum_average_power_of_charging_station",
        "TOTAL_HOURS_IN_A_YEAR": "total_hours_in_a_year",
        "OPERATION_AND_MAINTENTANCE_COST_PER_kWh_UTILIZED_CAPACITY": "operation_and_maintenance_cost_per_kwh_utilized_capacity",
        # INITIAL
        "INITIAL_AVERAGE_POWER_OF_CHARGING_STATION": "initial_average_power_of_charging_station",
        "INITIAL_INCOME_OF_ELECTRICITY_STOCK": "_integ_income_of_electricity_stock",
        "INITIAL_GOV_FUND_ON_EL_PRICE_STOCK": "_integ_gov_fund_on_el_price_stock",
        "INITIAL_GOV_CHARGING_SUBSIDY_STOCK_2": "_integ_gov_charging_subsidy_stock_2"
    }
    
    def __init__(self, model):
        self.model = model.components

    @property
    def time_unit(self):
        """Formulation of the unit for IRR is complicated. Thus we used this vriable to fix unit left and hand right problem. It doesn't change the model [Year]"""
        return self.model.time_unit()

    @property
    def CONSTRUCTION_COST_PER_STATION(self):
        """Construction cost per kW [SEK/Charging stations]"""
        return self.model.construction_cost_per_station()

    @property
    def LIFETIME_OF_A_STATION(self):
        """"Based on interviews, EU report page 204, and REEL project report European Commission. (2021). Impact Assessment: Proposal for a Regulation of the European Parliament and of the Council on the deployment of alternative fuels infrastructure, and repealing Directive 2014/94/EU of the European Parliament and of the Council. REEL. (2022). Regional Electrified Logistics. [Year]"""
        return self.model.lifetime_of_a_station()

    @property
    def sensitivity_coefficient_for_CHARGING_SUBSIDY(self):
        """[Dmnl]"""
        return self.model.sensitivity_coefficient_for_charging_subsidy()

    @property
    def sensitivity_coefficient_for_EL(self):
        """using only for sensitivity analysis [Dmnl]"""
        return self.model.sensitivity_coefficient_for_price_of_electricity()

    @property
    def Ancillary_revenue(self):
        """[SEK/(Charging stations*Year)]"""
        return self.model.ancillary_revenue()

    @property
    def AVERAGE_CONSUMPTION_PER_KM_FOR_ETRUCK(self):
        """[kWh/KM]"""
        return self.model.average_consumption_per_km_for_etruck()

    @property
    def AVERAGE_MILEAGE_PER_VEHICLE_PER_YEAR(self):
        """[KM/(Vehicle*Year)]"""
        return self.model.average_mileage_per_vehicle_per_year()

    @property
    def MARGIN_OF_CHARGING_PROVIDERS_FOR_ELECTRICITY_PRICE(self):
        """Based on interviews [Dmnl]"""
        return self.model.margin_of_charging_providers_for_electricity_price()

    @property
    def DISCOUNT_RATE(self):
        """[Dmnl]"""
        return self.model.discount_rate()

    @property
    def MAX_NOMINAL_CAPACITY_OF_A_STATION_PER_YEAR(self):
        """Charger Power (kw/station)* 8760 hour/year [kWh/(Year*Charging stations)]"""
        return self.model.max_nominal_capacity_of_a_station_per_year()

    ## From "Average Power of Charging Station" stock
    @property
    def CONSTRUCTION_COST_PER_KW(self):
        """[SEK/Kw]"""
        return self.model.construction_cost_per_kw()

    @property
    def ADJ_TIME_OF_POWER_OF_CHARGING_STATION(self):
        """[Year]"""
        return self.model.adj_time_of_power_of_charging_station() 

    @property
    def MAXIMUM_AVERAGE_POWER_OF_CHARGING_STATION(self):    
        """[Kw/Charging stations]"""
        return self.model.maximum_average_power_of_charging_station()

    @property
    def TOTAL_HOURS_IN_A_YEAR(self):
        """Total number of hours in a year = 24*365 = 8760 [kWh/kw/Year]"""
        return self.model.total_hours_in_a_year()

    @property
    def OPERATION_AND_MAINTENTANCE_COST_PER_kWh_UTILIZED_CAPACITY(self):
        """The annual cost of operating and maintaining a charging station. [SEK/kWh]"""
        return self.model.operation_and_maintenance_cost_per_kwh_utilized_capacity()

    @property
    def INITIAL_AVERAGE_POWER_OF_CHARGING_STATION(self): 
        """[kw/Charging stations]"""
        return self.model.initial_average_power_of_charging_station()

    ## from Average Power of Charging Station (Not implemented in Excel file)
    def time_for_tech_maturity_of_power_of_charging_station(self):
        """[Time]"""
        return self.model.time_for_tech_maturity_of_power_of_charging_station()

    def TECHNOLOGY_MATURITY_OF_POWER_OF_CHARGING_STATION(self):
        """using look up to creat an S-shape growth [Dmnl]"""
        return self.model.tehnology_maturity_of_power_of_charging_station()

    def average_power_of_charging_station_gap(self):
        """[kw/Charging stations]"""
        return self.model.average_power_of_charging_station_gap()

    def maximum_nominal_capacity_of_a_charging_station_per_year__NEW(self):
        """[kWh/(Year*Charging stations)]"""
        return self.model.maximum_nominal_capacity_of_a_charging_station_per_year_new()

    def operational_and_maintenance_cost_of_a_station__based_on_utilisation(self):
        """[SEK/(Charging stations*Year)]"""
        return self.model.operational_maintenance_cost_of_a_station_based_on_utilisation()
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
    def MAX_UTILIZATION_RATE_OF_A_STATION_percentage(self): 
        """[Dmnl]"""
        return self.model.max_possible_utilization_rate_of_a_stationpercentage()
    
    def maximum_available_capacity_of_a_station_per_year(self): 
        """[kWh/(Year*Charging stations)]"""
        return self.model.maximum_available_capacity_of_a_station_per_year()
    
    def construction_cost_per_station_paid_by_infra_providers(self):
        """[SEK/Charging stations]"""
        return self.model.construction_cost_per_station_paid_by_infra_providers()
    
    def Construction_cost_paid_by_infra_providers_per_station_per_year__discounted(self): 
        """[SEK/(Charging stations*Year)]"""
        return self.model.construction_cost_paid_by_infra_providers_per_station_per_year_discounted()
    
    def CHARGE_RETAIL_PRICE(self): 
        """a ceil of 5*price of EL is considered to control the model in extreme test. [SEK/kWh]"""
        return self.model.charge_retail_price()

    def sale_revenue(self): 
        """[SEK/(Charging stations*Year)]"""
        return self.model.sale_revenue()
    
    def revenue_per_station_per_year(self): 
        """[SEK/(Charging stations*Year)]"""
        return self.model.revenue_per_station_per_year()
    
    def charging_station_profitability__Profitability_index_after_gov_subsidy(self): #
        """[Dmnl]"""
        return self.model.charging_station_profitability_index()
                
    def utilization_in_total(self): 
        """[Dmnl]"""
        return self.model.utilization_in_total()
    
    def utilization_in_total_percentage(self): 
        """[Dmnl]"""
        return self.model.utilization_in_totalpercentage()
            
    def utilization_rate_of_a_station(self): 
        """[Dmnl]"""
        return self.model.utilization_in_totalpercentage()

    def utilized_capacity_of_a_station_per_year(self): 
        """[kWh/(Year*Charging stations)]"""
        return self.model.utilized_capacity_of_a_station_per_year()
    
    def cost_of_electricity_per_station_per_year(self): 
        """[SEK/(Charging stations*Year)]"""
        return self.model.cost_of_electricity_per_station_per_year()

    def operation_cost_per_station_per_year(self): 
        """[SEK/(Charging stations*Year)]"""
        return self.model.operation_cost_per_station_per_year()
    
    def total_operational_cost_per_station__accumulated_over_lifetime_years(self): 
        """[SEK/Charging stations]"""
        return self.model.total_operational_cost_per_station_accumulated_over_lifetime_years()

    def GOV_SUBSIDY_PERCENTAGE_ON_CONSTRUCTION_COST_OF_CHARGING_STATIONS(self): 
        """Put a maximum to avoid to be more than 1! [Dmnl]"""
        return self.model.gov_subsidy_percentage_on_construction_cost_of_charging_stations()
    
    def max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks(self): 
        """"min of 0.1; max of 0.7 Based on interviews and Anders Grauers course Grauers, A. (2023). Electromobility: a system perspective [Course]. Swedish Electromobility Centre, Chalmers University of Technology. [Dmnl]"""
        # GRAPH(self.model.vehicle_fleet.share_of_electric_truck_in_total_fleet_size) Points: (0.000, 0.1000), (1.000, 0.7000)
        return self.model.max_possible_utilization_rate_of_a_station_lookup_number_of_etrucks()
    
    def Charging_station_Capacity_to_demand_ratio_percentage(self): 
        """[Dmnl]"""
        return self.model.charg_availability.charging_station_capacity_to_demand_ratio*100
                
    # Time dependent variables - DIRECT        
    def Average_energy_demand_from_each_station_per_year(self): 
        """to avoid being zero in the denominator [kWh/(Charging stations*Year)]"""
        return self.model.average_energy_demand_from_each_station_per_year()

    def Power_supply_per_etruck_per_year(self): 
        """[kWh/(Year*Vehicle)]"""
        return self.model.power_supply_per_etruck_per_year()
    
    def total_consumption_of_electric_fleet(self): 
        """[kWh/Year]"""
        return self.model.total_consumption_of_electric_fleet()
    
    def Total_power_supply_by_all_charging_station_per_year(self): 
        """[kWh/Year]"""
        return self.model.total_power_supply_by_all_charging_station_per_year()
    
    def total_capacity_of_all_installed_station(self): 
        """[kWh/Year]"""
        return self.model.total_capacity_of_all_installed_station()
    
    ## FLOWS
    # Inflows
    def Annual_income_of_electricity__inflow(self): 
        """[SEK/Year]"""
        return self.model.annual_income_of_electricity_inflow()
    
    def annual_gov_fund_on_EL_price(self): 
        """Positive amounts show that governments pay subsidies on EL; Negative amounts show that governments receive taxes on EL [SEK/Year]"""
        return self.model.annual_gov_fund_on_el_price()
    
    def annual_gov_subsidy_on_charging_2(self): 
        """[SEK/Year]"""
        return self.model.annual_gov_subsidy_on_charging_2()
    ## from Average Power of Charging Station (Not implemented in Excel file)
    def Increase_in_Average_Power_of_Charging_Station(self):
        """[kw/Charging stations/Year]"""
        return self.model.increase_in_average_power_of_charging_station()

    ## STOCKS
    def income_of_electricity_stock(self): 
        """[SEK]"""
        return self.model._integ_income_of_electricity_stock()
    
    def gov_fund_on_EL_price_stock(self): 
        """[SEK]"""
        return self.model._integ_gov_fund_on_el_price_stock()
    
    def gov_Charging_subsidy_stock_2(self): 
        """[SEK]"""
        return self.model._integ_gov_charging_subsidy_stock_2()
    ## from Average Power of Charging Station (Not implemented in Excel file)
    def average_Power_of_Charging_Station(self):
        """[kw/Charging stations]"""
        return self.model._integ_average_power_of_charging_station()

    
