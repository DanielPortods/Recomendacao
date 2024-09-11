BLUE = "Blue"
GREEN = "Green"

class Tariff():
    def is_green():
        ...


class BlueTariff(Tariff):
    _instance = None
     
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BlueTariff, cls).__new__(cls)
        return cls._instance        
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.peak_tusd_in_reais_per_kw = 44.10
            self.peak_tusd_in_reais_per_mwh = 98.56
            self.peak_te_in_reais_per_mwh = 450.99
            self.off_peak_tusd_in_reais_per_kw = 22.46
            self.off_peak_tusd_in_reais_per_mwh = 98.56
            self.off_peak_te_in_reais_per_mwh = 287.37

class GreenTariff:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GreenTariff, cls).__new__(cls)
        return cls._instance        
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.peak_tusd_in_reais_per_mwh = 1168.19
            self.peak_te_in_reais_per_mwh = 450.99
            self.off_peak_tusd_in_reais_per_mwh = 98.56
            self.off_peak_te_in_reais_per_mwh = 287.37
            self.na_tusd_in_reais_per_kw = 22.46

#Tarifas obtidas do site da Copel https://www.copel.com/site/copel-distribuicao/tarifas-de-energia-eletrica/
#Acesso em 13/12/2023