# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO
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

    model = pysd.read_vensim("C:/Users/tonoz/Desktop/KTH/TFM/Appendix1_Supplementary_material_Vensim_simulation_model.mdl")

    # var = model.doc
    # name_map = dict(zip(var["Real Name"], var["Py Name"]))
    # var.to_csv("C:/Users/tonoz/Desktop/KTH/TFM/output.csv", index=False)

    # apply_scenario(model) # Set-up of static variables / initial values of stocks for the current simulation
    # apply_scenario(model, {"ETRUCK_LIFETIME" : 2}) # Set-up of static variables / initial values of stocks for the current simulation
    apply_scenario(model, {"ETRUCK_LIFETIME" : 2, "INITIAL_TECHNOLOGY_MATURITY_OF_ETRUCK" : 10}) # Set-up of static variables / initial values of stocks for the current simulation
    output = ModelOutput()
    model.set_stepper(output, final_time=2060) # Original Vensim simulation from 2017 to 2060

    model_class = Model(model) # Initialization of reader's class tree

    #TESTING THE OUTPUTS
    print(model_class.vehicle_fleet.ETRUCK_LIFETIME)  # self.etruck_lifetime = self.model.ETRUCK_LIFETIME
    print(model_class.investment_on_stations.future_demand_of_charging_station) #SMOOTH
    print(model_class.vehicle_fleet.Etruck_Decommission) #DELAY

    print("Time:", model_class.t)
    print(model_class.charg_cost_and_profitability.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks()) #VAR
    print("technology Maturity of Etruck [STOCK]: ",model_class.utility_function.technology_Maturity_of_Etruck()) #STOCK
    print(model_class.charg_cost_and_profitability.Annual_income_of_electricity__inflow()) #FLOW
    print(model_class.charg_cost_and_profitability.DEFAULT["average_mileage_per_vehicle_per_year"]) #STATIC VAR
    # print(model_class.charg_cost_and_profitability.STOCK_DEFAULTS["_integ_income_of_electricity_stock"]) #INITIAL VALUE OF STOCK
    
    model.step(1)

    print("\nTime:", model_class.t)
    print(model_class.charg_cost_and_profitability.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks()) #VAR
    print("technology Maturity of Etruck [STOCK]: ",model_class.utility_function.technology_Maturity_of_Etruck()) #STOCK
    print(model_class.charg_cost_and_profitability.Annual_income_of_electricity__inflow()) #FLOW
    print(model_class.charg_cost_and_profitability.DEFAULT["average_mileage_per_vehicle_per_year"]) #STATIC VAR

    # model.step(1)

    # print("\nTime:", model_class.t)
    # print(model_class.charg_cost_and_profitability.max_possible_utilization_rate_of_a_station__lookup_number_of_etrucks()) #VAR
    # print("technology Maturity of Etruck [STOCK]: ",model_class.utility_function.technology_Maturity_of_Etruck()) #STOCK
    # print(model_class.charg_cost_and_profitability.Annual_income_of_electricity__inflow()) #FLOW
    # print(model_class.charg_cost_and_profitability.DEFAULT["average_mileage_per_vehicle_per_year"]) #STATIC VAR