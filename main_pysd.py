# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO
import os
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
pio.renderers.default = "browser"
import math
import ast
import numpy as np
import pandas as pd
import pysd
import inspect
import LTM
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

    def create_dataset(self, model, output_path, lv_outputs):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        #HARD CODED DICTS AND LISTS
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
        prev = LTM.snapshot(model, names)
        for _ in range(self.nsteps):
            model.step(1)
            cur = LTM.snapshot(model, names)
            #Initialize the class    
            ls_class = LTM.LinkScore()
            ls_class.model = model
            ls_class.cur = cur
            ls_class.prev = prev
            #Get df of the link scores of the model
            df = ls_class.link_score(self, stocks_flows, filtered_deps, z_with_links)

            #Initialize the class    
            ps_class = LTM.PathScore()
            var_list, stock_list = ps_class.df_to_VariableSPA(df, stocks_flows)
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

                scored = ps_class.score_stocks_for_output(self, lv_outputs_list[i], ps_class.stocks_related_to_output_total, False)
                if not scored.empty:
                    relevance_history.append(scored)
                set_of_stocks |= ps_class.stocks_related_to_output_total
                # print(f"STOCKS RELATED TO OUTPUT {lv_outputs_list[i].name} AT TIME {model_class.t} are: \n{ps_class.stocks_related_to_output_total}\n")
                #CLEAN THE VARIABLES
                ps_class.stocks_related_to_output_total = set()
                ps_class.stocks_related_to_output_prev = set()

            #TRACK THE RELATIONS BETWEEN STOCKS                 
            # stocks_varSPA = ps_class.list_to_VariableSPA(stocks_flows.keys())
            stocks_varSPA = ps_class.list_to_VariableSPA(list(set_of_stocks))
            for i in range(len(list(stocks_varSPA))):            
                stock_scored = ps_class.score_stocks_for_output(self, stocks_varSPA[i], list(set_of_stocks), False)
                if not stock_scored.empty:
                    stock_relevance_history.append(stock_scored)

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
                stock_scored = ps_class.score_stocks_for_output(self, stocks_varSPA[i], inputs, False, input_dict)
                if not stock_scored.empty:
                    # stock_scored_print = stock_scored[["path_score","relative_path_score","origin","output","pair_total","global_relative_path_score","pair_relevance","t"]]
                    # stock_scored_print.to_csv(os.path.join(output_path, "input_csv",f"input-{stocks_varSPA[i].name}.csv"))            
                    input_relevance_history.append(stock_scored)
                else:
                    print(f"No input goes to {stocks_varSPA[i].name} at time {self.t}\n")

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

        if relevance_history:
            history = pd.concat(relevance_history, ignore_index=True)
            history.to_csv(os.path.join(output_path, "path_relevance_history.csv"), index=False)

            pairs = (history.drop_duplicates(["t", "output", "origin"])
                            [["t", "output", "origin", "pair_total", "pair_relevance"]])
            pairs.to_csv(os.path.join(output_path, "stock_relevance_pairs.csv"), index=False)

            overall = (pairs.groupby(["output", "origin"])["pair_relevance"]
                            .agg(max_relevance="max", mean_relevance="mean", steps_active="count")
                            .reset_index()
                            .sort_values(["output", "max_relevance"], ascending=[True, False]))
            overall.to_csv(os.path.join(output_path, "stock_relevance_overall.csv"), index=False)

        #SAME WITH STOCKS
        if stock_relevance_history:
            s_history = pd.concat(stock_relevance_history, ignore_index=True)
            s_history.to_csv(os.path.join(output_path, "s_path_relevance_history.csv"), index=False)

            s_pairs = (s_history.drop_duplicates(["t", "output", "origin"])
                            [["t", "output", "origin", "pair_total", "pair_relevance"]])
            s_pairs.to_csv(os.path.join(output_path, "s_stock_relevance_pairs.csv"), index=False)

            s_overall = (s_pairs.groupby(["output", "origin"])["pair_relevance"]
                            .agg(max_relevance="max", mean_relevance="mean", steps_active="count")
                            .reset_index()
                            .sort_values(["output", "max_relevance"], ascending=[True, False]))
            s_overall.to_csv(os.path.join(output_path, "s_stock_relevance_overall.csv"), index=False)

        #SAME WITH INPUTS
        if input_relevance_history:
            i_history = pd.concat(input_relevance_history, ignore_index=True)
            i_history.to_csv(os.path.join(output_path, "i_path_relevance_history.csv"), index=False)

            i_pairs = (i_history.drop_duplicates(["t", "output", "origin"])
                            [["t", "output", "origin", "pair_total", "pair_relevance"]])
            i_pairs.to_csv(os.path.join(output_path, "i_stock_relevance_pairs.csv"), index=False)

            i_overall = (i_pairs.groupby(["output", "origin"])["pair_relevance"]
                            .agg(max_relevance="max", mean_relevance="mean", steps_active="count")
                            .reset_index()
                            .sort_values(["output", "max_relevance"], ascending=[True, False]))
            i_overall.to_csv(os.path.join(output_path, "i_stock_relevance_overall.csv"), index=False)

        return history, pairs, overall, s_history, s_pairs, s_overall, i_history, i_pairs, i_overall

    def plot_heatmap(self, df, column, case_string, scenario_name):
        fig = go.Figure(go.Heatmap(
            z=df[column],
            x=df.origin,
            y=df.output,
            colorscale="RdBu_r",                  # blue = cold, red = hot
            colorbar=dict(title=column),
            texttemplate="%{z}",                  # show values in cells
            hovertemplate="Output: %{y}<br>Origin: %{x}<br>Value: %{z}<extra></extra>",
            xgap=2, ygap=2,                       # gaps between cells
        ))
        fig.update_layout(title=f"{column.capitalize()} from {case_string} for {scenario_name} [{self.t0} to {self.nsteps * self.dt + self.t0}]")
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

    def plot_results(self, history, pairs, overall, s_history, s_pairs, s_overall, i_history, i_pairs, i_overall, outputs, scenario_name):
        stocks = ['average_power_of_charging_station',
                    'purchase_cost_of_etrucks', 
                    'rd_fund_of_etrucks',
                    'governmnet_fund_balance_by_five_levers', 
                    'gov_fund_on_diesel_price', 
                    'gov_fund_on_el_price_stock', 
                    'gov_charging_subsidy_stock_2', 
                    'gov_tech_maturity_fund_stock', 
                    'total_truck_fleet_size', 
                    'technology_maturity_of_etruck', 
                    'charging_stations_under_construction', 
                    'installed_charging_stations', 
                    'etruck_fleet_size', 
                    'cumulative_emission_without_any_etrucks', 
                    'total_gov_funds', 
                    'cumulative_emission_with_having_etrucks', 
                    'income_of_diesel_stock', 
                    'income_of_electricity_stock', 
                    'gov_vehicle_subsidy_stock', 
                    'gov_charging_subsidy_stock', 
                    'utility_function_of_etruck', 
                    'potential_private_investment_in_charging_stations',
                    'potential_government_investment_in_charging_stations']
        s_outputs = [s for s in stocks if s in s_overall["output"].values]

        i_outputs = [s for s in stocks if s in i_overall["output"].values]        
        
        #Number of paths
        n_paths = (history.groupby(["t", "output", "origin"])
                    .size()
                    .rename("n_paths")
                    .reset_index())
        self.plot_functions(n_paths, outputs, "n_paths", "stock to output", scenario_name)
        #Pair relevance
        self.plot_functions(pairs, outputs, "pair_relevance", "stock to output", scenario_name)
        #Pair total (abs value)
        self.plot_functions(pairs, outputs, "pair_total", "stock to output", scenario_name)
        self.plot_heatmap(overall, "max_relevance", "stock to output", scenario_name)
        self.plot_heatmap(overall, "mean_relevance", "stock to output", scenario_name)
        #Number of paths
        s_n_paths = (s_history.groupby(["t", "output", "origin"])
                    .size()
                    .rename("n_paths")
                    .reset_index())
        self.plot_functions(s_n_paths, s_outputs, "n_paths", "stock to stock", scenario_name)
        #Pair relevance
        self.plot_functions(s_pairs, s_outputs, "pair_relevance", "stock to stock", scenario_name)
        #Pair total (abs value)
        self.plot_functions(s_pairs, s_outputs, "pair_total", "stock to stock", scenario_name)
        self.plot_heatmap(s_overall, "max_relevance", "stock to stock", scenario_name)
        self.plot_heatmap(s_overall, "mean_relevance", "stock to stock", scenario_name)
        #Number of paths
        i_n_paths = (i_history.groupby(["t", "output", "origin"])
                        .size()
                        .rename("n_paths")
                        .reset_index())
        self.plot_functions(i_n_paths, i_outputs, "n_paths", "input to stock", scenario_name)
        #Pair relevance
        self.plot_functions(i_pairs, i_outputs, "pair_relevance", "input to stock", scenario_name)
        #Pair total (abs value)
        self.plot_functions(i_pairs, i_outputs, "pair_total", "input to stock", scenario_name)
        self.plot_heatmap(i_overall, "max_relevance", "input to stock", scenario_name)
        self.plot_heatmap(i_overall, "mean_relevance", "input to stock", scenario_name)


