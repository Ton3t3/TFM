# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO

class vehicle_fleet_sector:
    # vehicle_fleet sector static variables
    DEFAULT = {
        "etruck_lifetime" : 12,
        # INITIAL
        "initial_etruck_fleet_size" : 1,
        "initial_total_truck_fleet_size" : 83025
    }

    STOCK_DEFAULTS = {}

    # readable_name -> canonical key (DEFAULT key / PySD py_name)
    ALIASES = {
        "ETRUCK_LIFETIME": "etruck_lifetime",
        #INITIAL
        "INITIAL_ETRUCK_FLEET_SIZE": "initial_etruck_fleet_size",
        "INITIAL_TOTAL_TRUCK_FLEET_SIZE": "initial_total_truck_fleet_size"
    }

    def __init__(self, model):
        self.model = model.components

    @property
    def ETRUCK_LIFETIME(self):
        """The average operational lifespan of electric vehicles [Year]"""
        return self.model.etruck_lifetime()

    @property
    def INITIAL_ETRUCK_FLEET_SIZE(self): 
        """The starting number of electric trucks in the fleet [Vehicle]"""
        return self.model.initial_etruck_fleet_size()

    @property
    def INITIAL_TOTAL_TRUCK_FLEET_SIZE(self):
        """The starting number of total trucks in the fleet [Vehicle]"""
        return self.model.initial_total_truck_fleet_size()


    def time_for_truck_sales(self):
        return self.model.time_for_truck_sales()

    ## OUTPUTS
    def share_of_electric_truck_in_new_sales(self): 
        """The proportion of the total truck fleet that is sold to the market [Dmnl]"""
        return self.model.etruck_share_in_new_sales()
                
    def share_of_electric_truck_in_total_fleet_size (self): 
        """The proportion of the total truck fleet that is electric [Dmnl]""" 
        return self.model.etruck_share_in_total_fleet()
    
    ## FLOWS
    # Inflows
    def Total_Truck_Sales(self):   
        """Number of new trucks (both electric and diesel) that are sold in each year [Vehicle/Year]"""
        return self.model.total_truck_sales()
    
    def Etruck_Sales(self):
        """Number of new electric trucks that are sold in each year [Vehicle/Year]"""
        return self.model.etruck_sales()
    
    # Outflows
    def Total_Truck_Decommission(self):
        """Number of total trucks that are removed from use in each year [Vehicle/Year]"""
        return self.model._delayfixed_total_truck_decommission()
                
    def Etruck_Decommission(self): 
        """Number of electric trucks that are removed from use in each year [Vehicle/Year]"""
        return self.model._delayfixed_etruck_decommission() 

    ## STOCKS 
    def etruck_Fleet_Size(self): 
        """The total number of electric trucks in the fleet [Vehicle]"""
        return self.model._integ_etruck_fleet_size()
    
    def total_Truck_Fleet_Size(self): 
        """The total number of trucks in the fleet [Vehicle]"""
        return self.model._integ_total_truck_fleet_size()
