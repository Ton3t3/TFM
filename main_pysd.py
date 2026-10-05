# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO

import ast
import numpy as np
import pandas as pd
import pysd
import inspect
from pysd.py_backend.output import ModelOutput
# Class imports
from class_folder.emission_sector_class import emission_sector
from class_folder.charging_station_cost_and_profitability_sector_class import charging_station_cost_and_profitability_sector
from class_folder.investment_on_charging_station_sector_class import investment_on_charging_stations_sector
from class_folder.charging_station_availability_sector_class import charging_station_availability_sector
from class_folder.vehicle_cost_sector_class import vehicle_cost_sector
from class_folder.utility_function_sector import utility_function_sector
from class_folder.vehicle_fleet_sector_class import vehicle_fleet_sector
import LTM

import warnings


def get_return_expression(func):
    """Parses a function's source code and returns the return expression as a string."""
    try:
        source = inspect.getsource(func)
        parsed = ast.parse(source)
        
        # Traverse nodes to find Return statements
        for node in ast.walk(parsed):
            if isinstance(node, ast.Return):
                # Unparse converts the AST expression node back into a readable code string
                return ast.unparse(node.value)
    except Exception as e:
        return f"Could not parse: {e}"
    return "No return statement found"


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


def baseline_scenario():
    SECTORS = [emission_sector, vehicle_fleet_sector, vehicle_cost_sector, utility_function_sector, charging_station_cost_and_profitability_sector, charging_station_availability_sector,investment_on_charging_stations_sector]
    merged_def = {}
    merged_stocks_def = {}
    for sector_cls in SECTORS:
        merged_def.update(getattr(sector_cls, "DEFAULT", {}))
        merged_stocks_def.update(getattr(sector_cls, "STOCK_DEFAULTS", {}))
    return merged_def, merged_stocks_def

def collect_aliases():
    SECTORS = [emission_sector, vehicle_fleet_sector, vehicle_cost_sector, utility_function_sector, charging_station_cost_and_profitability_sector, charging_station_availability_sector,investment_on_charging_stations_sector]
    merged_aliases = {}
    for sector_cls in SECTORS:
        for alias, canonical in getattr(sector_cls, "ALIASES", {}).items():
            if alias in merged_aliases and merged_aliases[alias] != canonical:
                raise ValueError(f"Alias '{alias}' maps to different canonical names across sectors")
            merged_aliases[alias] = canonical
    return merged_aliases

def apply_scenario(model, overrides=None):
    baseline_defaults,baseline_stock_defaults = baseline_scenario()
    aliases = collect_aliases()

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

    apply_scenario(model) # Set-up of static variables / initial values of stocks for the current simulation
    # apply_scenario(model, {"ETRUCK_LIFETIME" : 2}) # Set-up of static variables / initial values of stocks for the current simulation
    # apply_scenario(model, {"ETRUCK_LIFETIME" : 2, "INITIAL_TECHNOLOGY_MATURITY_OF_ETRUCK" : 10}) # Set-up of static variables / initial values of stocks for the current simulation
    output = ModelOutput()

    model_class = Model(model) # Initialization of reader's class tree

    # model.set_stepper(output, final_time=2060)
    model.set_stepper(output, final_time=2060, step_vars=[model_class.charg_cost_and_profitability.ALIASES["LIFETIME_OF_A_STATION"]]) # Original Vensim simulation from 2017 to 2060


    #TESTING THE OUTPUTS
    df = LTM.link_score(model, model_class)
    
    ## PRINT THE RETURN STATEMENTS OF ALL FUNCTIONS IN THE MODEL, BUT DOES NOT HELP AT ALL
    # # Get the list of dynamic variables from dependencies
    # dynamic_vars = [key for key, val in model._dependencies.items() if len(val) != 0]
    # static_vars = [key for key in model._dependencies.keys() if key not in dynamic_vars]
    # dynamic_vars = [var for var in dynamic_vars if var not in ["saveper", "OUTPUTS"]]  # Exclude "OUTPUTS" from the list of dynamic variables

    # # max_dependency = max(len(val) for val in model._dependencies.values())
    # # key_with_max_dependency = max(model._dependencies, key=lambda k: len(model._dependencies[k]))

    # max_dependency = 0
    # key_with_max_dependency = None
    # for key, val in model._dependencies.items():
    #     if key != "OUTPUTS":
    #         if len(val) > max_dependency:
    #             max_dependency = len(val)
    #             key_with_max_dependency = key
    
    
    # print(f"Maximum number of dependencies for any variable: {max_dependency}")
    # print(f"Variable with maximum dependencies: {key_with_max_dependency}")

    # for var_name in dynamic_vars:
    #     # Check if the component exists in model.components
    #     if hasattr(model.components, var_name):
    #         func = getattr(model.components, var_name)
            
    #         return_stmt = get_return_expression(func)
    #         print(f"{var_name} -> {return_stmt}")




    print("Time:", model_class.t)
    print("-·-·-·-·-·-·-·-·-·-")
    print("LIFETIME OF A STATION:",model_class.charg_cost_and_profitability.LIFETIME_OF_A_STATION()) #VAR
    # print("total operational cost per station (accumulated over lifetime years)",model_class.charg_cost_and_profitability.total_operational_cost_per_station__accumulated_over_lifetime_years())
    print("technology Maturity of Etruck [der]: ",model_class.utility_function.der_technology_Maturity_of_Etruck()) #STOCK
    print("technology Maturity of Etruck [val]: ",model_class.utility_function.technology_Maturity_of_Etruck()) #STOCK

    
    for n in range(40):
        if n%10 == 5:
            model.step(1, {model_class.charg_cost_and_profitability.ALIASES["LIFETIME_OF_A_STATION"]: model_class.charg_cost_and_profitability.LIFETIME_OF_A_STATION()+1})
        else:
            model.step(1)
        print("\nTime:", model_class.t)
        print("-·-·-·-·-·-·-·-·-·-")
        print("LIFETIME OF A STATION:",model_class.charg_cost_and_profitability.LIFETIME_OF_A_STATION()) #VAR
        # print("total operational cost per station (accumulated over lifetime years)",model_class.charg_cost_and_profitability.total_operational_cost_per_station__accumulated_over_lifetime_years())
        print("technology Maturity of Etruck [der]: ",model_class.utility_function.der_technology_Maturity_of_Etruck()) #STOCK
        print("technology Maturity of Etruck [val]: ",model_class.utility_function.technology_Maturity_of_Etruck()) #STOCK