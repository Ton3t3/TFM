#1. calculate link scores
#   How? 
#       a. check every function from the model
#       b. calculate link score for each variable used in the function
#   How can I identify the variables used in a function?

# from xxlimited import Str

import numpy as np
import pandas as pd

def snapshot(model, names):
    """**Takes a snapshot of the model's current state for all the variables of the model**"""
    res = {n: model[n] for n in names}
    res["time"] = model.components.time()
    return res

def filter_dependencies(model):
    stateful_vars = []
    filtered_deps = {}
    for key, val in model.dependencies.items():
        if (key not in ["saveper", "time_step", "final_time", "initial_time", "OUTPUTS"]) and (key[0] != "_"):
            if (getattr(model.components, key).type == "Stateful"):
                val_dict = dict()
                for i_key, i_val in val.items():
                    if "_" in i_key[0]:
                        #References a _integ / _delayfixed / _smooth
                        stateful_var_dependencies = model.dependencies[i_key]
                        val_dict.update(stateful_var_dependencies["initial"] | stateful_var_dependencies["step"])
                    else:
                        val_dict[i_key] = i_val
                stateful_vars.append(key)
                filtered_deps[key] = val_dict
            else:
                filtered_deps[key] = val
    dynamic_vars = [key for key, val in filtered_deps.items() if (len(val) != 0) and (key not in [var for var in stateful_vars if (getattr(model.components, var).subtype != "Integ")])] #Not including _smooth and _delayfixed
    return filtered_deps, dynamic_vars

