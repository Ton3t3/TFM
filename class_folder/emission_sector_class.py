# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO

class emission_sector:
    #emission sector static variables
    DEFAULT = {
        "swich_for_new_regulation_effect" : 1, 
        "carbon_intensity_of_biofuel" : 361/1000, 
        "carbon_intensity_of_diesel" : 3424/1000, 
        "carbon_intensity_of_electricity_fuel" : 0, 
        "factor_for_correction_emission" : 0.612, 
        "kwh_to_litre_converter" : 9.8 
    }

    STOCK_DEFAULTS = {
        "_integ_governmnet_fund_balance_by_five_levers" : 0,
        "_integ_cumulative_emission_without_any_etrucks" : 10^-9,
        "_integ_cumulative_emission_with_having_etrucks" : 10^-9,
        "_integ_total_gov_funds" : 10^-9
    }

    ALIASES = {
        "SWICH_FOR_NEW_REGULATION_EFFECT": "swich_for_new_regulation_effect",
        "Carbon_intensity_of_biofuel": "carbon_intensity_of_biofuel",
        "Carbon_intensity_of_diesel": "carbon_intensity_of_diesel",
        "Carbon_intensity_of_electricity__fuel": "carbon_intensity_of_electricity_fuel",
        "factor_for_correction_emission": "factor_for_correction_emission",
        "Kwh_to_Litre_converter": "kwh_to_litre_converter",
        # INITIAL
        "INITIAL_GOVERNMENT_FUND_BALANCE_BY_FIVE_LEVERS": "_integ_governmnet_fund_balance_by_five_levers",
        "INITIAL_CUMULATIVE_EMISSION_WITHOUT_ANY_ETRUCKS": "_integ_cumulative_emission_without_any_etrucks",
        "INITIAL_CUMULATIVE_EMISSION_WITH_HAVING_ETRUCKS": "_integ_cumulative_emission_with_having_etrucks",
        "INITIAL_TOTAL_GOV_FUNDS": "_integ_total_gov_funds"
    }

    def __init__(self, model):
        self.model = model.components

    @property
    def SWICH_FOR_NEW_REGULATION_EFFECT(self):
        """[Dmnl]"""
        return self.model.swich_for_new_regulation_effect()

    @property
    def Carbon_intensity_of_biofuel(self):
        """[kgCO2eq/Litre]"""
        return self.model.carbon_intensity_of_biofuel()

    @property
    def Carbon_intensity_of_diesel(self):
        """[kgCO2eq/Litre]"""
        return self.model.carbon_intensity_of_diesel()

    @property
    def Carbon_intensity_of_electricity__fuel(self):
        """driving carbon intensity equal to zero [kgCO2eq/kWh]"""
        return self.model.carbon_intensity_of_electricity_fuel()

    @property
    def factor_for_correction_emission(self):
        """Based on discussion with SCB (Statistikmyndigheten) experts"""
        return self.model.factor_for_correction_emission()

    @property
    def Kwh_to_Litre_converter(self):
        """"Energy content in kWh per liter of diesel fuel Energy content in MJ per liter: 36 MJ Conversion factor: 1 MJ = 0.277778 kWh [kWh/Litre]"""
        return self.model.kwh_to_litre_converter()

    ##
    def time_for_carbon_cost(self):
        return self.model.time_for_carbon_cost()
    
    def time_for_emission_reduction(self):
        return self.model.time_for_emission_reduction()
        
    def CARBON_SOCIETY_COST(self):
        """[SEK/kgCO2eq]"""
        return self.model.carbon_society_cost()

    def annual_fuel_consumption__kWh__per_diesel_truck(self):
        """[kWh/(Vehicle*Year)]"""
        return self.model.annual_fuel_consumption_kwh_per_diesel_truck()
    
    def emission_reduction_based_on_previous_regulation(self):
        """[Dmnl]"""
        return self.model.emission_reduction_based_on_previous_regulation()
    
    def emission_reduction_based_on_new_regulation(self):
        """[Dmnl]"""
        return self.model.emission_reduction_based_on_new_regulation()
    
    def Biofuel_share(self):
        """[Dmnl]"""
        return self.model.biofuel_share()
    
    def Carbon_intensity_of_diesel_fuel_by_considering_biofuel(self):
        """[kgCO2eq/kWh]"""
        return self.model.carbon_intensity_of_diesel_fuel_by_considering_biofuel()
    
    ## DEPENDANT ON TIME - INDIRECT
    def annual_fuel_consumption__kWh__for_diesel_fleet(self): 
        """[kWh/Year]"""
        return self.model.annual_fuel_consumption_kwh_for_diesel_fleet()
    
    def Annual_operational_emission_from_diesel_trucks(self): 
        """[kgCO2eq/Year]"""
        return self.model.annual_operational_emission_from_diesel_trucks()
    
    def Total_annual_emission_from_trucks__tank_to_wheel(self): 
        """[kgCO2eq/Year]"""
        return (self.Annual_operational_emission_from_etrucks+self.Annual_operational_emission_from_diesel_trucks)
          
    def Annual_carbon_cost(self):
        """[SEK/Year]"""
        return self.model.annual_carbon_cost() 

    def Saving_emission_converted_to_money_due_to_electrification(self): 
        """[SEK]"""
        return self.model.saving_emission_converted_to_money_due_to_electrification()

    def Emission_per_kwh__annually(self): 
        """[kgCO2eq/kWh]"""
        return self.model.emission_per_kwh_annually()
    
    # DEPENDANT ON TIME - DIRECT
    def Saving_emission_by_transit_to_electrification(self): 
        """[kgCO2eq]"""
        return self.model.saving_emission_by_transit_to_electrification()
    
    def Annual_operational_emission_from_etrucks(self): 
        """[kgCO2eq/Year]"""
        return self.model.annual_operational_emission_from_etrucks()
    
    def Gov_total_fund_per_vehicle(self): 
        """[SEK/Vehicle]"""
        return self.model.gov_total_fund_per_vehicle()
     
    def total_annual_amount_of_energy(self): 
        """[kWh/Year]"""
        return self.model.total_annual_amount_of_energy()
    
    def Share_of_diesel_truck_in_total_fleet_size(self): 
        """[Dmnl]"""
        return self.model.share_of_diesel_truck_in_total_fleet_size()
    
    def Monetarized_saving_emissions_per_investment_unit_in_electrification(self): 
        """[Dmnl]"""
        return self.model.monetarized_saving_emissions_per_investment_unit_in_electrification()
    
    ## FLOWS
    # Inflows
    def Annual_Gov_Funding_by_Five_Levers(self): 
        """[SEK/Year]"""
        return self.model.annual_gov_funding_by_five_levers()

    def Annual_Emission__without_any_etrucks(self): 
        """[kgCO2eq/Year]"""
        return self.model.annual_emission_without_any_etrucks()

    def Annual_Emission__with_having_etrucks(self): 
        """[kgCO2eq/Year]"""
        return self.model.annual_emission_with_having_etrucks()

    def Annual_Total_Gov_Funds(self): 
        """[SEK/Year]"""
        return self.model.annual_total_gov_funds()
    
    ## STOCKS
    def government_Fund_Balance_by_Five_Levers(self): 
        """[SEK]"""
        return self.model._integ_governmnet_fund_balance_by_five_levers
    
    def cumulative_Emission_without_any_etrucks(self): 
        """small initial value near to zero [kgCO2eq]"""
        return self.model._integ_cumulative_emission_without_any_etrucks()
    
    def cumulative_Emission_with_having_etrucks(self): 
        """small initial value near to zero [kgCO2eq]"""
        return self.model._integ_cumulative_emission_with_having_etrucks()
    
    def total_Gov_Funds(self): 
        """small initial value near to zero [SEK]"""
        return self.model._integ_total_gov_funds()
    
