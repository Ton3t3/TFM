# CODE BY EMILIO ANTONIO ZUBIZARRETA PELAYO

class charging_station_availability_sector: 
    # charging_station_availability sector static variables
    DEFAULT = {
        "time_to_build_a_charging_station" : 2,
        # INITIAL
        "initial_charging_stations_under_construction" : (3*90000*1.5)/(0.1*350*8760),
        "initial_charging_stations" : (0.5*90000*1.5)/(0.1*350*8760)
    }

    STOCK_DEFAULTS = {}

    ALIASES = {
        "TIME_TO_BUILD_A_CHARGING_STATION": "time_to_build_a_charging_station",
        # INITIAL
        "INITIAL_CHARGING_STATIONS_UNDER_CONSTRUCTION": "initial_charging_stations_under_construction",
        "INITIAL_CHARGING_STATIONS": "initial_charging_stations"
    }

    def __init__(self, model):
        self.model = model.components

    @property
    def TIME_TO_BUILD_A_CHARGING_STATION(self):
        """"Based on interviews and REEL project report REEL. (2022). Regional Electrified Logistics. [Year]"""
        return self.model.time_to_build_a_charging_station()
    
    @property
    def INITIAL_CHARGING_STATIONS_UNDER_CONSTRUCTION(self):
        """There is a 3 truck difference between 2017 and 2018, and we calculated the demand for initial charging staions based on 350 KW chargers. [Charging stations]"""
        return self.model.initial_charging_stations_under_construction()
                
    @property
    def INITIAL_CHARGING_STATIONS(self):
        """There is 1 truck in the year 2017, and we calculated the demand for initial charging staions based on 350 KW chargers. [Charging stations]"""
        return self.model.initial_charging_stations()

    ##    
    def availability_of_charging_station(self): 
        """[Dmnl]"""
        return self.model.availability_of_charging_station()
     
    # Time dependent variables - DIRECT
    def charging_station_capacity_to_demand_ratio(self): 
        """[Dmnl]"""
        return self.model.charging_station_capacity_to_demand_ratio()
    
    def ratio_etruck_to_charging_station(self): 
        """[Vehicle/Charging stations]"""
        return self.model.ratio_etruck_to_charging_station()
    
    ## FLOWS
    # Infows
    def Building_Charging_Station(self): 
        """[Charging stations/Year]"""
        return self.model.building_charging_station()
    
    # In-betweenflows
    def Finishing_Charging_Station(self): 
        """[Charging stations/Year]"""
        return self.model.finishing_charging_station()
    
    # Outflows
    def Decaying_Charging_Station(self): 
        """[Charging stations/Year]"""
        return self.model._delayfixed_decaying_charging_station()        

    ## STOCKS
    def installed_Charging_Stations(self): 
        """[Charging stations]"""
        return self.model._integ_installed_charging_stations()

    def charging_Stations_under_construction(self): 
        """[Charging stations]"""
        return self.model._integ_charging_stations_under_construction()


