# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO
import os
import ast
import numpy as np
import pandas as pd
import pysd
import inspect
import LTM
from pysd.py_backend.output import ModelOutput
# Class imports
from class_folder.emission_sector_class import emission_sector
from class_folder.charging_station_cost_and_profitability_sector_class import charging_station_cost_and_profitability_sector
from class_folder.investment_on_charging_station_sector_class import investment_on_charging_stations_sector
from class_folder.charging_station_availability_sector_class import charging_station_availability_sector
from class_folder.vehicle_cost_sector_class import vehicle_cost_sector
from class_folder.utility_function_sector import utility_function_sector
from class_folder.vehicle_fleet_sector_class import vehicle_fleet_sector

import warnings


class Model:
    SECTORS = [emission_sector, vehicle_fleet_sector, vehicle_cost_sector, utility_function_sector, charging_station_cost_and_profitability_sector, charging_station_availability_sector,investment_on_charging_stations_sector]
    
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


    def baseline_scenario(self):
        merged_def = {}
        merged_stocks_def = {}
        for sector_cls in self.SECTORS:
            merged_def.update(getattr(sector_cls, "DEFAULT", {}))
            merged_stocks_def.update(getattr(sector_cls, "STOCK_DEFAULTS", {}))
        return merged_def, merged_stocks_def

    def collect_aliases(self):
        merged_aliases = {}
        for sector_cls in self.SECTORS:
            for alias, canonical in getattr(sector_cls, "ALIASES", {}).items():
                if alias in merged_aliases and merged_aliases[alias] != canonical:
                    raise ValueError(f"Alias '{alias}' maps to different canonical names across sectors")
                merged_aliases[alias] = canonical
        return merged_aliases

    def apply_scenario(self, model, overrides=None):
        baseline_defaults,baseline_stock_defaults = self.baseline_scenario()
        aliases = self.collect_aliases()

        # resolve alias names -> canonical py_names; leave already-canonical names untouched
        resolved = {aliases.get(key, key): value for key, value in (overrides or {}).items()} #Including both DEFAULT and STOCK_DEFAULTS variables

        const_changes = {k: v for k, v in resolved.items() if k in baseline_defaults}
        initial_stock_changes = {k: v for k, v in resolved.items() if k not in const_changes}

        scenario = {**baseline_defaults, **const_changes}
        model.set_components(scenario)

        init_scenario = {**baseline_stock_defaults, **initial_stock_changes}
        for stock_attr, value in init_scenario.items():
            stock = getattr(model.components, stock_attr)
            stock.init_func = lambda v=value: v   # v=value avoids late-binding bug in the loop
    