def run_model(model, step_vars, base_output_path, scenario_name, outputs, new_dfs_bool, plot_results_bool, overrides=None):
    output_path = os.path.join(base_output_path, scenario_name)
    model.reload()

    output = ModelOutput()

    model_class = Model(model) # Initialization of reader's class tree
    model_class.apply_scenario(model, overrides) 
    # model_class.apply_scenario(model, {"ETRUCK_LIFETIME" : 2, "INITIAL_TECHNOLOGY_MATURITY_OF_ETRUCK" : 10}) # Set-up of static variables / initial values of stocks for the current simulation

    model.set_stepper(output, final_time=2060, step_vars=step_vars) # Original Vensim simulation from 2017 to 2060

    #$#$#~TESTING THE OUTPUTS~#$#$#
    # model_class.nsteps = 20 #For testing
    model_class.nsteps = int((model_class.tf - model_class.t0)/model_class.dt) #For full simulations

    if new_dfs_bool:
        history, pairs, overall, s_history, s_pairs, s_overall, i_history, i_pairs, i_overall = model_class.create_dataset(model, output_path, outputs)
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
        
    
    #$#$#~PLOT THE RESULTS~#$#$#
    if plot_results_bool:
        model_class.plot_results(history, pairs, overall, s_history, s_pairs, s_overall, i_history, i_pairs, i_overall, outputs, scenario_name)

