#1. calculate link scores
#   How? 
#       a. check every function from the model
#       b. calculate link score for each variable used in the function
#   How can I identify the variables used in a function?

# from xxlimited import Str

import numpy as np
import pandas as pd
from itertools import islice

def snapshot(model, names):
    """**Takes a snapshot of the model's current state for all the variables of the model**"""
    res = {n: model[n] for n in names}
    res["time"] = model.components.time()
    return res

def eval_z(model, z, inputs, originals, cur_z=None):
    # replace inputs by constants
    model.set_components(inputs)  
    model.clean_caches()      
    # recompute z with the corresponding past and current values                  
    val = model[z]
    # print(f"Inputs: {inputs}\nz12: {val}")
    # restore the original equations
    for key, function in originals.items():       
        setattr(model.components, key, function)
    model.clean_caches()
    val_restored = model[z]
    if abs(cur_z - val_restored) != 0:
        print(f"WARNING: Restored {z} value {val_restored} does not match current value {cur_z}")
    return val

def link_score(model, model_class, stocks_flows):
    deps = model.dependencies
    #Filtered 
    stateful_vars = []
    discarted_vars = {}
    filtered_deps = {}

    for key, val in deps.items():
        if (key not in ["saveper", "time_step", "final_time", "initial_time", "OUTPUTS"]) and (key[0] != "_"):
            if (getattr(model.components, key).type == "Stateful"):
                val_dict = dict()
                # Get all the variables that the stocks depended on, some of them
                # will require to look further than others
                for i_key, i_val in val.items():
                    # In case one of the dependencies is a stock, we want to get the dependencies 
                    # under the "initial" and "step" dicts 
                    if "_" in i_key[0]:
                        #References a _integ / _delayfixed / _smooth
                        print(f"Cheching {key}...\n")
                        stateful_var_dependencies = model.dependencies[i_key]
                        val_dict.update(stateful_var_dependencies["initial"] | stateful_var_dependencies["step"])
                    else:
                        val_dict[i_key] = i_val
                stateful_vars.append(key)
                filtered_deps[key] = val_dict
            else:
                filtered_deps[key] = val
    dynamic_vars = [key for key, val in filtered_deps.items() if (len(val) != 0) and (key not in [var for var in stateful_vars if (getattr(model.components, var).subtype != "Integ")])] #Not including _smooth and _delayfixed
    static_vars = [key for key in filtered_deps.keys() if (key not in dynamic_vars) and (key not in stateful_vars)]
    # print (f"Stateful variables: {stateful_vars}")
    # print (f"Discarded variables: {[vars for vars in deps.keys() if (deps.keys() not in filtered_deps.keys())]}")

    categories = ["z", "dz", "inputs", "dx", "dz_x", "ls"]
    rows = []
    n_steps = 1
    links_to_score = dynamic_vars
    names = list(filtered_deps.keys())
    
    prev = snapshot(model, names)
    for _ in range(n_steps):
        model.step(1)
        cur = snapshot(model, names)
        for z in links_to_score:             # aux/flow variables, not stocks or stateful vars
            dx_total = []
            dz_x_total = []
            ls_total = []
            not_flow_x_counter = 0
            for x in filtered_deps[z]:
                # IN CASE THE CURRENT Z IS A STOCK
                is_stateful_bool = (getattr(model.components, z).type == "Stateful")
                if is_stateful_bool:
                    #ONLY INCLUDE THE LINKS THAT ARE NOT FLOWS
                    if (x in stocks_flows[z]) or (stocks_flows[z][1] is not None and x in stocks_flows[z][1]):
                        continue
                    else:
                        not_flow_x_counter += 1                                         
                        inputs = {d: prev[d] for d in filtered_deps[z] if (d != x) and not((d in stocks_flows[z]) or (stocks_flows[z][1] is not None and d in stocks_flows[z][1]))}
                        inputs[x] = cur[x]
                        originals = {d: getattr(model.components, d) for d in inputs}
                        z_x = eval_z(model, z, inputs, originals, cur_z=cur[z])
                        dz_x, dz, dx = z_x - prev[z], cur[z] - prev[z], cur[x] - prev[x]
                        dx_total.append(dx)
                        dz_x_total.append(dz_x)
                        ls = 0.0 if (dz == 0 or dx == 0) else abs(dz_x/dz) * np.sign(dz_x/dx)
                        ls_total.append(ls)
                else:
                    inputs = {d: prev[d] for d in filtered_deps[z] if d != x}
                    inputs[x] = cur[x]
                    originals = {d: getattr(model.components, d) for d in inputs}
                    z_x = eval_z(model, z, inputs, originals, cur_z=cur[z])
                    dz_x, dz, dx = z_x - prev[z], cur[z] - prev[z], cur[x] - prev[x]
                    dx_total.append(dx)
                    dz_x_total.append(dz_x)
                    ls = 0.0 if (dz == 0 or dx == 0) else abs(dz_x/dz) * np.sign(dz_x/dx)
                    ls_total.append(ls)
                # print(f"dz_x: {dz_x}, dz: {dz}, dx: {dx}")
                # print(f"Link score for {z} with respect to its dependencies: {ls}")
                # print("··" * 50)
            if (not is_stateful_bool) or ((is_stateful_bool) and (not_flow_x_counter != 0)):
                rows.append([z, dz, inputs, dx_total, dz_x_total, ls_total])
            # print("\n")
        for z in static_vars:            
            #Since all these variables are static, their link score is 0.0
            rows.append([z, 0.0, {}, 0.0, 0.0, 0.0])
        
        df = pd.DataFrame(rows, columns=categories)
        df.set_index("z")
        df.to_csv(f'link_score_t-{model_class.t}-previous.csv')
        #CHANGE FORMAT FOR STRONGEST PATH ALGORITHM
        rows2 = []
        visited_current_x = []
        visited_z = set()
        categories2 = ["x", "z", "ls", "stock_bool"]
        for _, row in df.iterrows():
            for x_var in row["inputs"]:
                future_z_list = []
                future_ls_list = []
                if x_var not in visited_current_x:
                    current_x = x_var
                    for _, row2 in df.iterrows():
                        counter = 0
                        for x_var2 in row2["inputs"]:
                            if current_x == x_var2:
                                future_z_list.append(row2["z"])
                                visited_z.add(row2["z"])
                                future_ls_list.append(row2["ls"][counter])
                            counter += 1
                    visited_current_x.append(current_x)
                    #MARK IF THE CURRENT_X IS A STOCK OR NOT
                    if current_x in stocks_flows.keys():
                        rows2.append([current_x, future_z_list, future_ls_list, True]) 
                    else:
                        rows2.append([current_x, future_z_list, future_ls_list, False]) 
        
        #CHECK HOW MANY VARIABLES ARE NOT INCLUDED
        print((set(static_vars) | set(dynamic_vars)) - (set(visited_current_x)|(set(visited_z))))
        #Stock pipe related links [ ls(i->s) and ls(o->s)]
        for s in stocks_flows.keys():
            exists_inflow_bool = True
            exists_outflow_bool = True
            #Inflow
            inflow = stocks_flows[s][0]
            if inflow == None:
                inflow_value = 0
                exists_inflow_bool = False
            else: 
                inflow_value = prev[inflow]
            #Outflows
            outflow = stocks_flows[s][1]
            if outflow == None:
                outflow_value_list = [0]
                exists_outflow_bool = False
            else:
                #There exist one of the stocks that has two outflows
                outflow_value_list = [prev[o] for o in outflow]
                total_outflow_value = sum(outflow_value_list)
            #CALCULATE LINK SCORES
            ls_is = 0
            ls_os_list = dict()
            #CASE I -> S -> NONE
            if exists_outflow_bool == False:
                if inflow_value == 0:
                    ls_is = 0
                else:
                    ls_is = 1
            #CASE NONE -> S -> O
            elif exists_inflow_bool == False:
                for i in range(len(outflow_value_list)):
                    if outflow_value_list[i] == 0:
                        ls_os_list[outflow[i]] = 0
                    else:
                        ls_os_list[outflow[i]] = 1
            # CASE I -> S -> O
            else:
                ls_is = abs(inflow_value/(inflow_value-total_outflow_value))
                for i in range(len(outflow_value_list)):
                    ls_os_list[outflow[i]] = abs(outflow_value_list[i]/(inflow_value-total_outflow_value))
            
            #STORE THE LINK SCORES
            #Store inflows (i -> s)
            if exists_inflow_bool:
                i_in_list = False
                #CASE A: THE VARIABLE IS ALREADY DEFINED IN ROWS2 => ADD THE LINK TO THE EXISTING ROW
                for sublist in rows2:
                    if (sublist and sublist[0] == inflow) and (exists_inflow_bool):
                        i_in_list = True
                        sublist[1].append(s)
                        sublist[2].append(ls_is)
                #CASE B: THE VARIABLE IS NOT DEFINED IN ROWS2 => ADD THE LINK TO THE DATAFRAME        
                if (i_in_list == False) and (exists_inflow_bool):
                    rows2.append([inflow, [s], [ls_is], False])
            #Store outflows (o -> s)
            if exists_outflow_bool:
                o_in_list_array = {var:False for var in outflow}
                #CASE A: THE VARIABLE IS ALREADY DEFINED IN ROWS2 => ADD THE LINK TO THE EXISTING ROW
                for sublist in rows2:
                    if (sublist and sublist[0] in ls_os_list.keys()) and (exists_outflow_bool):
                            o_in_list_array[sublist[0]] = True
                            sublist[1].append(s)
                            sublist[2].append(ls_os_list[sublist[0]])
                #CASE B: THE VARIABLE IS NOT DEFINED IN ROWS2 => ADD THE LINK TO THE DATAFRAME  
                for i in range(len(o_in_list_array)):    
                    key = next(islice(o_in_list_array, i, None))  
                    if (o_in_list_array[key] == False) and (exists_outflow_bool):
                        rows2.append([key, [s], [ls_os_list[key]], False])

        #DELAY and SMOOTH variables
        for v in set(stateful_vars) - set(stocks_flows.keys()):
            """The link score of a pathway which passes through a macro is the composite
            link score of the pathway with the strongest absolute magnitude of its pathway score
            across all pathways through the macro."""
            print(v)

        prev = cur
        print(f"Step completed. Current time: {model_class.t}\n")
        df2 = pd.DataFrame(rows2, columns=categories2)
        df2.set_index("x")
        df2.to_csv(f'link_score_t-{model_class.t}-next.csv')

        # df_list.append(df)
        # df_list_next.append(df2)
        # df.to_csv(f'link_score_t-{model_class.t}.csv')
    # return df_list, df_list_next
    return df, df2


