#1. calculate link scores
#   How? 
#       a. check every function from the model
#       b. calculate link score for each variable used in the function
#   How can I identify the variables used in a function?


import importlib.util
import os

# file_path = "C:/Users/tonoz/Desktop/KTH/TFM"
# file_name = "Appendix1_Supplementary_material_Vensim_simulation_model.mdl"

# def get_full_file_path():
#     py_filename = file_name.replace(".mdl", "") + ".py"
#     return os.path.join(file_path, py_filename)

# # 1. Get the absolute file path to the .py file
# full_path = get_full_file_path()

# # 2. Load the module spec from the file path
# module_name = "translated_model"  # Arbitrary internal name for the module
# spec = importlib.util.spec_from_file_location(module_name, full_path)
# # spec = importlib.util.spec_from_file_location(module_name, "C:/Users/tonoz/Desktop/KTH/TFM/Appendix1_Supplementary_material_Vensim_simulation_model.py")
# # 3. Create and execute the module
# model_raw = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(model_raw)

# # 4. Access functions or variables inside the imported model
# value = model_raw.operational_maintenance_cost_of_a_station_based_on_percentage_of_capex()
# print(value)




import numpy as np
import pandas as pd

def snapshot(model, names):
    res = {n: model[n] for n in names}
    res["time"] = model.components.time()
    return res

def eval_z(model, z, inputs, originals, cur_z=None):
    model.set_components(inputs)         # replace inputs by constants
    model.clean_caches()                 # make sure z is recomputed
    val = model[z]
    print(f"Inputs: {inputs}\nz12: {val}")
    for k, f in originals.items():       # restore the original equations
        setattr(model.components, k, f)
    model.clean_caches()
    val_restored = model[z]
    if abs(cur_z - val_restored) != 0:
        print(f"WARNING: Restored {z} value {val_restored} does not match current value {cur_z}")
    return val

def link_score(model, model_class):
    df_list = []
    deps = model.dependencies
    #Filtered 
    stateful_vars = {}
    filtered_deps = {}
    for key, val in deps.items():
        if (key not in ["saveper", "OUTPUTS"]) and (key[0] != "_"):
            filtered_deps[key] = val
            if (getattr(model.components, key).type == "Stateful"):
                stateful_vars[key] = val
    dynamic_vars = [key for key, val in filtered_deps.items() if (len(val) != 0) and (key not in stateful_vars.keys())]
    static_vars = [key for key in filtered_deps.keys() if key not in dynamic_vars]


    categories = ["z", "dz", "inputs", "dx", "dz_x", "ls"]
    rows = []
    n_steps = 2
    # links_to_score = ["operation_cost_per_station_per_year","diesel_retail_price"]
    links_to_score = dynamic_vars
    names = list(filtered_deps.keys())
    
    prev = snapshot(model, names)
    for _ in range(n_steps):
        model.step(1)
        cur = snapshot(model, names)
        for z in links_to_score:             # aux/flow variables, not stocks
            print(f"Previous value of {z} (z1): {prev[z]}")
            print(f"Current value of {z} (z2): {cur[z]}")
            print("··" * 50)
            dx_total = []
            dz_x_total = []
            ls_total = []
            for x in deps[z]:
                print(f"[ {x} -> {z} ]")                
                print(f"Previous value of {x} (x1): {prev[x]}")
                print(f"Current value of {x} (x2): {cur[x]}")
                inputs = {d: prev[d] for d in deps[z] if d != x}
                inputs[x] = cur[x]
                originals = {d: getattr(model.components, d) for d in inputs}
                z_x = eval_z(model, z, inputs, originals, cur_z=cur[z])
                dz_x, dz, dx = z_x - prev[z], cur[z] - prev[z], cur[x] - prev[x]
                dx_total.append(dx)
                dz_x_total.append(dz_x)
                ls = 0.0 if (dz == 0 or dx == 0) else abs(dz_x/dz) * np.sign(dz_x/dx)
                ls_total.append(ls)
                # store ls[(x, z)][model.time()]
                print(f"dz_x: {dz_x}, dz: {dz}, dx: {dx}")
                print(f"Link score for {z} with respect to its dependencies: {ls}")
                print("··" * 50)
            rows.append([z, dz, inputs, dx_total, dz_x_total, ls_total])
            print("\n")
        prev = cur
        print(f"Step completed. Current time: {model_class.t}\n")
        df = pd.DataFrame(rows, columns=categories)
        df.set_index("z")
        df_list.append(df)
        df.to_csv(f'link_score_t-{model_class.t}.csv')
    return df_list