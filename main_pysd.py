# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO
import os
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
pio.renderers.default = "browser"
import math
import argparse
import ast
import numpy as np
import pandas as pd
import pysd
import inspect
import LTM
from model_red import Model_red
import re
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
        #For the simulation
        self.nsteps = 1
        self.stocks_flows = dict()

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

    def del_warings(self):
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
        """**Set-up of static variables / initial values of stocks for the current simulation**"""
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

    def set_path(self, path_name, csv_bool):
        """**Creates the path folder in case the path does not exist**"""
        if csv_bool:
            if not os.path.exists(path_name):
                os.makedirs(path_name)
        return path_name

    def create_dataset(self, model, output_path, lv_outputs, unstable_bool):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        #HARD CODED DICTS AND LISTS
        input_output_dict = {
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

        #OUTPUTS OF THE SENSITIVITY ANALYSIS
        # levers_outputs_keys = ["etruck_fleet_size", "annual_total_gov_funds"] EN LA FUNCIÓN


        #Filtered dependencies dict
        filtered_deps, z_with_links = LTM.filter_dependencies(model)   
        names = list(filtered_deps.keys())

        relevance_history = []
        stock_relevance_history = []
        input_relevance_history = []
        relevance_loop_history = []
        out_loop_history = []
        stock_relevance_loop_history = []
        stock_loop_history = []
        input_relevance_loop_history = []
        input_loop_history = []
        prev = LTM.snapshot(model, names)
        for step_idx in range(self.nsteps):
            if unstable_bool:
                if (self.dt*step_idx)%8 == 4 and step_idx != 0: 
                    model.step(1, step_vars={"sensitivity_coefficient_for_charging_subsidy": 1.2,
                                            "sensitivity_coefficient_for_vehicle_subsidy": 1.2,
                                            "factor_of_gov_investment_on_the_tech_maturity": 1.2,
                                            "sensitivity_coefficient_for_price_of_electricity": 0.8,
                                            "sensitivity_coefficient_for_diesel": 1.2,
                                            "onoff_switch_for_considering_future_charging_demand": 1})
                elif (self.dt*step_idx)%8 == 0 and step_idx != 0:
                    model.step(1, step_vars={"sensitivity_coefficient_for_charging_subsidy": 0.8,
                                            "sensitivity_coefficient_for_vehicle_subsidy": 0.8,
                                            "factor_of_gov_investment_on_the_tech_maturity": 0.8,
                                            "sensitivity_coefficient_for_price_of_electricity": 1.2,
                                            "sensitivity_coefficient_for_diesel": 0.8,
                                            "onoff_switch_for_considering_future_charging_demand": 0})
                else:
                    model.step(1)
            else:
                model.step(1)
            cur = LTM.snapshot(model, names)
            #Initialize the class    
            ls_class = LTM.LinkScore()
            ls_class.model = model
            ls_class.cur = cur
            ls_class.prev = prev
            #Get df of the link scores of the model
            df = ls_class.link_score(self, filtered_deps, z_with_links)

            #Initialize the class    
            ps_class = LTM.PathScore()
            var_list, stock_list = ps_class.df_to_VariableSPA(self, df)
            ps_class.var_list = var_list  
            ps_class.stock_list = stock_list

            #Create the lists of VariableSPA variables that we are going to analyze
            # #INPUTS
            # inputs = list(set(levers_inputs_keys) | input_output_dict.keys())
            # print(f"List of inputs for the path_score analysis: {inputs}\n")
            # inputs_list = ps_class.list_to_VariableSPA(inputs)
            # #OUTPUTS
            # outputs = list(set().union(*input_output_dict.values()))
            # print(f"List of outputs for the path_score analysis: {outputs}\n")
            # outputs_list = ps_class.list_to_VariableSPA(outputs)
            #LV_OUTPUTS
            lv_outputs_list = ps_class.list_to_VariableSPA(lv_outputs)

            #Start the path search
            # #STOCKS - STOCKS
            # ps_class.path_search(stock_list, stock_list, model_class, model_class.set_path(os.path.join(output_path, "stock_stock")), False, True)
            # # INPUTS - STOCKS
            # ps_class.path_search(inputs_list, stock_list, model_class, model_class.set_path(os.path.join(output_path, "input_stock")), False, True)
            # # INPUTS - OUTPUTS
            # ps_class.path_search(inputs_list, outputs_list, model_class, model_class.set_path(os.path.join(output_path, "input_output")), False, True)
            # # STOCKS - OUTPUTS
            # ps_class.path_search(stock_list, outputs_list, model_class, model_class.set_path(os.path.join(output_path, "stock_output")), False, True)

            #STOCKS - SENSITIVITY OUTPUTS
            modified_output_path = os.path.join(output_path, "stock_lvOutput")
            set_of_stocks = set()
            for i in range(len(lv_outputs_list)):
                #1st-Search the stocks related to the outputs (and stocks-stocks relations)
                ps_class.backward_stock_search(self, [lv_outputs_list[i]], modified_output_path)

                scored,loop_scored = ps_class.score_stocks_for_output(self, lv_outputs_list[i], ps_class.stocks_related_to_output_total, False)
                if not scored.empty:
                    relevance_history.append(scored)
                if not loop_scored.empty:
                    relevance_loop_history.append(loop_scored)
                set_of_stocks |= ps_class.stocks_related_to_output_total
                # print(f"STOCKS RELATED TO OUTPUT {lv_outputs_list[i].name} AT TIME {model_class.t} are: \n{ps_class.stocks_related_to_output_total}\n")
                #CLEAN THE VARIABLES
                ps_class.stocks_related_to_output_total = set()
                ps_class.stocks_related_to_output_prev = set()
            # #Include total relative loop scores using all the loops in each timestep
            # out_loop_history_df = pd.concat(out_loop_history, ignore_index=True)
            # out_loop_history_df = ps_class.add_total_rel_loop_scores(out_loop_history_df)
            # #Reorganize the columns                                 
            # out_loop_history_df = out_loop_history_df[["t", "origin", "path_score", "relative_path_score", "total_loop_score","signed_total_loop_score", "relative_global_loop_score", "global_total_loop_score", "path_set", "stocks_in_path"]]
            # out_loop_history_df.rename(columns={"path_score": "loop_score", "relative_path_score": "relative_loop_score"}, inplace=True)
            # relevance_loop_history.append(out_loop_history_df)
            # out_loop_history = []

            #TRACK THE RELATIONS BETWEEN STOCKS                 
            # stocks_varSPA = ps_class.list_to_VariableSPA(stocks_flows.keys())
            stocks_varSPA = ps_class.list_to_VariableSPA(list(set_of_stocks))
            for i in range(len(list(stocks_varSPA))):            
                stock_scored, stock_loop_scored = ps_class.score_stocks_for_output(self, stocks_varSPA[i], list(set_of_stocks), False)
                if not stock_scored.empty:
                    stock_relevance_history.append(stock_scored)
                if not stock_loop_scored.empty:
                    stock_relevance_loop_history.append(stock_loop_scored)
            #Include total relative loop scores using all the loops in each timestep
            # stock_relevance_loop_history_df = pd.concat(stock_loop_history, ignore_index=True)
            # stock_relevance_loop_history_df = ps_class.add_total_rel_loop_scores(stock_relevance_loop_history_df)
            # #Reorganize the columns                                 
            # stock_relevance_loop_history_df = stock_relevance_loop_history_df[["t", "origin", "path_score", "relative_path_score", "total_loop_score","signed_total_loop_score", "relative_global_loop_score", "global_total_loop_score", "path_set", "stocks_in_path"]]
            # stock_relevance_loop_history_df.rename(columns={"path_score": "loop_score", "relative_path_score": "relative_loop_score"}, inplace=True)
            # stock_relevance_loop_history.append(stock_relevance_loop_history_df)
            # stock_loop_history = []
            #TRACK THE RELATIONS BETWEEN 
            suggested_inputs = [
                "mistrust_effect",
                "time_to_build_a_charging_station",
                "construction_cost_per_station",
                "lifetime_of_a_station",
                "margin_of_charging_providers_for_electricity_price",
                "time_to_close_gap_for_gov",
                "onoff_switch_for_considering_future_charging_demand",
                "planning_horizon",
                "technology_improvement_per_sek_spent",
                "time_to_spend_rd_funds",
                "average_mileage_per_vehicle_per_year",
                "etruck_lifetime",
                "purchase_cost_of_diesel_truck"
            ]
            inputs = list(set(levers_inputs_keys) | set(suggested_inputs))
            # print(inputs)
            #Constant inputs have always a link score of 0 with their next variable, so we need to check
            # the score of the next variable to see if its active or not
            inputs_SPA = ps_class.list_to_VariableSPA(inputs)
            input_dict = dict()
            for input in inputs_SPA:
                input_dict[input.name] = [input_next_var.variable.name for input_next_var in input.links]

            # print(input_dict)

            for i in range(len(list(stocks_varSPA))):     
                # print(f"\nFrom inputs to {stocks_varSPA[i].name}")       
                stock_scored, stock_loop_scored = ps_class.score_stocks_for_output(self, stocks_varSPA[i], inputs, False, input_dict)
                if not stock_scored.empty:
                    # stock_scored_print = stock_scored[["path_score","relative_path_score","origin","output","pair_total","global_relative_path_score","pair_relevance","t"]]
                    # stock_scored_print.to_csv(os.path.join(output_path, "input_csv",f"input-{stocks_varSPA[i].name}.csv"))            
                    input_relevance_history.append(stock_scored)
                else:
                    print(f"No input goes to {stocks_varSPA[i].name} at time {self.t}\n")
                if not stock_loop_scored.empty:
                    input_relevance_loop_history.append(stock_loop_scored)

            #END THE LOOP
            prev = cur
            print(f"Step completed. Current time: {self.t}\n")

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
        if relevance_loop_history:
            loop_history = pd.concat(relevance_loop_history, ignore_index=True)
            loop_history = loop_history[["t", "origin", "path_score", "relative_path_score", "total_loop_score", "signed_total_loop_score", "path_set", "stocks_in_path"]]
            loop_history.rename(columns={"path_score": "loop_score", "relative_path_score": "relative_loop_score", "path_set": "loop_set", "origin": "stock"}, inplace=True)
            loop_history.to_csv(os.path.join(output_path, "path_relevance_loop_history.csv"), index=False)

            keys_pairs = ["t", "loop_set"]
            loop_pairs = (loop_history.drop_duplicates(keys_pairs)
                            [["t", "stocks_in_path", "loop_score", "loop_set"]])
            #Include total relative loop scores using all the loops in each timestep
            loop_pairs = ps_class.add_total_rel_loop_scores(loop_pairs)
            #Reorganize the columns                                 
            loop_pairs["n_active_loops"] = loop_pairs.groupby("t")["loop_set"].transform("nunique") 
            loop_pairs = loop_pairs[["t", "stocks_in_path", "loop_score", "relative_global_loop_score", "n_active_loops", "global_loop_relevance", "global_total_loop_score", "global_signed_total_loop_score", "loop_set"]]          
            loop_pairs.to_csv(os.path.join(output_path, "stock_relevance_loop_pairs.csv"), index=False)

            loop_summary = (
                loop_pairs.groupby("loop_set", as_index=False)
                .agg(max_global_loop_relevance=("global_loop_relevance", "max"),
                    sum_global_loop_relevance=("global_loop_relevance", "sum"),
                    mean_global_loop_relevance_when_present=("global_loop_relevance", "mean"),
                    n_steps_present=("t", "nunique"),
                    stocks_in_path=("stocks_in_path", "first"))
            )
            loop_summary["mean_global_loop_relevance_all_steps"] = loop_summary["sum_global_loop_relevance"] / loop_pairs["t"].nunique()
            loop_summary = loop_summary.drop(columns="sum_global_loop_relevance")
            # Retrieve the corresponding relative_global_loop_score
            idx = loop_pairs.groupby("loop_set")["global_loop_relevance"].idxmax()
            max_scores = (loop_pairs.loc[idx, ["loop_set", "relative_global_loop_score", "n_active_loops"]])
            loop_summary = loop_summary.merge(max_scores,
                                            on="loop_set",
                                            how="left"
            )
            loop_summary = loop_summary.rename(columns={'relative_global_loop_score': 'max_relative_global_loop_score',
                                                        'n_active_loops': 'max_active_loops'})
            loop_summary = loop_summary[["max_relative_global_loop_score", "max_active_loops", "max_global_loop_relevance", "mean_global_loop_relevance_all_steps", "n_steps_present", "mean_global_loop_relevance_when_present", "loop_set", "stocks_in_path"]]
            loop_summary.to_csv(os.path.join(output_path, "global_loop_relevance_summary.csv"), index=False)

        if relevance_history:
            history = pd.concat(relevance_history, ignore_index=True)
            history = history[["t", "origin", "output", "path_score", "relative_path_score", "pair_relevance", "relative_pair_relevance", "pair_total", "signed_pair_total", "path_set", "stocks_in_path"]]
            history = history.sort_values(by=["t", "output"], kind="stable").reset_index(drop=True)
            history.to_csv(os.path.join(output_path, "path_relevance_history.csv"), index=False)

            keys_pairs = ["t", "output", "origin"]
            n_paths = history.groupby(keys_pairs).size().rename("active_paths").reset_index()
            pairs = (history.drop_duplicates(keys_pairs)
                            [["t", "output", "origin", "signed_pair_total", "pair_total", "pair_relevance", "relative_pair_relevance"]]
                             .merge(n_paths, on=keys_pairs, how="left"))
            n_output_paths = (pairs.groupby(["t", "output"]).agg(n_active_outputs=("origin", "nunique")).reset_index())
            pairs = pairs.merge(n_output_paths, on=["t", "output"], how="left")
            pairs.to_csv(os.path.join(output_path, "stock_relevance_pairs.csv"), index=False)


            keys = ["output", "origin"]
            d = pairs.dropna(subset=["pair_relevance"])
            peak = (
                d.sort_values(
                    ["pair_relevance", "relative_pair_relevance", "n_active_outputs"],
                    ascending=[False, False, False],   # highest relevance, then highest relative, then earliest step
                    na_position="last",               # a NaN relative value never wins over a real one
                )
                .drop_duplicates(keys)                # first row per pair = the winning timestep
                .rename(columns={
                    "pair_relevance": "max_relevance",
                    "relative_pair_relevance": "relative_max_relevance",
                    "n_active_outputs": "max_active_outputs",
                    "active_paths": "max_active_paths"
                })
                [keys + ["max_relevance", "relative_max_relevance", "max_active_outputs", "max_active_paths"]]
            )
            stats = (
                pairs.groupby(keys)
                .agg(
                    mean_relevance=("pair_relevance", "mean"),
                    steps_active=("pair_relevance", "count"),
                )
                .reset_index()
            )

            overall = (
                peak.merge(stats, on=keys, how="left")
                .sort_values(["output", "max_relevance"], ascending=[True, False])
                .reset_index(drop=True)
            )
            overall.to_csv(os.path.join(output_path, "stock_relevance_overall.csv"), index=False)

        #SAME WITH STOCKS
        if stock_relevance_loop_history:
            s_loop_history = pd.concat(stock_relevance_loop_history, ignore_index=True)
            s_loop_history = s_loop_history[["t", "origin", "path_score", "relative_path_score", "total_loop_score", "signed_total_loop_score", "path_set", "stocks_in_path"]]
            s_loop_history.rename(columns={"path_score": "loop_score", "relative_path_score": "relative_loop_score", "path_set": "loop_set", "origin": "stock"}, inplace=True)
            s_loop_history.to_csv(os.path.join(output_path, "s_path_relevance_loop_history.csv"), index=False)

            s_keys_pairs = ["t", "loop_set"]
            s_loop_pairs = (s_loop_history.drop_duplicates(s_keys_pairs)
                            [["t", "stocks_in_path", "loop_score", "loop_set"]])
            #Include total relative loop scores using all the loops in each timestep
            s_loop_pairs = ps_class.add_total_rel_loop_scores(s_loop_pairs)
            #Reorganize the columns                                 
            s_loop_pairs["n_active_loops"] = s_loop_pairs.groupby("t")["loop_set"].transform("nunique") 
            s_loop_pairs = s_loop_pairs[["t", "stocks_in_path", "loop_score", "relative_global_loop_score", "n_active_loops", "global_loop_relevance", "global_total_loop_score", "global_signed_total_loop_score", "loop_set"]]          
            s_loop_pairs.to_csv(os.path.join(output_path, "s_stock_relevance_loop_pairs.csv"), index=False)

            s_loop_summary = (
                s_loop_pairs.groupby("loop_set", as_index=False)
                .agg(max_global_loop_relevance=("global_loop_relevance", "max"),
                    sum_global_loop_relevance=("global_loop_relevance", "sum"),
                    mean_global_loop_relevance_when_present=("global_loop_relevance", "mean"),
                    n_steps_present=("t", "nunique"),
                    stocks_in_path=("stocks_in_path", "first"))
            )
            s_loop_summary["mean_global_loop_relevance_all_steps"] = s_loop_summary["sum_global_loop_relevance"] / s_loop_pairs["t"].nunique()
            s_loop_summary = s_loop_summary.drop(columns="sum_global_loop_relevance")
            # Retrieve the corresponding relative_global_loop_score
            s_idx = s_loop_pairs.groupby("loop_set")["global_loop_relevance"].idxmax()
            s_max_scores = (s_loop_pairs.loc[s_idx, ["loop_set", "relative_global_loop_score", "n_active_loops"]])
            s_loop_summary = s_loop_summary.merge(s_max_scores,
                                            on="loop_set",
                                            how="left"
            )
            s_loop_summary = s_loop_summary.rename(columns={'relative_global_loop_score': 'max_relative_global_loop_score',
                                                        'n_active_loops': 'max_active_loops'})
            s_loop_summary = s_loop_summary[["max_relative_global_loop_score", "max_active_loops", "max_global_loop_relevance", "mean_global_loop_relevance_all_steps", "n_steps_present", "mean_global_loop_relevance_when_present", "loop_set", "stocks_in_path"]]
            s_loop_summary.to_csv(os.path.join(output_path, "s_global_loop_relevance_summary.csv"), index=False)

        if stock_relevance_history:
            s_history = pd.concat(stock_relevance_history, ignore_index=True)
            s_history = s_history[["t", "origin", "output", "path_score", "relative_path_score", "pair_relevance", "relative_pair_relevance", "pair_total", "signed_pair_total", "path_set", "stocks_in_path"]]
            s_history = s_history.sort_values(by=["t", "output"], kind="stable").reset_index(drop=True)
            s_history.to_csv(os.path.join(output_path, "s_path_relevance_history.csv"), index=False)

            keys_pairs = ["t", "output", "origin"]
            s_n_paths = s_history.groupby(keys_pairs).size().rename("active_paths").reset_index()
            s_pairs = (s_history.drop_duplicates(keys_pairs)
                            [["t", "output", "origin", "pair_total", "pair_relevance", "relative_pair_relevance"]]
                            .merge(s_n_paths, on=keys_pairs, how="left"))
            s_n_output_paths = (s_pairs.groupby(["t", "output"]).agg(n_active_outputs=("origin", "nunique")).reset_index())
            s_pairs = s_pairs.merge(s_n_output_paths, on=["t", "output"], how="left")
            s_pairs.to_csv(os.path.join(output_path, "s_stock_relevance_pairs.csv"), index=False)

            keys = ["output", "origin"]
            s_d = s_pairs.dropna(subset=["pair_relevance"])
            s_peak = (
                s_d.sort_values(
                    ["pair_relevance", "relative_pair_relevance", "n_active_outputs"],
                    ascending=[False, False, False],   # highest relevance, then highest relative, then earliest step
                    na_position="last",               # a NaN relative value never wins over a real one
                )
                .drop_duplicates(keys)                # first row per pair = the winning timestep
                .rename(columns={
                    "pair_relevance": "max_relevance",
                    "relative_pair_relevance": "relative_max_relevance",
                    "n_active_outputs": "max_active_outputs",
                    "active_paths": "max_active_paths"
                })
                [keys + ["max_relevance", "relative_max_relevance", "max_active_outputs", "max_active_paths"]]
            )
            s_stats = (
                s_pairs.groupby(keys)
                .agg(
                    mean_relevance=("pair_relevance", "mean"),
                    steps_active=("pair_relevance", "count"),
                )
                .reset_index()
            )
            s_overall = (
                s_peak.merge(s_stats, on=keys, how="left")
                .sort_values(["output", "max_relevance"], ascending=[True, False])
                .reset_index(drop=True)
            )
            # s_overall = (s_pairs.groupby(["output", "origin"])
            #                 .agg(max_relevance=("pair_relevance","max"), relative_max_relevance=("relative_pair_relevance", "max"), mean_relevance=("pair_relevance", "mean"), steps_active=("pair_relevance", "count"))
            #                 .reset_index()
            #                 .sort_values(["output", "max_relevance"], ascending=[True, False]))
            s_overall.to_csv(os.path.join(output_path, "s_stock_relevance_overall.csv"), index=False)

        #SAME WITH INPUTS
        if input_relevance_loop_history:
            i_loop_history = pd.concat(input_relevance_loop_history, ignore_index=True)
            i_loop_history.to_csv(os.path.join(output_path, "i_path_relevance_loop_history.csv"), index=False)
        else:
            i_loop_history = pd.DataFrame()

        if input_relevance_history:
            i_history = pd.concat(input_relevance_history, ignore_index=True)
            i_history = i_history[["t", "origin", "output", "path_score", "relative_path_score", "pair_relevance", "relative_pair_relevance", "pair_total", "signed_pair_total", "path_set", "stocks_in_path"]]
            i_history = i_history.sort_values(by=["t", "output"], kind="stable").reset_index(drop=True)
            i_history.to_csv(os.path.join(output_path, "i_path_relevance_history.csv"), index=False)

            keys_pairs = ["t", "output", "origin"]
            i_n_paths = i_history.groupby(keys_pairs).size().rename("active_paths").reset_index()
            i_pairs = (i_history.drop_duplicates(keys_pairs)
                            [["t", "output", "origin", "pair_total", "pair_relevance", "relative_pair_relevance"]]
                            .merge(i_n_paths, on=keys_pairs, how="left"))
            i_n_output_paths = (i_pairs.groupby(["t", "output"]).agg(n_active_outputs=("origin", "nunique")).reset_index())
            i_pairs = i_pairs.merge(i_n_output_paths, on=["t", "output"], how="left")
            i_pairs.to_csv(os.path.join(output_path, "i_stock_relevance_pairs.csv"), index=False)

            keys = ["output", "origin"]
            i_d = i_pairs.dropna(subset=["pair_relevance"])
            i_peak = (
                i_d.sort_values(
                    ["pair_relevance", "relative_pair_relevance", "n_active_outputs"],
                    ascending=[False, False, False],   # highest relevance, then highest relative, then earliest step
                    na_position="last",               # a NaN relative value never wins over a real one
                )
                .drop_duplicates(keys)                # first row per pair = the winning timestep
                .rename(columns={
                    "pair_relevance": "max_relevance",
                    "relative_pair_relevance": "relative_max_relevance",
                    "n_active_outputs": "max_active_outputs",
                    "active_paths": "max_active_paths"
                })
                [keys + ["max_relevance", "relative_max_relevance", "max_active_outputs", "max_active_paths"]]
            )
            i_stats = (
                i_pairs.groupby(keys)
                .agg(
                    mean_relevance=("pair_relevance", "mean"),
                    steps_active=("pair_relevance", "count"),
                )
                .reset_index()
            )
            i_overall = (
                i_peak.merge(i_stats, on=keys, how="left")
                .sort_values(["output", "max_relevance"], ascending=[True, False])
                .reset_index(drop=True)
            )
            # i_overall = (i_pairs.groupby(["output", "origin"])
            #                 .agg(max_relevance=("pair_relevance","max"), relative_max_relevance=("relative_pair_relevance", "max"), mean_relevance=("pair_relevance", "mean"), steps_active=("pair_relevance", "count"))
            #                 .reset_index()
            #                 .sort_values(["output", "max_relevance"], ascending=[True, False]))
            i_overall.to_csv(os.path.join(output_path, "i_stock_relevance_overall.csv"), index=False)

        return history, pairs, overall, s_history, s_pairs, s_overall, i_history, i_pairs, i_overall, loop_summary, s_loop_summary

    def plot_heatmap(self, df, columns, case_string, scenario_name,
                    cell_w=70, cell_h=45, min_panel_h=350, min_width=800, gap_px=220):
        if isinstance(columns, str):          # allow a single column name too
            columns = [columns]

        nrows = len(columns)

        outputs = sorted(df["output"].unique())
        origins = sorted(df["origin"].unique())

        # Adaptive sizing (pixels), driven by the grid dimensions
        margin = dict(l=130, r=130, t=110, b=70)
        panel_h = max(min_panel_h, len(outputs) * cell_h + 80)    # height of each heatmap
        plot_h = nrows * panel_h + (nrows - 1) * gap_px           # plot area only (no margins)
        # width = max(min_width, len(origins) * cell_w + margin["l"] + margin["r"])
        height = plot_h + margin["t"] + margin["b"]

        fig = make_subplots(
            rows=nrows, cols=1,
            subplot_titles=[c.replace("_", " ").capitalize() for c in columns],
            # Plotly spacing is a fraction of the plot area, not of the full figure height
            vertical_spacing=(gap_px / plot_h) if nrows > 1 else 0,
        )

        for idx, column in enumerate(columns):
            row = idx + 1

            grid = (df.pivot(index="output", columns="origin", values=column)
                    .reindex(index=outputs, columns=origins))

            # Place each colorbar right next to its own panel
            subplot = fig.get_subplot(row, 1)
            x_end = subplot.xaxis.domain[1]
            y0, y1 = subplot.yaxis.domain

            fig.add_trace(
                go.Heatmap(
                    z=grid.values,
                    x=grid.columns,
                    y=grid.index,
                    colorscale="RdBu_r",
                    colorbar=dict(
                        title=column,
                        x=x_end + 0.01,
                        y=(y0 + y1) / 2,
                        len=(y1 - y0) * 0.9,
                    ),
                    texttemplate="%{z}",
                    hovertemplate=(f"Output: %{{y}}<br>Origin: %{{x}}<br>{column}: %{{z}}"
                                "<extra></extra>"),
                    xgap=2, ygap=2,
                ),
                row=row, col=1,
            )
            # Every panel has its own axes, so label each one
            fig.update_xaxes(title_text="Origin" if row == nrows else None, row=row, col=1)
            fig.update_yaxes(title_text="Output", row=row, col=1)

        names = ", ".join(c.replace("_", " ") for c in columns)
        fig.update_layout(
            title=(f"{names.capitalize()} from {case_string} for {scenario_name} "
                f"[{self.t0} to {self.nsteps * self.dt + self.t0}]"),
            # width=width,
            height=height,
            margin=margin,
        )
        fig.show()

    def plot_loop_relevance(
        data,                       # path to CSV or a DataFrame
        sort_by="max_global_loop_relevance",
        top_n=None,                 # show only the top N loops after sorting
        height_per_loop=22
    ):

        METRICS = [
            ("max_global_loop_relevance", "Max global loop relevance", "log"),
            ("max_relative_global_loop_score", "Max relative global loop score", "linear"),
            ("mean_global_loop_relevance_all_steps", "Mean global loop relevance (all steps)", "log"),
        ]
        """Three aligned horizontal bar panels (one per metric), one row per loop.

        Loops are sorted by `sort_by` so rows can be compared across metrics.
        Relevance panels use a log x-axis (values span ~1e-16 to ~1e3);
        the relative-score panel is linear and coloured by sign.
        """
        # df = pd.read_csv(data) if isinstance(data, str) else data.copy()
        df = pd.read_csv(data)
        
        # Short, readable labels; full loop info goes in the hover.
        df["loop_id"] = [f"Loop {i+1}" for i in range(len(df))]
        df["n_stocks"] = df["loop_set"].apply(lambda s: len(ast.literal_eval(s)))
        df["label"] = df["loop_id"] + " (" + df["n_stocks"].astype(str) + " stocks)"
        df["hover_stocks"] = df["loop_set"].apply(
            lambda s: "<br>".join(ast.literal_eval(s)))

        df = df.sort_values(sort_by, ascending=True)   # largest ends up on top
        if top_n:
            df = df.tail(top_n)

        fig = make_subplots(
            rows=1, cols=3, shared_yaxes=True, horizontal_spacing=0.02,
            subplot_titles=[m[1] for m in METRICS],
        )

        for col, (key, title, scale) in enumerate(METRICS, start=1):
            if key == "max_relative_global_loop_score":
                colors = ["#2a9d8f" if v >= 0 else "#e76f51" for v in df[key]]
            else:
                colors = "#264653"
            fig.add_trace(
                go.Bar(
                    x=df[key], y=df["label"], orientation="h",
                    marker_color=colors, showlegend=False,
                    customdata=df[["hover_stocks", "n_steps_present"]],
                    hovertemplate=(
                        "<b>%{y}</b><br>" + title + ": %{x:.3g}<br>"
                        "Steps present: %{customdata[1]}<br><br>"
                        "<i>Loop stocks:</i><br>%{customdata[0]}<extra></extra>"
                    ),
                ),
                row=1, col=col,
            )
            fig.update_xaxes(type=scale, row=1, col=col, showgrid=True,
                            gridcolor="rgba(128,128,128,0.25)")

        fig.add_vline(x=0, line_width=1, line_color="gray", row=1, col=2)
        fig.update_layout(
            title="Global loop relevance summary",
            height=max(400, height_per_loop * len(df) + 150),
            bargap=0.25, template="plotly_white",
            margin=dict(l=150, r=30, t=80, b=40),
        )
        fig.show()

     
    def plot_functions(self, df, outputs, column: str, case_string:str, scenario_name:str, per_fig: int = 3):
        for i in range(math.ceil(len(outputs) / per_fig)):
            chunk = outputs[i * per_fig:(i + 1) * per_fig]

            fig = make_subplots(
                rows=len(chunk), cols=1,
                shared_xaxes=True,
                vertical_spacing=0.08,
                subplot_titles=[f"{output} plots" for output in chunk],
            )

            seen = set()  # origins already in the legend
            for row, output in enumerate(chunk, start=1):
                sel = df[df["output"] == output].sort_values("t")
                for origin, g in sel.groupby("origin"):
                    fig.add_trace(
                        go.Scatter(
                            x=g["t"],
                            y=g[column],
                            mode="lines+markers",
                            name=str(origin),
                            legendgroup=str(origin),
                            showlegend=origin not in seen,
                        ),
                        row=row, col=1,
                    )
                    seen.add(origin)

            fig.update_layout(height=250 * len(chunk) + 100,
                            title_text=f"{column} evolution from {case_string} for {scenario_name} ({i + 1}/{math.ceil(len(outputs) / per_fig)})",)
            fig.show()

    def plot_results(self, history, pairs, overall, s_history, s_pairs, s_overall, i_history, i_pairs, i_overall, loop_summary, s_loop_summary, outputs, scenario_name, output_path):
        #Only print the stocks that have information
        s_outputs = [s for s in self.stocks_flows.keys() if s in s_overall["output"].values]
        i_outputs = [s for s in self.stocks_flows.keys() if s in i_overall["output"].values]        
        
        #Number of paths
        # n_paths = (history.groupby(["t", "output", "origin"])
        #             .size()
        #             .rename("n_paths")
        #             .reset_index())
        # self.plot_functions(n_paths, outputs, "n_paths", "stock to output", scenario_name)
        # #Pair relevance
        # self.plot_functions(pairs, outputs, "pair_relevance", "stock to output", scenario_name)
        # #Pair total (abs value)
        # self.plot_functions(pairs, outputs, "pair_total", "stock to output", scenario_name)
        #Loop
        # self.plot_loop_relevance(os.path.join(output_path, "global_loop_relevance_summary.csv"))
        #Path
        self.plot_heatmap(overall, ["max_relevance", "relative_max_relevance"], "stock to output", scenario_name)
        self.plot_heatmap(overall, "mean_relevance", "stock to output", scenario_name)
        #Number of paths
        # s_n_paths = (s_history.groupby(["t", "output", "origin"])
        #             .size()
        #             .rename("n_paths")
        #             .reset_index())
        # self.plot_functions(s_n_paths, s_outputs, "n_paths", "stock to stock", scenario_name)
        # #Pair relevance
        # self.plot_functions(s_pairs, s_outputs, "pair_relevance", "stock to stock", scenario_name)
        # #Pair total (abs value)
        # self.plot_functions(s_pairs, s_outputs, "pair_total", "stock to stock", scenario_name)
        #Loop
        # self.plot_loop_relevance(os.path.join(output_path, "s_global_loop_relevance_summary.csv"))
        #Path
        self.plot_heatmap(s_overall, ["max_relevance", "relative_max_relevance"], "stock to stock", scenario_name)
        self.plot_heatmap(s_overall, "mean_relevance", "stock to stock", scenario_name)
        #Number of paths
        # i_n_paths = (i_history.groupby(["t", "output", "origin"])
        #                 .size()
        #                 .rename("n_paths")
        #                 .reset_index())
        # self.plot_functions(i_n_paths, i_outputs, "n_paths", "input to stock", scenario_name)
        # #Pair relevance
        # self.plot_functions(i_pairs, i_outputs, "pair_relevance", "input to stock", scenario_name)
        # #Pair total (abs value)
        # self.plot_functions(i_pairs, i_outputs, "pair_total", "input to stock", scenario_name)
        self.plot_heatmap(i_overall, ["max_relevance", "relative_max_relevance"], "input to stock", scenario_name)
        self.plot_heatmap(i_overall, "mean_relevance", "input to stock", scenario_name)

def run_reduced_model(model, prunable_stocks, output_path, scenario_name, outputs, overrides=None, unstable_bool=False, step_vars = []):
    model.reload()
        
    model_class = Model(model) # Initialization of reader's class tree
    model_class.apply_scenario(model, overrides) # Set-up of static variables / initial values of stocks for the current simulation

    sim_params = {**{s: 1e-15 for s in prunable_stocks}}
    low_dict = {"sensitivity_coefficient_for_charging_subsidy": 0.8,
                "sensitivity_coefficient_for_vehicle_subsidy": 0.8,
                "factor_of_gov_investment_on_the_tech_maturity": 0.8,
                "sensitivity_coefficient_for_price_of_electricity": 1.2,
                "sensitivity_coefficient_for_diesel": 0.8,
                "onoff_switch_for_considering_future_charging_demand": 0}

    high_dict = {"sensitivity_coefficient_for_charging_subsidy": 1.2,
                "sensitivity_coefficient_for_vehicle_subsidy": 1.2,
                "factor_of_gov_investment_on_the_tech_maturity": 1.2,
                "sensitivity_coefficient_for_price_of_electricity": 0.8,
                "sensitivity_coefficient_for_diesel": 1.2,
                "onoff_switch_for_considering_future_charging_demand": 1}
    output = ModelOutput()
    model.set_stepper(output, final_time=2060, step_vars=step_vars+list(sim_params.keys()), return_columns=["time_for_emission_reduction"]+outputs)
    nsteps = int((model_class.tf - model_class.t0)/model_class.dt)
    for step_idx in range(nsteps):
        if unstable_bool:
            if (model_class.dt*step_idx)%8 == 4 and step_idx != 0:
                model.set_components(high_dict | sim_params)
                model.clean_caches()
                model.step(1, step_vars=sim_params)
            elif (model_class.dt*step_idx)%8 == 0 and step_idx != 0:
                model.set_components(low_dict | sim_params)
                model.clean_caches()
                model.step(1, step_vars=sim_params)
            else:
                model.step(1, step_vars=sim_params)
        else:
            model.step(1, step_vars=sim_params)
    baseline = output.collect(model)
    baseline.rename(columns={"time_for_emission_reduction": "time"}, inplace=True)
    baseline.to_csv(os.path.join(output_path, f"{scenario_name}_model_results.csv"), index=False)
    return baseline

def run_model(model, step_vars, base_output_path, scenario_name, outputs, n_steps, new_dfs_bool, plot_results_bool, overrides=None, unstable_bool=False):
    output_path = os.path.join(base_output_path, scenario_name)
    model.reload()

    output = ModelOutput()

    model_class = Model(model) # Initialization of reader's class tree
    model_class.apply_scenario(model, overrides) # Set-up of static variables / initial values of stocks for the current simulation
    model_class.stocks_flows = {
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

    model.set_stepper(output, final_time=2060, step_vars=step_vars, return_columns=outputs + ["time_for_emission_reduction"])

    #$#$#~TESTING THE OUTPUTS~#$#$#
    if n_steps is not None:
        model_class.nsteps = n_steps
    else: 
        model_class.nsteps = int((model_class.tf - model_class.t0)/model_class.dt) #For full simulations 

    if new_dfs_bool:
        history, pairs, overall, s_history, s_pairs, s_overall, i_history, i_pairs, i_overall, loop_summary, s_loop_summary = model_class.create_dataset(model, output_path, outputs, unstable_bool)
        # Get the results of the model run for further analysis if needed
        df_results = output.collect(model)
        df_results = df_results[["time_for_emission_reduction"] + outputs]
        df_results.rename(columns={"time_for_emission_reduction": "time"}, inplace=True)
        df_results.to_csv(os.path.join(output_path, "model_results.csv"), index=False)
    else:
        #Read the remaining datasets
        history = pd.read_csv(os.path.join(output_path, "path_relevance_history.csv"))
        pairs = pd.read_csv(os.path.join(output_path, "stock_relevance_pairs.csv"))
        overall = pd.read_csv(os.path.join(output_path, "stock_relevance_overall.csv"))
        s_history = pd.read_csv(os.path.join(output_path, "s_path_relevance_history.csv"))
        s_pairs = pd.read_csv(os.path.join(output_path, "s_stock_relevance_pairs.csv"))
        s_overall = pd.read_csv(os.path.join(output_path, "s_stock_relevance_overall.csv"))
        i_history = pd.read_csv(os.path.join(output_path, "i_path_relevance_history.csv"))
        i_pairs = pd.read_csv(os.path.join(output_path, "i_stock_relevance_pairs.csv"))
        i_overall = pd.read_csv(os.path.join(output_path, "i_stock_relevance_overall.csv"))
        loop_summary = pd.read_csv(os.path.join(output_path, "global_loop_relevance_summary.csv"))
        s_loop_summary = pd.read_csv(os.path.join(output_path, "s_global_loop_relevance_summary.csv"))

    #$#$#~PLOT THE RESULTS~#$#$#
    if plot_results_bool:
        model_class.plot_results(history, pairs, overall, s_history, s_pairs, s_overall, i_history, i_pairs, i_overall, loop_summary, s_loop_summary, outputs, scenario_name, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configuration of the pysd model simulation tool")
    parser.add_argument('vensim_path', help='Path to the Vensim .mdl file')
    parser.add_argument('output_path', help='Path where the outputs will be stored')
    parser.add_argument('-db', '--df_bool', action='store_true', help='Informs if a new dataset needs to be created')
    parser.add_argument('-pb', '--plot_bool', action='store_true', help='Informs if we want to plot the results')
    parser.add_argument('-sb', '--sim_bool', action='store_true', help='Informs if we are in a testing simulation')
    parser.add_argument('-n', '--num_steps', type=int, default=20, help='Number of steps for the testing simulation (default 20)')
    parser.add_argument('-rf', '--rel_factor', type=float, default=1.2, help='Factor for relative max threshold')
    parser.add_argument('-Mr', '--max_relevance', type=float, default=0.4, help='Max relevance threshold')
    parser.add_argument('-mr', '--mean_relevance', type=float, default=0.2, help='Mean relevance threshold')

    args = parser.parse_args()
    vensim_path = str(args.vensim_path)
    output_path = str(args.output_path)
    df_bool = bool(args.df_bool)
    plot_bool = bool(args.plot_bool)
    sim_bool = bool(args.sim_bool)
    num_steps = int(args.num_steps)
    rel_factor = float(args.rel_factor)
    max_relevance = float(args.max_relevance)
    mean_relevance = float(args.mean_relevance)

    # vensim_path = "C:/Users/tonoz/Desktop/KTH/TFM/Appendix1_Supplementary_material_Vensim_simulation_model.mdl"
    # output_path = "E:/TFM"
    # df_bool = False
    # plot_bool = False
    # sim_bool = False
    # num_steps = 20
    # rel_factor = 1.2
    # max_relevance = 0.4
    # mean_relevance = 0.15

    model = pysd.read_vensim(vensim_path)

    step_vars = ["sensitivity_coefficient_for_charging_subsidy", "sensitivity_coefficient_for_vehicle_subsidy", "factor_of_gov_investment_on_the_tech_maturity", "sensitivity_coefficient_for_price_of_electricity", "sensitivity_coefficient_for_diesel", "onoff_switch_for_considering_future_charging_demand"]

    if sim_bool:
        base_output_path = os.path.join(output_path, "outputs_testing") #Path where the output folder is located
        n_steps = num_steps #For testing
    else:
        base_output_path = os.path.join(output_path, "outputs") #Path where the output folder is located
        # base_output_path = "C:/Users/tonoz/Desktop/KTH/TFM/Repo_TFM/outputs" #Path where the output folder is located   
        n_steps = None #For full simulations
    if not os.path.exists(base_output_path):
        os.makedirs(base_output_path)
    
    outputs = ["etruck_fleet_size","annual_total_gov_funds"]
    #BASE SCENARIO
    run_model(model, step_vars, base_output_path, "base_scenario", outputs, n_steps, new_dfs_bool=df_bool, plot_results_bool=plot_bool)
    #LOW ELECTRIFICATION SCENARIO
    run_model(model, step_vars, base_output_path, "low_electrification_scenario", outputs, n_steps, new_dfs_bool=df_bool, plot_results_bool=plot_bool, overrides={"sensitivity_coefficient_for_charging_subsidy": 0.8,
                                                                                                                                                                "sensitivity_coefficient_for_vehicle_subsidy": 0.8,
                                                                                                                                                                "factor_of_gov_investment_on_the_tech_maturity": 0.8,
                                                                                                                                                                "sensitivity_coefficient_for_price_of_electricity": 1.2,
                                                                                                                                                                "sensitivity_coefficient_for_diesel": 0.8,
                                                                                                                                                                "onoff_switch_for_considering_future_charging_demand": 0})
    #HIGH ELECTRIFICATION SCENARIO
    run_model(model, step_vars, base_output_path, "high_electrification_scenario", outputs, n_steps, new_dfs_bool=df_bool, plot_results_bool=plot_bool, overrides={"sensitivity_coefficient_for_charging_subsidy": 1.2,
                                                                                                                                                                "sensitivity_coefficient_for_vehicle_subsidy": 1.2,
                                                                                                                                                                "factor_of_gov_investment_on_the_tech_maturity": 1.2,
                                                                                                                                                                "sensitivity_coefficient_for_price_of_electricity": 0.8,
                                                                                                                                                                "sensitivity_coefficient_for_diesel": 1.2,
                                                                                                                                                                "onoff_switch_for_considering_future_charging_demand": 1})
    
    #UNSTABLE POLICY SCENARIO
    run_model(model, step_vars, base_output_path, "unstable_policy_scenario", outputs, n_steps, new_dfs_bool=df_bool, plot_results_bool=plot_bool, overrides={"sensitivity_coefficient_for_charging_subsidy": 0.8,
                                                                                                                                                                "sensitivity_coefficient_for_vehicle_subsidy": 0.8,
                                                                                                                                                                "factor_of_gov_investment_on_the_tech_maturity": 0.8,
                                                                                                                                                                "sensitivity_coefficient_for_price_of_electricity": 1.2,
                                                                                                                                                                "sensitivity_coefficient_for_diesel": 0.8,
                                                                                                                                                                "onoff_switch_for_considering_future_charging_demand": 0}, unstable_bool=True)
    
    #&%#&%#&%#&%#&%#&%#&%#&%#&%#&%#&%#&%#&%#&%
    # Proceed with the model reduction part
    #&%#&%#&%#&%#&%#&%#&%#&%#&%#&%#&%#&%#&%#&%
    red_class = Model_red()
    #From the arguments
    red_class.rel_factor = rel_factor
    red_class.max_relevance = max_relevance
    red_class.mean_relevance = mean_relevance

    df_list = red_class.import_reduction_dfs(base_output_path)
    prunable_stocks = red_class.model_reduction(df_list)
    print(prunable_stocks)
    reduced_output_path = os.path.join(base_output_path, "reduction_folder")
    if not os.path.exists(reduced_output_path):
        os.makedirs(reduced_output_path)
    
    #Base scenario
    base_output = run_reduced_model(model, prunable_stocks, reduced_output_path, "base", outputs)
    full_base_output = pd.read_csv(os.path.join(base_output_path, "base_scenario", "model_results.csv"))
    base_nrmse = dict()
    for output in outputs:
        base_nrmse[output] = red_class.nrmse(full_base_output[output].values, base_output[output].values)
    base_df = pd.DataFrame([base_nrmse])
    base_df["scenario"] = "Base"
    print("\n\nNRMSE FOR BASE SCENARIO")
    print(base_nrmse)
    #Low scenario
    low_output = run_reduced_model(model, prunable_stocks, reduced_output_path, "low", outputs, overrides={"sensitivity_coefficient_for_charging_subsidy": 0.8,
                                                                                                                                        "sensitivity_coefficient_for_vehicle_subsidy": 0.8,
                                                                                                                                        "factor_of_gov_investment_on_the_tech_maturity": 0.8,
                                                                                                                                        "sensitivity_coefficient_for_price_of_electricity": 1.2,
                                                                                                                                        "sensitivity_coefficient_for_diesel": 0.8,
                                                                                                                                        "onoff_switch_for_considering_future_charging_demand": 0})
    full_low_output = pd.read_csv(os.path.join(base_output_path, "low_electrification_scenario", "model_results.csv"))
    low_nrmse = dict()
    for output in outputs:
        low_nrmse[output] = red_class.nrmse(full_low_output[output].values, low_output[output].values)
    low_df = pd.DataFrame([low_nrmse])
    low_df["scenario"] = "Low electrification"
    print("\n\nNRMSE FOR LOW SCENARIO")
    print(low_nrmse)
    #High scenario
    high_output = run_reduced_model(model, prunable_stocks, reduced_output_path, "high", outputs,  overrides={"sensitivity_coefficient_for_charging_subsidy": 1.2,
                                                                                                                                            "sensitivity_coefficient_for_vehicle_subsidy": 1.2,
                                                                                                                                            "factor_of_gov_investment_on_the_tech_maturity": 1.2,
                                                                                                                                            "sensitivity_coefficient_for_price_of_electricity": 0.8,
                                                                                                                                            "sensitivity_coefficient_for_diesel": 1.2,
                                                                                                                                            "onoff_switch_for_considering_future_charging_demand": 1})
    full_high_output = pd.read_csv(os.path.join(base_output_path, "high_electrification_scenario", "model_results.csv"))
    high_nrmse = dict()
    for output in outputs:
        high_nrmse[output] = red_class.nrmse(full_high_output[output].values, high_output[output].values)
    high_df = pd.DataFrame([high_nrmse])
    high_df["scenario"] = "High electrification"
    print("\n\nNRMSE FOR HIGH SCENARIO")
    print(high_nrmse)
    #Unstable scenario
    unstable_output = run_reduced_model(model, prunable_stocks, reduced_output_path, "unstable", outputs, overrides={"sensitivity_coefficient_for_charging_subsidy": 0.8,
                                                                                                                                                    "sensitivity_coefficient_for_vehicle_subsidy": 0.8,
                                                                                                                                                    "factor_of_gov_investment_on_the_tech_maturity": 0.8,
                                                                                                                                                    "sensitivity_coefficient_for_price_of_electricity": 1.2,
                                                                                                                                                    "sensitivity_coefficient_for_diesel": 0.8,
                                                                                                                                                    "onoff_switch_for_considering_future_charging_demand": 0}, unstable_bool=True, step_vars=step_vars)
    full_unstable_output = pd.read_csv(os.path.join(base_output_path, "unstable_policy_scenario", "model_results.csv"))
    unstable_nrmse = dict()
    for output in outputs:
        unstable_nrmse[output] = red_class.nrmse(full_unstable_output[output].values, unstable_output[output].values)    
    unstable_df = pd.DataFrame([unstable_nrmse])
    unstable_df["scenario"] = "Unstable policy"
    print("\n\nNRMSE FOR UNSTABLE SCENARIO")
    print(unstable_nrmse)
    nrmse_df_list = [base_df, low_df, high_df, unstable_df]
    nrmse_df = pd.concat(nrmse_df_list)
    nrmse_df.set_index("scenario", drop=False)
    nrmse_df = nrmse_df[["scenario"] + outputs]
    nrmse_df["prunable_stocks"] = str(prunable_stocks)
    nrmse_df["rel_factor"] = rel_factor
    nrmse_df["max_relevance"] = max_relevance
    nrmse_df["mean_relevance"] = mean_relevance
    nrmse_df.to_csv(os.path.join(base_output_path, "reduction_folder", f"nrsme_[{rel_factor},{max_relevance},{mean_relevance}].csv"))