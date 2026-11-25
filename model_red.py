import pandas as pd
import os
import ast
import numpy as np

class Model_red():
    def __init__(self):
        #Pair set thresholds
        self.max_relevance_so_threshold = 0
        self.relative_max_relative_so_threshold = 0
        self.mean_relevance_so_threshold = 0
        #~~~~~~~       ~~~~~~~~       ~~~~~~~~~~~
        self.max_relevance_ss_threshold = 0
        self.relative_max_relative_ss_threshold = 0
        self.mean_relevance_ss_threshold = 0
        #Loop set thresholds
        self.max_global_loop_relevance_threshold = 0
        self.relative_max_loop_threshold = 0
        self.mean_global_loop_relevance_threshold = 0
        #Loop set of stocks we need to preserve
        self.loop_set = set()
        #Threshold params
        self.rel_factor=1.2
        self.max_relevance=0.4
        self.mean_relevance=0.15

    def nrmse(self, full, red, how="range"):
        max_length = min(len(full), len(red))
        if len(full) == max_length:
            red = red[:max_length]
        else:
            full = full[:max_length]
        err = np.sqrt(np.mean((full - red) ** 2))
        scale = (full.max() - full.min()) if how == "range" else full.mean()
        return err / scale if scale != 0 else np.nan
    
    def import_reduction_dfs(self, base_output_path):
        scenario_folder_list = ["base_scenario", "high_electrification_scenario", "low_electrification_scenario", "unstable_policy_scenario"]
        df_list = []
        for scenario in scenario_folder_list:
            loop_summary = pd.read_csv(os.path.join(base_output_path, scenario, "s_global_loop_relevance_summary.csv"))
            so_overall = pd.read_csv(os.path.join(base_output_path, scenario, "stock_relevance_overall.csv"))
            ss_overall = pd.read_csv(os.path.join(base_output_path, scenario, "s_stock_relevance_overall.csv"))
            df_list.extend([loop_summary, so_overall, ss_overall])
        return df_list

    def set_thresholds(self, df, case_idx):
        """ SETS THE THRESHOLDS FOR THE MODEL REDUCTION PROCESS
        CASE 0 -> LOOP
        CASE 1 -> S-O
        CASE other -> S-S"""
        match case_idx:
            case 0: #LOOP
                #Relative threshold -> 20% increase of equally distributed result
                self.relative_max_loop_threshold = (1/df["max_active_loops"]) * self.rel_factor
                #Max relevance threshold -> 0.4
                self.max_global_loop_relevance_threshold = self.max_relevance
                #Mean relevance threshold -> 0.15
                self.mean_global_loop_relevance_threshold = self.mean_relevance
            case 1: #STOCK - OUTPUT
                #Relative threshold -> 20% increase of equally distributed result
                self.relative_max_relative_so_threshold = (1/df["max_active_outputs"]) * self.rel_factor
                #Max relevance threshold -> 0.4
                self.max_relevance_so_threshold = self.max_relevance
                #Mean relevance threshold -> 0.15
                self.mean_relevance_so_threshold = self.mean_relevance
            case _: #STOCK - STOCK
                #Relative threshold -> 20% increase of equally distributed result
                self.relative_max_relative_ss_threshold = (1/df["max_active_outputs"]) * self.rel_factor
                #Max relevance threshold -> 0.4
                self.max_relevance_ss_threshold = self.max_relevance
                #Mean relevance threshold -> 0.15
                self.mean_relevance_ss_threshold = self.mean_relevance

    
    def check_loop_scores(self, loop_summary_df):
        """
        OBJECTIVE -> FIND ALL THE STOCKS THAT NEED TO BE PRESERVED AFTER THE REDUCTION"""
        #CHECK STOCK-STOCK LOOPS (IF THERE EXISTS LOOPS FOR STOCK-OUTPUT, MEANS THAT SOME OUTPUT IS A STOCK ITSELF)
        for i in range(loop_summary_df.shape[0]):
            #Set the thresholds
            self.set_thresholds(loop_summary_df.iloc[i], 0)
            if loop_summary_df.loc[i, "mean_global_loop_relevance_all_steps"] >= self.mean_global_loop_relevance_threshold:
                stocks_in_path_str = loop_summary_df.loc[i, "stocks_in_path"]
                stocks_in_path = ast.literal_eval(stocks_in_path_str)
                for stock in stocks_in_path:
                    self.loop_set.add(stock)
                print(f"Because loop L{i} has mean loop relevance: {loop_summary_df.loc[i, "mean_global_loop_relevance_all_steps"]} over threshold {self.mean_global_loop_relevance_threshold}, we should include {stocks_in_path} as our necessary stocks")
            elif (loop_summary_df.loc[i, "max_global_loop_relevance"] >= self.max_global_loop_relevance_threshold) and (loop_summary_df.loc[i, "max_relative_global_loop_score"] >= self.relative_max_loop_threshold):
                stocks_in_path_str = loop_summary_df.loc[i, "stocks_in_path"]
                stocks_in_path = ast.literal_eval(stocks_in_path_str)
                for stock in stocks_in_path:
                    self.loop_set.add(stock)
                print(f"Because loop L{i} has max loop relevance: {loop_summary_df.loc[i, "max_global_loop_relevance"]} and max rel loop score: {loop_summary_df.loc[i, "max_relative_global_loop_score"]} over thresholds {self.max_global_loop_relevance_threshold} and {self.relative_max_loop_threshold}, we should include {stocks_in_path} as our necessary stocks")
        # print(self.loop_set)

    def check_stock_stock_relations(self, stock_pruning_candidate, ss_pair_summary_df):
        """BOOL THAT INDICATES IF, AFTER GOING THROUGH THE STOCK-STOCK RELATIONS, IT IS STILL A PLAUSIBLE CANDIDATE FOR PRUNING"""
        for i in range(ss_pair_summary_df.shape[0]):
            stock_output_bool = ss_pair_summary_df.loc[i, "output"] == stock_pruning_candidate 
            stock_input_bool = ss_pair_summary_df.loc[i, "origin"] == stock_pruning_candidate
            # Set thresholds
            self.set_thresholds(ss_pair_summary_df.iloc[i], 2)
            if (stock_output_bool and not stock_input_bool):
                if ss_pair_summary_df.loc[i, "mean_relevance"] >= self.mean_relevance_ss_threshold:
                    #IS RELEVANT FOR SOME STOCK-STOCK RELATION --> CANNOT PRUNE IT
                    print(f"STOCK {stock_pruning_candidate} has stock-STOCK mean relevance {ss_pair_summary_df.loc[i, "mean_relevance"]} with stock {ss_pair_summary_df.loc[i, "origin"]}, over threshold {self.mean_relevance_ss_threshold}")
                    return False
                elif (ss_pair_summary_df.loc[i, "max_relevance"] >= self.max_relevance_ss_threshold) and (ss_pair_summary_df.loc[i, "relative_max_relevance"] >= self.relative_max_relative_ss_threshold):
                    #IS RELEVANT FOR SOME STOCK-STOCK RELATION --> CANNOT PRUNE IT
                    print(f"STOCK {stock_pruning_candidate} has stock-STOCK max relevance {ss_pair_summary_df.loc[i, "max_relevance"]} and relative max relevance {ss_pair_summary_df.loc[i, "relative_max_relevance"]} with stock {ss_pair_summary_df.loc[i, "origin"]}, over thresholds {self.max_relevance_ss_threshold} and {self.relative_max_relative_ss_threshold}")
                    return False
                else:
                    #IT IS STILL CONSIDERED AS A PRUNING CANDIDATE
                    continue

            elif (not stock_output_bool and stock_input_bool):
                if ss_pair_summary_df.loc[i, "mean_relevance"] >= self.mean_relevance_ss_threshold:
                    #IS RELEVANT FOR SOME STOCK-STOCK RELATION --> CANNOT PRUNE IT
                    print(f"STOCK {stock_pruning_candidate} has STOCK-stock mean relevance {ss_pair_summary_df.loc[i, "mean_relevance"]} with stock {ss_pair_summary_df.loc[i, "output"]}, over threshold {self.mean_relevance_ss_threshold}")
                    return False
                elif (ss_pair_summary_df.loc[i, "max_relevance"] >= self.max_relevance_ss_threshold) and (ss_pair_summary_df.loc[i, "relative_max_relevance"] >= self.relative_max_relative_ss_threshold):
                    #IS RELEVANT FOR SOME STOCK-STOCK RELATION --> CANNOT PRUNE IT
                    print(f"STOCK {stock_pruning_candidate} has STOCK-stock max relevance {ss_pair_summary_df.loc[i, "max_relevance"]} and relative max relevance {ss_pair_summary_df.loc[i, "relative_max_relevance"]} with stock {ss_pair_summary_df.loc[i, "output"]}, over thresholds {self.max_relevance_ss_threshold} and {self.relative_max_relative_ss_threshold}")
                    return False
                else:
                    #IT IS STILL CONSIDERED AS A PRUNING CANDIDATE
                    continue
        return True

    def check_pair_scores(self, so_pair_summary_df, ss_pair_summary_df):
        """
        OBJECTIVE -> 1.FIND THE  LEAST RELEVANT STOCK-OUTPUT RELATIONS"""
        stock_pruning_dict = dict()
        for output in set(so_pair_summary_df["output"]):
            stock_pruning_candidates_set = set()
            for i in range(so_pair_summary_df.shape[0]):
                stock_pruning_candidate = (so_pair_summary_df.loc[i, "origin"])
                #1. Check that the stock is not included in the protected stock set obtained from the loop score analysis
                if stock_pruning_candidate not in self.loop_set:
                    #2. Check the  stock-output relations
                    output_bool = so_pair_summary_df.loc[i, "output"] == output
                    #$ Set thresholds
                    self.set_thresholds(so_pair_summary_df.iloc[i], 1)
                    if output_bool:
                        if (so_pair_summary_df.loc[i, "mean_relevance"] < self.mean_relevance_so_threshold):
                            if ((so_pair_summary_df.loc[i, "max_relevance"] < self.max_relevance_so_threshold) and (so_pair_summary_df.loc[i, "relative_max_relevance"] < self.relative_max_relative_so_threshold)):
                                #3. Check the stock-stock relations
                                still_candidate_bool = self.check_stock_stock_relations(stock_pruning_candidate, ss_pair_summary_df)
                                if still_candidate_bool:
                                    stock_pruning_candidates_set.add(stock_pruning_candidate) 
                            else:
                                #IS RELEVANT FOR SOME STOCK-OUTPUT RELATION --> CANNOT PRUNE IT
                                print(f"STOCK {stock_pruning_candidate} has STOCK-output max relevance {so_pair_summary_df.loc[i, "max_relevance"]} and relative max relevance {so_pair_summary_df.loc[i, "relative_max_relevance"]} with output {output}, over thresholds {self.max_relevance_so_threshold} and {self.relative_max_relative_so_threshold}")
                        else:
                            #IS RELEVANT FOR SOME STOCK-OUTPUT RELATION --> CANNOT PRUNE IT
                            print(f"STOCK {stock_pruning_candidate} has STOCK-output mean relevance {so_pair_summary_df.loc[i, "mean_relevance"]} with output {output}, over threshold {self.mean_relevance_so_threshold}")
                    else:
                        continue           
            stock_pruning_dict[output] = stock_pruning_candidates_set
        return stock_pruning_dict
    
    def model_reduction(self, df_list):
        """ APPLY THE MODEL REDUCTION"""
        #Retrieve the dataframes
        base_loop_summary_df = df_list[0]
        base_so_overall = df_list[1]
        base_ss_overall = df_list[2]
        low_loop_summary_df = df_list[3]
        low_so_overall = df_list[4]
        low_ss_overall = df_list[5]
        high_loop_summary_df = df_list[6]
        high_so_overall = df_list[7]
        high_ss_overall = df_list[8]
        unstable_loop_summary_df = df_list[9]
        unstable_so_overall = df_list[10]
        unstable_ss_overall = df_list[11]
        #1st: Check the loop scores -> Identify stocks that are part of relevant loops (cannot prune them)
        self.loop_set = set()
        print("\n\nBASE LOOP ANALYSIS")
        self.check_loop_scores(base_loop_summary_df)
        print("\n\nLOW LOOP ANALYSIS")
        self.check_loop_scores(low_loop_summary_df)
        print("\n\nHIGH LOOP ANALYSIS")
        self.check_loop_scores(high_loop_summary_df)
        print("\n\nUNSTABLE LOOP ANALYSIS")
        self.check_loop_scores(unstable_loop_summary_df)
        print(f"The following stocks are PROHIBITED to be eliminated:\n{self.loop_set}")
        #2nd: Check which are the pairs that are LEAST relevant, and the stock involved in them for pruning FOR EACH OUTPUT
        print("\n\nBASE PAIR ANALYSIS")
        base_stock_pruning_dict = self.check_pair_scores(base_so_overall, base_ss_overall)
        print("\n\nLOW PAIR ANALYSIS")
        low_stock_pruning_dict = self.check_pair_scores(low_so_overall, low_ss_overall)
        print("\n\nHIGH PAIR ANALYSIS")
        high_stock_pruning_dict = self.check_pair_scores(high_so_overall, high_ss_overall)
        print("\n\nUNSTABLE PAIR ANALYSIS")
        unstable_stock_pruning_dict = self.check_pair_scores(unstable_so_overall, unstable_ss_overall)
        #3rd: Check which are the stocks that are shared in ALL dicts
        dict_list = [base_stock_pruning_dict, low_stock_pruning_dict, high_stock_pruning_dict, unstable_stock_pruning_dict]
        common_stocks_by_key = {
            key: set.intersection(*(d[key] for d in dict_list))
            for key in dict_list[0].keys()
        }
        print(common_stocks_by_key)
        common_stocks_in_output = set.intersection(*common_stocks_by_key.values())
        return list(common_stocks_in_output)
