# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO

class vehicle_cost_sector:
    # vehicle_cost sector static variables
    DEFAULT = {
        "maintenance_cost_per_km_for_diesel_truck" : 1.32*0,
        "maintenance_cost_per_km_for_etruck" : 0.99*0,
        "diesel_truck_lifetime" : 12,
        "sensitivity_coefficient_for_vehicle_subsidy" : 1,
        "sensitivity_coefficient_for_diesel" : 1,
        "purchase_cost_of_diesel_truck" : 1.7595E+06,#1.76E+06,
        "learning_effect_delay" : 2,
        "average_consumption_per_km_for_diesel_truck" : 0.25,
        # INITIAL
        "initial_purchase_cost_of_etrucks" : 5.5131E+06
    }

    STOCK_DEFAULTS = {
        "_integ_income_of_diesel_stock" : 0,
        "_integ_gov_fund_on_diesel_price" : 0,
        "_integ_gov_vehicle_subsidy_stock" : 0            
    }

    ALIASES = {
        "MAINTENANCE_COST_PER_KM_FOR_DIESEL_TRUCK": "maintenance_cost_per_km_for_diesel_truck",
        "MAINTENANCE_COST_PER_KM_FOR_ETRUCK": "maintenance_cost_per_km_for_etruck",
        "DIESEL_TRUCK_LIFETIME": "diesel_truck_lifetime",
        "sensitivity_coefficient_for_VEHICLE_SUBSIDY": "sensitivity_coefficient_for_vehicle_subsidy",
        "sensitivity_coefficient_for_DIESEL": "sensitivity_coefficient_for_diesel",
        "PURCHASE_COST_OF_DIESEL_TRUCK": "purchase_cost_of_diesel_truck",
        "LEARNING_EFFECT_DELAY": "learning_effect_delay",
        "AVERAGE_CONSUMPTION_PER_KM_FOR_DIESEL_TRUCK": "average_consumption_per_km_for_diesel_truck",
        # INITIAL
        "INITIAL_PURCHASE_COST_OF_ETRUCKS": "initial_purchase_cost_of_etrucks",
        "INITIAL_INCOME_OF_DIESEL_STOCK": "_integ_income_of_diesel_stock",
        "INITIAL_GOV_FUND_ON_DIESEL_PRICE": "_integ_gov_fund_on_diesel_price",
        "INITIAL_GOV_VEHICLE_SUBSIDY_STOCK": "_integ_gov_vehicle_subsidy_stock"
    }

    def __init__(self, model):
        self.model = model.components

    @property
    def MAINTENANCE_COST_PER_KM_FOR_DIESEL_TRUCK(self):
        """[SEK/KM]"""
        return self.model.maintenance_cost_per_km_for_diesel_truck()

    @property
    def MAINTENANCE_COST_PER_KM_FOR_ETRUCK(self):
        """[SEK/KM]"""
        return self.model.maintenance_cost_per_km_for_etruck()

    @property
    def DIESEL_TRUCK_LIFETIME(self):
        """[Year]"""
        return self.model.diesel_truck_lifetime()

    @property
    def sensitivity_coefficient_for_VEHICLE_SUBSIDY(self):
        """Only use for sensitivity analysis [Dmnl]"""
        return self.model.sensitivity_coefficient_for_vehicle_subsidy()

    @property
    def sensitivity_coefficient_for_DIESEL(self):
        """Only use for sensitivity analysis [Dmnl]"""
        return self.model.sensitivity_coefficient_for_diesel()

    @property
    def PURCHASE_COST_OF_DIESEL_TRUCK(self):
        """EV: 5,513,100 SEK/vehicle Diesel: 1,759,500 SEK/vehicle EV: 470,000 EURO/vehicle Diesel: 150,000 EURO/vehicle EUR to SEK: 11.73 (14 May 2024) [SEK/Vehicle]"""
        return self.model.purchase_cost_of_diesel_truck()

    @property
    def LEARNING_EFFECT_DELAY(self):
        """Based on expert opinion [Year]"""
        return self.model.learning_effect_delay()

    @property
    def AVERAGE_CONSUMPTION_PER_KM_FOR_DIESEL_TRUCK(self):
        """100 km, 27 litre ICCT report, table 1 page 9 = 0.27 [Litre/KM]"""
        return self.model.average_consumption_per_km_for_diesel_truck()

    @property
    def INITIAL_PURCHASE_COST_OF_ETRUCKS(self):
        return self.model.initial_purchase_cost_of_etrucks()

    ##
    def time_for_diesel_price(self):
        return self.model.time_for_diesel_price()

    def DIESEL_RETAIL_PRICE(self):
        """"swedish diesel price energimyndigheten [SEK/Litre]"""
        return self.model.diesel_retail_price()
    
    def DIESEL_RETAIL_PRICE__SEK_per_kWh(self):
        """[SEK/kWh]"""
        return self.model.diesel_retail_price_sekkwh()

    ##
    def GOV_SUBSIDY_PERCENTAGE_ON_DIFFERENCE_BETWEEN_ETRUCK_AND_DIESEL_TRUCK_PURCHASE_COSTS(self): 
        """Klimatklivet:Funding 40% of the additional cost compared to a similar conventional truck. [Dmnl]"""
        return self.model.gov_subsidy_percentage_on_difference_between_etruck_diesel_truck_purchase_costs()
    ##
    def cost_of_diesel_fuel_per_km(self):
        """[SEK/KM]"""
        return self.model.cost_of_diesel_fuel_per_km()
    
    def annual_fuel_consumption__Litr__per_diesel_truck(self):
        """[Litre/(Vehicle*Year)]"""
        return self.model.annual_fuel_consumption_litr_per_diesel_truck()
    
    def annual_operation_cost__Opex__of_each_diesel_truck(self):
        """[SEK/(Vehicle*Year)]"""
        return self.model.annual_operation_cost_opex_of_each_diesel_truck()
    
    def discount_factor_for_diesel_truck(self):
        """[Year]"""
        return self.model.discount_factor_for_diesel_truck()
    
    def diesel_truck_discounted_total_opex(self):
        """[SEK/Vehicle]"""
        return self.model.diesel_truck_discounted_total_opex()
    
    def diesel_truck_total_cost(self):
        """[SEK/Vehicle]"""
        return self.model.diesel_truck_total_cost()
    
    def discount_factor_for_etruck(self):
        """[Year]"""
        return self.model.discount_factor_for_etruck()

    ##
    def cost_of_electricity_per_km(self): 
        """[SEK/KM]"""
        return self.model.cost_of_electricity_per_km()
    
    def annual_operation_cost__opex__of_each_etruck(self): 
        """[SEK/(Vehicle*Year)]"""
        return self.model.annual_operation_cost_opex_of_each_etruck()
    
    def etruck_discounted_total_Opex(self): 
        """[SEK/Vehicle]"""
        return self.model.etruck_discounted_total_opex()
                              
    #Time function dependant - DIRECT
    def purchase_cost_gap(self): 
        """[SEK/Vehicle]"""
        return self.model.purchase_cost_gap()
    
    def purchase_cost_paid_by_freight_companies(self): 
        """Price e-truck - Subsidy percentage* (Diffference between electric and regular) [SEK/Vehicle]"""
        return self.model.purchase_cost_paid_by_freight_companies()
    
    def electric_truck_total_cost(self): 
        """[SEK/Vehicle]"""
        return self.model.electric_truck_total_cost()
    
    ## FLOWS
    # Inflows
    def Annual_Income_of_Diesel__inflow(self): 
        """[SEK/Year]"""
        return self.model.annual_income_of_diesel_inflow()
    
    def Annual_Gov_Fund_on_Diesel_Price(self): 
        """Positive amounts show that governments pay subsidies on DIESEL Negative amounts show that governments receive taxes on DIESEL"""
        return self.model.annual_gov_fund_on_diesel_price()
    
    def Annual_gov_subsidy_on_vehicle_purchase_cost(self): 
        """[SEK/Year]"""
        return self.model.annual_gov_subsidy_on_vehicle_purchase_cost()

    # Outflows
    def Decrease_in_purchase_cost_of_etruck(self): 
        """[SEK/(Year*Vehicle)]"""
        return self.model.decrease_in_purchase_cost_of_etruck()

    # XTRA (Using two previous stocks)
    def Diesel_Truck_Fleet_Size(self): 
        """[Vehicle]"""
        return self.model.diesel_truck_fleet_size()
    
    ## STOCKS
    def purchase_Cost_of_Etrucks(self): 
        """EV: 5,513,100 SEK/vehicle Diesel: 1,759,500 SEK/vehicle EV: 470,000 EURO/vehicle Diesel: 150,000 EURO/vehicle EUR to SEK: 11.73 (14 May 2024) [SEK/Vehicle]"""
        return self.model._integ_purchase_cost_of_etrucks()
    
    def income_of_Diesel__Stock(self): 
        """[SEK]"""
        return self.model._integ_income_of_diesel_stock()
    
    def gov_Fund_on_Diesel_Price(self): 
        """[SEK]"""
        return self.model._integ_gov_fund_on_diesel_price()
    
    def gov_vehicle_subsidy_stock(self): 
        """[SEK]"""
        return self.model._integ_gov_vehicle_subsidy_stock()
    