if __name__ == "__main__":

    model = pysd.read_vensim("C:/Users/tonoz/Desktop/KTH/TFM/Appendix1_Supplementary_material_Vensim_simulation_model.mdl")

    step_vars = ["sensitivity_coefficient_for_charging_subsidy", "sensitivity_coefficient_for_vehicle_subsidy", "factor_of_gov_investment_on_the_tech_maturity", "sensitivity_coefficient_for_price_of_electricity", "sensitivity_coefficient_for_diesel", "onoff_switch_for_considering_future_charging_demand"]

    base_output_path = "E:/TFM/outputs" #Path where the output folder is located
    # base_output_path = "C:/Users/tonoz/Desktop/KTH/TFM/Repo_TFM/outputs" #Path where the output folder is located    
    
    outputs = ["etruck_fleet_size","annual_total_gov_funds"]
    #BASE SCENARIO
    run_model(model, step_vars, base_output_path, "base_scenario", outputs, new_dfs_bool=False, plot_results_bool=False)
    #LOW ELECTRIFICATION SCENARIO
    run_model(model, step_vars, base_output_path, "low_electrification_scenario", outputs, new_dfs_bool=True, plot_results_bool=True, overrides={"sensitivity_coefficient_for_charging_subsidy": 0.8,
                                                                                                                                                                "sensitivity_coefficient_for_vehicle_subsidy": 0.8,
                                                                                                                                                                "factor_of_gov_investment_on_the_tech_maturity": 0.8,
                                                                                                                                                                "sensitivity_coefficient_for_price_of_electricity": 1.2,
                                                                                                                                                                "sensitivity_coefficient_for_diesel": 0.8,
                                                                                                                                                                "onoff_switch_for_considering_future_charging_demand": 0})
    #HIGH ELECTRIFICATION SCENARIO
    run_model(model, step_vars, base_output_path, "high_electrification_scenario", outputs, new_dfs_bool=True, plot_results_bool=True, overrides={"sensitivity_coefficient_for_charging_subsidy": 1.2,
                                                                                                                                                                "sensitivity_coefficient_for_vehicle_subsidy": 1.2,
                                                                                                                                                                "factor_of_gov_investment_on_the_tech_maturity": 1.2,
                                                                                                                                                                "sensitivity_coefficient_for_price_of_electricity": 0.8,
                                                                                                                                                                "sensitivity_coefficient_for_diesel": 1.2,
                                                                                                                                                                "onoff_switch_for_considering_future_charging_demand": 1})
    
    