class Link:
    def __init__(self, variable, score=0.0):
        self.variable = variable   # the next VariableSPA
        self.score = score

class VariableSPA:
    def __init__(self, name):
        self.name = name
        self.best_score = 0.0
        self.links = []            # outgoing Links only
        self.visiting = False

class PathScore:
    def __init__(self):
        self.stack = []
        self.origin = None
        self.target = None
        self.paths = set() #Only stores unique paths 
        self.var_list = None

    def add_path_if_unique(self, is_a_loop):
        names = [v.name for v in self.stack]
        # canonical form: rotate so the smallest name comes first,
        # so the same path found from different stocks counts once
        try:
            if is_a_loop:
                i = names.index(min(names))
                self.paths.add(tuple(names[i:] + names[:i]))
                print(f"Path for target {self.target.name}: {tuple(names[i:] + names[:i])}\n")
            else:
                self.paths.add(tuple(names))
                print(f"Path from {self.origin.name} to target {self.target.name}: {tuple(names)}\n")
        except (ValueError):
            self.paths.add(tuple())
            print(f"Path for target {self.target.name}: {tuple()}\n")
            


    def check_outbound_uses(self, variable, score):
        if variable is self.target and self.stack:
            self.add_path_if_unique(self.origin is self.target)
            return
        # Never re-enter a variable already on the current path
        # (cycles that don't go through the target).
        if variable.visiting:
            return
        # if score < variable.best_score:
        if abs(score) < variable.best_score:
            return
        # variable.best_score = score
        variable.best_score = abs(score)
        variable.visiting = True
        self.stack.append(variable)
        for link in variable.links:
            self.check_outbound_uses(link.variable, score * link.score)
        variable.visiting = False
        self.stack.remove(variable)

    def sorting_ls(self, link):
        score = link.score
        if link.score > 0:
            score += 1e-16
        return abs(score)

    def string_to_VariableSPA(self, string_list):
        variableSPA_list = []
        for var_name in string_list:
            for varSPA in self.var_list:
                if var_name == varSPA.name:
                    variableSPA_list.append(varSPA)
        return variableSPA_list



    def df_to_VariableSPA(self, df_links, stocks_flows):
        var_list = []
        stock_list = []
        for _, row in df_links.iterrows():
            var_name = row["x"]
            next_links_list = []
            #Check if the variable has been registered earlier
            var_variable = next((v for v in var_list if v.name == var_name), None)
                #If it is not registered
            if var_variable == None:
                var_variable = VariableSPA(var_name)
                var_list.append(var_variable)
                #Check if the next_variable is a stock
                if var_name in stocks_flows.keys():
                    stock_list.append(var_variable)
            #Fill the Links argument of var_variable (wether it was already registered or not)
            for i in range(len(row["z"])):
                next_name = row["z"][i]
                next_variable = next((v for v in var_list if v.name == next_name), None)
                #If it is not registered
                if next_variable == None:
                    next_variable = VariableSPA(next_name)
                    var_list.append(next_variable)
                    #Check if the next_variable is a stock
                    if next_name in stocks_flows.keys():
                        stock_list.append(next_variable)
                #Register the link and its score
                next_link = Link(next_variable, row["ls"][i])
                next_links_list.append(next_link)
            #THE LINKS NEED TO BE SORTED SO THAT THE FIRST LINK HAS THE BIGGEST (ABSOLUTE VALUE) SCORE
            next_links_list.sort(reverse=True, key=self.sorting_ls)
            # Fill the var_variable links with the outgoing links
            var_variable.links = next_links_list
            # # Create a sepparate list of variables that are stocks
            # if row["stock_bool"] == True:
            #     stock_list.append(var_variable)
        return var_list, stock_list


    def strongest_path_algorithm(self, origin, target):
        self.paths = set()
        self.origin = origin
        for i in range(len(target)):        
            #reset state for every target
            for v in self.var_list: 
                v.best_score = 0.0
                v.visiting = False
            self.stack = []
            self.target = target[i]
            self.check_outbound_uses(origin, 1.0)
        return self.paths

    def path_score(self, path_set):
        path_score_list = []
        relative_path_score_list = []
        path_variables_list = [] #To not repeat another for path
        for path in path_set:
            final_link_score = 1
            #EACH PATH STORES A SET OF STRINGS IN ORDER
            empty_link_score_bool = False
            for i in range(len(path)):
                var = path[i]
                var_variable = next((v for v in self.var_list if v.name == var), None)
                for link in var_variable.links:
                    if link.variable.name == path[(i+1)%len(path)]:
                        var_link_score = link.score
                        final_link_score = final_link_score * var_link_score
                        #Do not include links with link score == 0
                        if final_link_score == 0:
                            empty_link_score_bool = True
                            break
            if not empty_link_score_bool:
                path_score_list.append(final_link_score)
                path_variables_list.append(path)
        #Compute relative path scores
        total_path_score = sum(abs(x) for x in path_score_list)
        for i in range(len(path_score_list)):
            path_s = path_score_list[i]
            path_vars = path_variables_list[i]
            relative_path_score_list.append([path_s, path_s/total_path_score, path_vars])
        return relative_path_score_list