from glob import glob
import pandas as pd
from commons.Tariff import BlueTariff, GreenTariff, BLUE, GREEN

class SheetsConversor:

    MONTHS = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
              "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    COLUMNS = ['year','month','peak_consumption_in_kwh','off_peak_consumption_in_kwh',
               'peak_measured_demand_in_kw','off_peak_measured_demand_in_kw',
               'contract_peak_demand_in_kw','contract_off_peak_demand_in_kw',"cost_reais", 
               'peak_exceeded_in_kw','off_peak_exceeded_in_kw', 'none']
    
    def __init__(self, sheets_dir) -> None:
        self.path = glob(f"{sheets_dir}/*.xls*")

    def convert(self, target = None, csv_save=False):
        ucs = {}
        stop = False
        for sheet_path in self.path:
            if stop:
                break

            print(f"Reading {sheet_path}...")
            sheet = pd.read_excel(sheet_path, sheet_name=None, 
                                  thousands='.', decimal=',', 
                                  names=self.COLUMNS, header=4)
            
            for uc in sheet:
                if stop:
                    break
                
                name = sheet_path + ' - ' + uc
                
                if target != None and name != target:
                    continue

                sheet[uc].drop(columns=['none'], inplace=True)
                sheet[uc].fillna(0, inplace=True)
                sheet[uc].month = sheet[uc].month.map(self.MONTHS)

                if csv_save:
                    ucs[sheet].to_csv(f"data/{sheet}.csv")

                ucs.update({name: sheet[uc]})
                stop = True if name == target else False

        print(f"Done! {len(ucs)} UCs conveted!")

        flags, contract = self.get_ucs_details(ucs)

        for uc in ucs:
            if flags[uc] == "Skip":
                continue

            ucs[uc].peak_exceeded_in_kw = (ucs[uc].peak_measured_demand_in_kw - ucs[uc].contract_peak_demand_in_kw).clip(0)
            ucs[uc].off_peak_exceeded_in_kw = (ucs[uc].off_peak_measured_demand_in_kw - ucs[uc].contract_off_peak_demand_in_kw).clip(0)

        return ucs, flags, contract
    
    def get_ucs_details(self, ucs: dict) -> dict:
        flags = {}
        contract = {}

        for uc in ucs:
            peak_demand = not (ucs[uc][self.COLUMNS[6]] == 0).all()
            off_peak_demand = not (ucs[uc][self.COLUMNS[7]] == 0).all()

            if peak_demand and not off_peak_demand:
                flag = GREEN
                ucs[uc][self.COLUMNS[7]] = ucs[uc][self.COLUMNS[6]]
            elif not peak_demand and off_peak_demand:
                flag = GREEN
                ucs[uc][self.COLUMNS[6]] = ucs[uc][self.COLUMNS[7]]
            elif off_peak_demand and peak_demand: 
                flag = BLUE
            else:
                flag = "Skip"

            off_peak_demand_contracted = ucs[uc][self.COLUMNS[7]].iloc[11]
            peak_demand_contracted = ucs[uc][self.COLUMNS[6]].iloc[11]
            
            flags.update({uc: flag})
            contract.update({uc: (peak_demand_contracted, off_peak_demand_contracted)})
        
        return flags, contract

    def check_ucs(self, ucs: dict) -> None:
        for uc, plan in ucs.items():
            if(len(plan) < 12):
                print(f'UC {uc} com menos de um ano, removing...')
                
            columns_to_check = ['peak_consumption_in_kwh',
                                'off_peak_consumption_in_kwh',
                                'peak_measured_demand_in_kw',
                                'off_peak_measured_demand_in_kw']
            
            for c in columns_to_check:
                if (plan[c] == 0).any():
                    print(f"uc {uc} problemática: contém valor 0 na coluna {c}")
