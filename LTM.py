#1. calculate link scores
#   How? 
#       a. check every function from the model
#       b. calculate link score for each variable used in the function
#   How can I identify the variables used in a function?

# from xxlimited import Str

import numpy as np
import pandas as pd
import os
import re

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
        # df.to_csv(f"link_score_t-{model_class.t}-next2.csv", index=False)
        return df

    def link_score(self, model_class, stocks_flows, filtered_deps, z_with_links):     
        # Aux/flow variables, not stocks or stateful vars
        for z in z_with_links:             
            self.z = z
            for x in filtered_deps[z]:
                self.x = x
                # IN CASE THE CURRENT Z IS A STOCK
                is_stateful_bool = (getattr(self.model.components, z).type == "Stateful")
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
        self.stock_list = None
        self.var_list = None
        #For the path_score algorithm
        self.path = None
        #For the backward path search algorithm
        self.stocks_related_to_output_prev = set()
        self.stocks_related_to_output_total = set()

    def add_path_if_unique(self, is_a_loop):
        """Adds the current path to the class set of paths.

        Parameters
        ----------
        is_a_loop : bool
            Bool that indicates that the current path forms a loop

        Returns
        -------
        None
        """
        names = [v.name for v in self.stack]
        # canonical form: rotate so the smallest name comes first,
        # so the same path found from different stocks counts once
        try:
            if is_a_loop:
                # stack is [T, a, b, ..., T]; drop the closing duplicate
                cycle = names[:-1]
                i = cycle.index(min(cycle))
                cycle = cycle[i:] + cycle[:i]
                self.paths.add(tuple(cycle))
                # print(f"Path for target {self.target.name}: {tuple(names[i:] + names[:i])}\n")
            else:
                self.paths.add(tuple(names))
                # print(f"Path from {self.origin.name} to target {self.target.name}: {tuple(names)}\n")
        except (ValueError):
            self.paths.add(tuple())
            # print(f"Path for targets {self.target.name}: {tuple()}\n")
            


    def check_outbound_uses(self, variable, score):
        """Executes the Path Score Algorithm.

        Parameters
        ----------
        variable : `VariableSPA`
            Current variable of the path used to check its `Link` links.
        score : float
            Current score of the path score.

        Returns
        -------
        None
        """
        if variable is self.target and self.stack:
            ## Add the target variable to the path stack
            self.stack.append(variable)
            self.add_path_if_unique(self.origin is self.target)
            self.stack.pop()
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
        """Sorts the elements of the links from higher to lower Link Score.

        Parameters
        ----------
        link : `Link`
            Link that wants to be sorted.

        Returns
        -------
        abs(score) : float
            Score of the Link Score of the analyzed **link** in absolute value.
        """
        score = link.score
        if link.score > 0:
            score += 1e-16
        return abs(score)

    def list_to_VariableSPA(self, string_list):
        """Transforms a list of strings to a list of `VariableSPA` elements.

        Parameters
        ----------
        string_list : List of str
            List of variables in **str** form.

        Returns
        -------
        variableSPA_list : List of `VariableSPA`
            Translated list of variables into `VariableSPA` class.
        """
        variableSPA_list = []
        for var_name in string_list:
            for varSPA in self.var_list:
                if var_name == varSPA.name:
                    variableSPA_list.append(varSPA)
        return variableSPA_list

    def df_to_VariableSPA(self, df_links, stocks_flows):
        """Transforms the variables located in the `LinkScore` **df** to a list of `VariableSPA` variables.

        Parameters
        ----------
        df_links : pandas.DataFrame
            DataFrame containing all the links form the model.
        stocks_flows : dict
            Hardcoded dictionary where all the flows from each stock of the model are described.

        Returns
        -------
        var_list : List of `VariableSPA`
            List containing all the variables from the model in `VariableSPA` class
        stock_list : List of `VariableSPA`
            List containing all the stocks from the model in `VariableSPA` class
        """
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
        return var_list, stock_list


    def strongest_path_algorithm(self, origin, target, input_dict):
        """Path finder algorihm used to calculate the path score from **origin** to **target**.

        Parameters
        ----------
        origin : `VariableSPA`
            First variable of the path being analyzed.
        target : list of str
            Target variable of the path being analyzed.

        Returns
        -------
        relative_path_score_dict :
        reduced_relative_path_score_dict :
        """
        self.origin = origin
        self.paths = set()
        #Avoid the error if target is a single variable
        target_norm = target if isinstance(target, list) else [target]
        for i in range(len(target_norm)):        
            #reset state for every target
            for v in self.var_list: 
                v.best_score = 0.0
                v.visiting = False
            self.stack = []
            self.target = target_norm[i]
            self.check_outbound_uses(origin, 1.0)
        relative_path_score_dict, reduced_relative_path_score_dict = self.path_score(input_dict)
        return relative_path_score_dict, reduced_relative_path_score_dict

    def path_score_calc(self, input_dict):
        """ Calculates the numeric path score of a given path set
            Parameters
            ----------
            None

            Returns
            ----------
            The function will return a **tuple** with two elements:

            * self.path : tuple of str
                Set of variables from the current path that is being analyzed in *path_score* function
            * final_path_score: float
                Final value of the path score calculation"""
        final_path_score = 1
        #Iterate for each variable of the path IN ORDER
        for i in range(len(self.path)):
            if i == 0 and (input_dict and self.path[i] in input_dict):
                continue
            var = self.path[i]
            VariableSPA_var = next((v for v in self.var_list if v.name == var), None)
            for link in VariableSPA_var.links:
                next_var = self.path[(i+1)%len(self.path)]
                if link.variable.name == next_var:
                    var_link_score = link.score
                    final_path_score = final_path_score * var_link_score
                    #If the path score is already 0, it is no use to continue
                    if final_path_score == 0:
                        break
        return (self.path, final_path_score)

    def relative_path_score_calc(self, path_score_list):
        #REMEMBER: path_score_list = [(path, path_score), (path2, path_score2), ...]
        #Compute relative path scores
        total_path_score = sum(abs(path_score[1]) for path_score in path_score_list)
        relative_path_score_dict = {path_score[0] : (path_score[1], path_score[1]/total_path_score if total_path_score != 0 else None) for path_score in path_score_list}
        return relative_path_score_dict


    def dict_to_df(self, relative_path_score_dict, model_class, output_path, origin_name, csv_bool, extra_string = ""):
            rows = [
                {
                    "path_score": path_values[0],
                    "relative_path_score": path_values[1],
                    "path_set": path,
                    "origin": origin_name
                }
                for path, path_values in relative_path_score_dict.items()
            ]
            df = pd.DataFrame(rows)
            if csv_bool:
                df.to_csv(os.path.join(output_path,f'path_score_t-{model_class.t}-{origin_name}'+extra_string+'.csv'))
            return df

    def path_score(self, input_dict):
        path_score_list = []
        reduced_path_score_list = []
        for path in self.paths:
            self.path = path
            #Calculate the path score
            final_path_score_tuple = self.path_score_calc(input_dict)
            #Store the path score result in a list
            path_score_list.append(final_path_score_tuple)
            if final_path_score_tuple[1] != 0:
                reduced_path_score_list.append(final_path_score_tuple)
        #Calculate the relative path score
        return self.relative_path_score_calc(path_score_list), self.relative_path_score_calc(reduced_path_score_list)

    def add_cross_stock_scores(self, df_list, output_name):
        """df_list: one DataFrame per stock (origin) for a single output."""
        # Total absolute path score of each (stock -> output) pair
        totals = [df["path_score"].abs().sum() if not df.empty else 0.0
                for df in df_list]
        # Shared reference: the strongest pair for this output
        reference = max(totals, default=0.0)

        for df, total in zip(df_list, totals):
            if df.empty:
                continue
            df["output"] = output_name
            df["pair_total"] = total
            if reference != 0:
                df["global_relative_path_score"] = df["path_score"] / reference #WATCH OUT!!!
                df["pair_relevance"] = total / reference
            else:
                df["global_relative_path_score"] = 0.0
                df["pair_relevance"] = 0.0
        return df_list

    def path_search(self, inputs: VariableSPA, outputs: VariableSPA, model_class, output_path, full_df_bool, csv_bool, input_dict = {}):
        df_list = []
        for input in inputs:
            relative_path_score_dict, reduced_relative_path_score_dict = self.strongest_path_algorithm(input, outputs, input_dict)
            #To store all the paths
            if full_df_bool:
                df_full = self.dict_to_df(relative_path_score_dict, model_class, output_path, input.name, csv_bool, "_full")
                df_list.append(df_full)
            #To store only the active paths  
            df = self.dict_to_df(reduced_relative_path_score_dict, model_class, output_path, input.name, csv_bool)
            if not df.empty:
                df_list.append(df)

        if not isinstance(outputs, list): # single output -> compare its stocks
            self.add_cross_stock_scores(df_list, outputs.name)
        return df_list

    def backward_get_stock_df(self, df_list, threshold=0.0):
        stocks_related_to_output = set()
        for df in df_list:
            # if df.shape != (0,0):
            if not df.empty and df.loc[0, 'pair_relevance'] >= threshold:
                origin_name = df.loc[0, 'origin']
                stocks_related_to_output.add(origin_name)
        return stocks_related_to_output

    def backward_get_stock(self, model_class, single_output_path):
        stocks_related_to_output = set()
        """*SEARCHES FROM ALL THE CSV FILES THE STOCKS THAT HAVE AN ACTUAL PATH FOR THE OUTPUT AND STORES THEM IN **stocks_related_to_output** VARIABLE*"""
        pattern = re.compile(rf"path_score_t-{re.escape(str(model_class.t))}-(?P<var>.+)\.csv")
        for file in os.listdir(single_output_path):
            m = pattern.fullmatch(file)
            if m is None or "full" in m.string:
                continue
            var = m["var"] 
            csv_file = pd.read_csv(os.path.join(single_output_path, file))
            if csv_file.shape != (0,1):
                stocks_related_to_output.add(var) #Returns the stock as a string
        return stocks_related_to_output        

    def backward_stock_search(self, model_class, output_list, output_path):
        for output in output_list:
            #Get the stocks related to each of the outputs
            full_df_bool = False # If we want to print also the paths with 0 path score
            csv_bool = False # If we want to create csv files from the path search dataframes
            single_output_path = model_class.set_path(output_path + f"-{output.name}", csv_bool)
            df_list = self.path_search(self.stock_list, output, model_class, single_output_path, full_df_bool, csv_bool)
                        
            if csv_bool:
                stocks_related_to_output = self.backward_get_stock(model_class, single_output_path)
            else:
                stocks_related_to_output = self.backward_get_stock_df(df_list)
            new_stocks = [s for s in stocks_related_to_output if s not in self.stocks_related_to_output_total] 
            self.stocks_related_to_output_total |= set(stocks_related_to_output)
            
            if not new_stocks:
                continue
            #rename the path for the next iteration
            new_stocks_list = self.list_to_VariableSPA(new_stocks)
            # self.stocks_related_to_output_prev = stocks_related_to_output.copy()
            self.backward_stock_search(model_class, new_stocks_list, single_output_path)


    def score_stocks_for_output(self, model_class, output, input_names, full_df_bool, input_dict = {}):
        """One search: all discovered stocks -> the root output, one common scale."""
        inputsSPA = self.list_to_VariableSPA(input_names)
        df_list = self.path_search(inputsSPA, output, model_class, "", full_df_bool, False, input_dict)
        frames = [df for df in df_list if not df.empty]
        if not frames:
            return pd.DataFrame()
        scored = pd.concat(frames, ignore_index=True)   # one row per path
        scored["t"] = model_class.t
        return scored