class LinkScore():
    def __init__(self):
        self.ls_dict = dict()
        self.model = None
        self.cur = None
        self.prev = None
        self.z = None
        self.x = None
        self.s = None

    def eval_z(self, inputs, originals, cur_z=None):
        # replace inputs by constants
        self.model.set_components(inputs)  
        self.model.clean_caches()      
        # recompute z with the corresponding past and current values                  
        val = self.model[self.z]
        # restore the original equations
        for key, function in originals.items():       
            setattr(self.model.components, key, function)
        self.model.clean_caches()
        val_restored = self.model[self.z]
        if abs(cur_z - val_restored) != 0:
            print(f"WARNING: Restored {self.z} value {val_restored} does not match current value {cur_z}")
        return val

    def is_a_flow_bool(self, stocks_flows):
        check_if_inflow = self.x in stocks_flows[self.z]
        check_if_outflow = stocks_flows[self.z][1] is not None and self.x in stocks_flows[self.z][1]
        return  check_if_inflow or check_if_outflow

    def dz_x_calc(self, filtered_deps):
        inputs = {d: self.prev[d] for d in filtered_deps[self.z] if d != self.x}
        inputs[self.x] = self.cur[self.x]
        originals = {d: getattr(self.model.components, d) for d in inputs}
        z_x = self.eval_z(inputs, originals, cur_z=self.cur[self.z])
        dz_x = z_x - self.prev[self.z]
        return dz_x

    def link_score_calc(self, dz_x):
        dz,dx = self.cur[self.z] - self.prev[self.z], self.cur[self.x] - self.prev[self.x]
        ls = 0.0 if (dz == 0 or dx == 0) else abs(dz_x/dz) * np.sign(dz_x/dx)
        return ls

    def variable_dict_storage(self, filtered_deps, is_stateful_bool, stocks_flows):
        if is_stateful_bool:
            #ONLY INCLUDE THE LINKS THAT ARE NOT FLOWS
            if self.is_a_flow_bool(stocks_flows):
                ls = None
            else:
                #IS AN INITIAL VARIABLE -> LS = 0
                ls = 0
        else:
            dz_x = self.dz_x_calc(filtered_deps)
            ls = self.link_score_calc(dz_x)
        #STORE THE LINK SCORES IN THE DICTIONARY
        if ls is not None:
            if self.x not in self.ls_dict:
                self.ls_dict[self.x] = [(self.z, ls)]
            else:
                self.ls_dict[self.x].append((self.z, ls))

    def get_flows(self, stocks_flows):
        exists_inflow = True
        exists_outflow = True
        #Inflow
        inflow = stocks_flows[self.s][0]
        if inflow == None:
            inflow_value = 0
            exists_inflow = False
        else: 
            inflow_value = self.prev[inflow]
        #Outflows
        outflow = stocks_flows[self.s][1]
        if outflow == None:
            outflow_value_list = [0]
            exists_outflow = False
        else:
            #There exist one of the stocks that has two outflows
            outflow_value_list = [self.prev[o] for o in outflow]
        total_outflow_value = sum(outflow_value_list)

        #Case_bool: 1 -> Inflow, None  2 -> None, Outflow   3 -> Inflow, Outflow
        case_bool = int(exists_inflow) + 2*int(exists_outflow)

        return inflow, inflow_value, outflow, outflow_value_list, total_outflow_value, case_bool


    def stocks_dict_storage(self, stocks_flows):
        #1. IDENTIFY THE FLOWS
        inflow, inflow_value, outflow, outflow_value_list, total_outflow_value, case_bool = self.get_flows(stocks_flows)
        #2. CALCULATE LINK SCORES
        ls_is = 0
        ls_os_list = dict()
        match case_bool:
            case 1: #CASE I -> S -> NONE
                if inflow_value == 0:
                    ls_is = 0
                else:
                    ls_is = 1
            case 2: #CASE NONE -> S -> O
                for i in range(len(outflow_value_list)):
                    if outflow_value_list[i] == 0:
                        ls_os_list[outflow[i]] = 0
                    else:
                        ls_os_list[outflow[i]] = 1
            case _: # CASE I -> S -> O
                ls_is = abs(inflow_value/(inflow_value-total_outflow_value))
                for i in range(len(outflow_value_list)):
                    ls_os_list[outflow[i]] = abs(outflow_value_list[i]/(inflow_value-total_outflow_value))
        #3. STORE THE LINK SCORES
        #Store inflows (i -> s)
        if case_bool != 2:
            #CASE A: THE VARIABLE IS ALREADY DEFINED IN THE DICT => ADD THE LINK TO THE EXISTING ROW
            if (inflow in self.ls_dict.keys()):
                self.ls_dict[inflow].append((self.s, ls_is))
            #CASE B: THE VARIABLE IS NOT DEFINED IN ROWS2 => ADD THE LINK TO THE DATAFRAME        
            else:
                self.ls_dict[inflow] = [(self.s, ls_is)]
        #Store outflows (o -> s)
        if case_bool != 1:
            for i in range(len(outflow_value_list)):
                #CASE A: THE VARIABLE IS ALREADY DEFINED IN ROWS2 => ADD THE LINK TO THE EXISTING ROW
                if (outflow[i] in self.ls_dict.keys()):   
                    self.ls_dict[outflow[i]].append((self.s, ls_os_list[outflow[i]]))                  
                #CASE B: THE VARIABLE IS NOT DEFINED IN ROWS2 => ADD THE LINK TO THE DATAFRAME  
                else:
                    self.ls_dict[outflow[i]] = [(self.s, ls_os_list[outflow[i]])]

    def dict_to_df(self, model_class):
        rows = [
            {
                "x": x,
                "z": [z for z, _ in targets],
                "ls": [ls for _, ls in targets]
            }
            for x, targets in self.ls_dict.items()
        ]
        df = pd.DataFrame(rows)
        df.to_csv(f"link_score_t-{model_class.t}-next2.csv", index=False)
        return df

    def link_score(self, model, model_class, stocks_flows):
        #Filtered dependencies dict
        filtered_deps, z_with_links = filter_dependencies(model)

        n_steps = 1
        #List of variables in the model
        names = list(filtered_deps.keys())
        prev = snapshot(model, names)
        for _ in range(n_steps):
            model.step(1)
            cur = snapshot(model, names)
            #Initialize the class
            self.model = model
            self.cur = cur
            self.prev = prev
            # Aux/flow variables, not stocks or stateful vars
            for z in z_with_links:             
                self.z = z
                for x in filtered_deps[z]:
                    self.x = x
                    # IN CASE THE CURRENT Z IS A STOCK
                    is_stateful_bool = (getattr(model.components, z).type == "Stateful")
                    self.variable_dict_storage(filtered_deps, is_stateful_bool, stocks_flows)

            #Stock pipe related links [ ls(i->s) and ls(o->s)]
            for s in stocks_flows.keys():
                self.s = s
                self.stocks_dict_storage(stocks_flows)

            #DELAY and SMOOTH variables
            # for v in set(stateful_vars) - set(stocks_flows.keys()):
            #     """The link score of a pathway which passes through a macro is the composite
            #     link score of the pathway with the strongest absolute magnitude of its pathway score
            #     across all pathways through the macro."""
            #     print(v)

            prev = cur
            print(f"Step completed. Current time: {model_class.t}\n")

            #Store the dict as a dataframe
            df = self.dict_to_df(model_class)
        return df


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