if __name__ == "__main__":

    warnings.filterwarnings(
    "ignore",
    message="Replacing a variable by a constant value.",
    category=UserWarning,
    )

    warnings.filterwarnings(
    "ignore",
    message="Replacing a constant value with a callable",
    category=UserWarning,
    )

    model = pysd.read_vensim("C:/Users/tonoz/Desktop/KTH/TFM/Appendix1_Supplementary_material_Vensim_simulation_model.mdl")

    # var = model.doc
    # name_map = dict(zip(var["Real Name"], var["Py Name"]))
    # var.to_csv("C:/Users/tonoz/Desktop/KTH/TFM/output.csv", index=False)

    output = ModelOutput()

    model_class = Model(model) # Initialization of reader's class tree
    model_class.apply_scenario(model) # Set-up of static variables / initial values of stocks for the current simulation
    # model_class.apply_scenario(model, {"ETRUCK_LIFETIME" : 2}) # Set-up of static variables / initial values of stocks for the current simulation
    # model_class.apply_scenario(model, {"ETRUCK_LIFETIME" : 2, "INITIAL_TECHNOLOGY_MATURITY_OF_ETRUCK" : 10}) # Set-up of static variables / initial values of stocks for the current simulation

    # model.set_stepper(output, final_time=2060)
    model.set_stepper(output, final_time=2060, step_vars=[model_class.charg_cost_and_profitability.ALIASES["LIFETIME_OF_A_STATION"]]) # Original Vensim simulation from 2017 to 2060

    #TESTING THE OUTPUTS
    output_path = "C:/Users/tonoz/Desktop/KTH/TFM/Repo_TFM/outputs"

    #HARD CODED
    stocks_flows = {
        #STOCK: [INFLOW, OUTFLOW]
        'average_power_of_charging_station': ['increase_in_average_power_of_charging_station', None],
        'purchase_cost_of_etrucks': [None, ['decrease_in_purchase_cost_of_etruck']], 
        'rd_fund_of_etrucks': ['rd_investment', ['rd_spending']], 
        'governmnet_fund_balance_by_five_levers': ["annual_gov_funding_by_five_levers", None], 
        'gov_fund_on_diesel_price': ['annual_gov_fund_on_diesel_price', None], 
        'gov_fund_on_el_price_stock': ['annual_gov_fund_on_el_price', None], 
        'gov_charging_subsidy_stock_2': ['annual_gov_subsidy_on_charging_2', None], 
        'gov_tech_maturity_fund_stock': ['annual_gov_tech_maturity_fund', None], 
        'total_truck_fleet_size': ['total_truck_sales', ['total_truck_decommission']], 
        'technology_maturity_of_etruck': ['technology_development_of_etruck', None], 
        'charging_stations_under_construction': ['building_charging_station', ['finishing_charging_station']], 
        'installed_charging_stations': ['finishing_charging_station', ['decaying_charging_station']], 
        'etruck_fleet_size': ['etruck_sales', ['etruck_decommission']], 
        'cumulative_emission_without_any_etrucks': ['annual_emission_without_any_etrucks', None], 
        'total_gov_funds': ['annual_total_gov_funds', None], 
        'cumulative_emission_with_having_etrucks': ['annual_emission_with_having_etrucks', None], 
        'income_of_diesel_stock': ['annual_income_of_diesel_inflow', None], 
        'income_of_electricity_stock': ['annual_income_of_electricity_inflow', None], 
        'gov_vehicle_subsidy_stock': ['annual_gov_subsidy_on_vehicle_purchase_cost', None], 
        'gov_charging_subsidy_stock': ['annual_gov_subsidy_on_charging', None], 
        'utility_function_of_etruck': ['change_in_utility', None], 
        'potential_private_investment_in_charging_stations': ['addition_of_private_investment_in_charging_stations', ['actual_private_investment_in_charging_stations', 'deciding_not_to_invest_reluctance_to_invest']], 
        'potential_government_investment_in_charging_stations': ['addition_of_government_investment_in_charging_stations', ['actual_government_investment_in_charging_stations']]
    }

    input_output_list = {
        #BASED ON THE INPUT-OUTPUT VARIABLES USED IN THE SENSITIVITY ANALYSIS
        "average_power_of_charging_station": ["construction_cost_per_station",
                                              "operational_maintenance_cost_of_a_station_based_on_percentage_of_capex",
                                              "charging_station_profitability_index",
                                              "etruck_share_in_total_fleet",
                                              "etruck_fleet_size",
                                              "utilization_rate_of_a_station",
                                              "installed_charging_stations"],
        "mistrust_effect": ["awareness_of_the_technology", 
                             "utility_function_of_etruck",
                             "etruck_share_in_total_fleet"],
        "based_utility_for_diesel_truck": ["etruck_share_in_total_fleet"],
        "margin_of_charging_providers_for_electricity_price": ["charge_retail_price",
                                                                "charging_station_profitability_index",
                                                                "etruck_share_in_total_fleet"],
        "construction_cost_per_kw": ["charging_station_profitability_index",
                                      "etruck_share_in_total_fleet"],
        "charging_capex_to_opex_conversion_factor": ["etruck_share_in_total_fleet"],
        "lifetime_of_a_station": ["installed_charging_stations",
                                  "etruck_share_in_total_fleet"],
        "max_possible_utilization_rate_of_a_station_lookup_number_of_etrucks": ["utilization_rate_of_a_station",
                                                                                "installed_charging_stations",
                                                                                "etruck_share_in_total_fleet"],
        "sensitivity_of_private_investors_to_profitability_index": ["installed_charging_stations",
                                                                    "etruck_share_in_total_fleet"],
        "technology_improvement_per_sek_spent": ["effect_of_technology_maturity",
                                                 "etruck_share_in_total_fleet"],
        "time_to_spend_rd_funds": ["effect_of_technology_maturity",
                                   "etruck_share_in_total_fleet"],
        "average_mileage_per_vehicle_per_year": ["electric_truck_total_cost",
                                                 "etruck_share_in_total_fleet"],
        "diesel_truck_lifetime": ["electric_truck_total_cost",
                                  "etruck_fleet_size"],
        "etruck_lifetime": ["electric_truck_total_cost",
                            "etruck_fleet_size"],
        "initial_purchase_cost_of_etrucks": ["electric_truck_total_cost",
                                             "etruck_fleet_size"],
        "purchase_cost_of_diesel_truck": ["electric_truck_total_cost",
                                          "etruck_share_in_total_fleet"],
        "average_consumption_per_km_for_diesel_truck": ["etruck_share_in_total_fleet"], #operational_cost_of_etrucks (?)
        "average_consumption_per_km_for_etruck": ["etruck_share_in_total_fleet"]        #operational_cost_of_etrucks (?)
    }

    levers_inputs_keys = ["sensitivity_coefficient_for_charging_subsidy", "sensitivity_coefficient_for_vehicle_subsidy", "factor_of_gov_investment_on_the_tech_maturity", "sensitivity_coefficient_for_price_of_electricity", "sensitivity_coefficient_for_diesel"]

    #Get df of the link scores of the model
    ls_class = LTM.LinkScore()
    df = ls_class.link_score(model, model_class, stocks_flows)
    
    ps_class = LTM.PathScore()
    var_list, stock_list = ps_class.df_to_VariableSPA(df, stocks_flows)
    # stocks_print = [stock.name for stock in stock_list]
    # print(f"STOCK_LIST: {stocks_print}\n \
    #       Number of stocks registered = {len(stocks_print)}/{len(stocks_flows.keys())}\n")
    ps_class.var_list = var_list

    #Look for loops with same stocks
    for stock_var in stock_list:
        path_set = ps_class.strongest_path_algorithm(stock_var, stock_list)

        path_score = ps_class.path_score(path_set)

        df3 = pd.DataFrame(path_score, columns=["path_score", "Relative_path_score", "path_set"])
        df3.to_csv(os.path.join(output_path,f'path_score_t-{model_class.t}-{stock_var.name}.csv'))

    # INPUTS - STOCKS
    inputs_list = ps_class.string_to_VariableSPA(levers_inputs_keys)
    for input in inputs_list:
        path_set = ps_class.strongest_path_algorithm(input, stock_list)
        
        path_score = ps_class.path_score(path_set)

        df4 = pd.DataFrame(path_score, columns=["path_score", "Relative_path_score", "path_set"])
        df4.to_csv(os.path.join(output_path,"input_stock",f'path_score_t-{model_class.t}-{input.name}.csv'))


    print(stocks_flows.values())
    

    # print("Time:", model_class.t)
    # print("-·-·-·-·-·-·-·-·-·-")
    # print("LIFETIME OF A STATION:",model_class.charg_cost_and_profitability.LIFETIME_OF_A_STATION()) #VAR
    # # print("total operational cost per station (accumulated over lifetime years)",model_class.charg_cost_and_profitability.total_operational_cost_per_station__accumulated_over_lifetime_years())
    # print("technology Maturity of Etruck [der]: ",model_class.utility_function.der_technology_Maturity_of_Etruck()) #STOCK
    # print("technology Maturity of Etruck [val]: ",model_class.utility_function.technology_Maturity_of_Etruck()) #STOCK

    
    # for n in range(40):
    #     if n%10 == 5:
    #         model.step(1, {model_class.charg_cost_and_profitability.ALIASES["LIFETIME_OF_A_STATION"]: model_class.charg_cost_and_profitability.LIFETIME_OF_A_STATION()+1})
    #     else:
    #         model.step(1)
    #     print("\nTime:", model_class.t)
    #     print("-·-·-·-·-·-·-·-·-·-")
    #     print("LIFETIME OF A STATION:",model_class.charg_cost_and_profitability.LIFETIME_OF_A_STATION()) #VAR
    #     # print("total operational cost per station (accumulated over lifetime years)",model_class.charg_cost_and_profitability.total_operational_cost_per_station__accumulated_over_lifetime_years())
    #     print("technology Maturity of Etruck [der]: ",model_class.utility_function.der_technology_Maturity_of_Etruck()) #STOCK
    #     print("technology Maturity of Etruck [val]: ",model_class.utility_function.technology_Maturity_of_Etruck()) #STOCK