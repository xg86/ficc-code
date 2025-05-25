import numpy as np
import pandas as pd
from pandas import DataFrame


class FXOptionDeltaExtrapolator:
    def __init__(self, rr_values, bf_values):
        """
        Initialize the extrapolator with FX option Delta RR and BF values

        :param deltas: List of delta values [10, 25, 50]
        :param rr_values: Corresponding Risk Reversal (RR) values
        :param bf_values: Corresponding Butterfly (BF) values
        """
        # Convert to numpy arrays for robust handling
        #self.deltas = np.array(deltas)
        self.rr_values = np.array(rr_values)
        self.bf_values = np.array(bf_values)

    def extraploate_delta_rr_bf (self, atm: float, rr_25:float, rr_10:float, target_delta:float, isRR:bool, d_25:float = 25.0, d_10:int = 10.0):
        print(f"***************************************")
        ATMto25gradient = -1*rr_25 / (atm * 100.0 - d_25)
        print(f"ATMto25gradient: {ATMto25gradient:.6f}")

        extrap10Delta = ATMto25gradient * d_10 - ATMto25gradient * atm * 100.0
        print(f"extrap10Delta: {extrap10Delta:.6f}")

        grad25to10 = -1 * (rr_10 - rr_25) / (d_25 - d_10)
        print(f"grad25to10: {grad25to10:.6f}")

        extrap_target_delta = grad25to10 * target_delta + rr_25 - grad25to10 * d_25
        print(f"{target_delta:.6f}, extrap_target_delta: {extrap_target_delta:.6f}")

        error25to10 = (rr_10 - extrap10Delta) / (d_25 - d_10)
        print(f"error25to10: {error25to10:.6f}")

        if isRR:
            extrap_target_delta_Adj = extrap_target_delta + error25to10 * (d_10 - target_delta)
            print(f"extrap_target_delta_Adj RR: {extrap_target_delta_Adj:.6f}")
            return extrap_target_delta_Adj

        extrap_target_delta_Adj = extrap_target_delta + error25to10 * (d_10 - target_delta)
        if(extrap_target_delta_Adj < 0):
            return 0.0
        else:
            print(f"extrap_target_delta_Adj BF: {extrap_target_delta_Adj:.6f}")
            return  extrap_target_delta_Adj

def build_market_matrix(atm: float,rr_values:np.array, bf_values:np.array, tenor:str, delta_df: DataFrame, index:int):

    extrapolator = FXOptionDeltaExtrapolator(rr_values, bf_values)

    target_deltas = np.array([1, 5])

    # Weighted Interpolation for 5 Delta RR and BF
    for target_delta in target_deltas:
        rr_target = extrapolator.extraploate_delta_rr_bf(atm, rr_values[1], rr_values[0], target_delta, True)
        bf_target = extrapolator.extraploate_delta_rr_bf(atm, bf_values[1], bf_values[0], target_delta, False)

        print(f"{tenor} {target_delta} Delta RR:  {rr_target:.6f}")
        print(f"{tenor} {target_delta} Delta BF:  {bf_target:.6f}")
        delta_df.at[index, str(target_delta)+'P'] = (atm + bf_target - rr_target/2)/100
        delta_df.at[index, str(target_delta)+'C'] = (atm + bf_target + rr_target/2)/100
        delta_df.at[index, 'ATM'] = atm/100


if __name__ == "__main__":
    ''' POC Nanjing bank
    market_rr =[
             {
               "Tenors": "ON",
               "10RR": -0.05,
               "25RR": -0.05,
               "ATM": 4
             },
             {
               "Tenors": "1W",
               "10RR": -0.05,
               "25RR": -0.05,
               "ATM": 8.3
             },
             {
               "Tenors": "2W",
               "10RR": 0.05,
               "25RR": 0.075,
               "ATM": 8.1
             },
             {
               "Tenors": "3W",
               "10RR": 0.1,
               "25RR": 0.075,
               "ATM": 7.8
             },
             {
               "Tenors": "1M",
               "10RR": 0.15,
               "25RR": 0.08,
               "ATM": 7.05
             },
             {
               "Tenors": "2M",
               "10RR": 0.2,
               "25RR": 0.1,
               "ATM": 5.925
             },
             {
               "Tenors": "3M",
               "10RR": 0.4,
               "25RR": 0.2,
               "ATM": 5.8
             },
             {
               "Tenors": "6M",
               "10RR": 0.6,
               "25RR": 0.35,
               "ATM": 5.375
             },
             {
               "Tenors": "9M",
               "10RR": 0.8,
               "25RR": 0.4,
               "ATM": 5.2
             },
             {
               "Tenors": "1Y",
               "10RR": 1.1,
               "25RR": 0.55,
               "ATM": 5.125
             },
             {
               "Tenors": "18M",
               "10RR": 1.2,
               "25RR": 0.525,
               "ATM": 5.2
             },
             {
               "Tenors": "2Y",
               "10RR": 1.2,
               "25RR": 0.55,
               "ATM": 5.3
             },
             {
               "Tenors": "3Y",
               "10RR": 1.2,
               "25RR": 0.6,
               "ATM": 5.35
             }
        ]

    market_bf = [
                 {
                   "Tenors": "ON",
                   "ATM": 4,
                   "25BF": 0.23,
                   "10BF": 0.35
                 },
                 {
                   "Tenors": "1W",
                   "ATM": 8.3,
                   "25BF": 0.23,
                   "10BF": 0.35
                 },
                 {
                   "Tenors": "2W",
                   "ATM": 8.1,
                   "25BF": 0.23,
                   "10BF": 0.375
                 },
                 {
                   "Tenors": "3W",
                   "ATM": 7.8,
                   "25BF": 0.23,
                   "10BF": 0.4
                 },
                 {
                   "Tenors": "1M",
                   "ATM": 7.05,
                   "25BF": 0.24,
                   "10BF": 0.41
                 },
                 {
                   "Tenors": "2M",
                   "ATM": 5.925,
                   "25BF": 0.27,
                   "10BF": 0.475
                 },
                 {
                   "Tenors": "3M",
                   "ATM": 5.8,
                   "25BF": 0.275,
                   "10BF": 0.55
                 },
                 {
                   "Tenors": "6M",
                   "ATM": 5.375,
                   "25BF": 0.28,
                   "10BF": 0.58
                 },
                 {
                   "Tenors": "9M",
                   "ATM": 5.2,
                   "25BF": 0.2775,
                   "10BF": 0.68
                 },
                 {
                   "Tenors": "1Y",
                   "ATM": 5.125,
                   "25BF": 0.285,
                   "10BF": 0.75
                 },
                 {
                   "Tenors": "18M",
                   "ATM": 5.2,
                   "25BF": 0.29,
                   "10BF": 0.77
                 },
                 {
                   "Tenors": "2Y",
                   "ATM": 5.3,
                   "25BF": 0.3,
                   "10BF": 0.785
                 },
                 {
                   "Tenors": "3Y",
                   "ATM": 5.35,
                   "25BF": 0.3,
                   "10BF": 0.8
                 }
                ]
'''
market_rr = [
 {
   "Tenors": "ON",
   "10RR": 0.204,
   "25RR": 0.35,
   "ATM": 3.7
 },
 {
   "Tenors": "SW",
   "10RR": 0.286,
   "25RR": 0.275,
   "ATM": 5.095
 },
 {
   "Tenors": "2W",
   "10RR": 0.407,
   "25RR": 0.295,
   "ATM": 5.2
 },
 {
   "Tenors": "3W",
   "10RR": 0.938,
   "25RR": 0.409,
   "ATM": 5
 },
 {
   "Tenors": "1M",
   "10RR": 0.344,
   "25RR": 0.237,
   "ATM": 4.95
 },
 {
   "Tenors": "2M",
   "10RR": 0.404,
   "25RR": 0.242,
   "ATM": 4.725
 },
 {
   "Tenors": "3M",
   "10RR": 0.388,
   "25RR": 0.26,
   "ATM": 4.625
 },
 {
   "Tenors": "6M",
   "10RR": 0.571,
   "25RR": 0.292,
   "ATM": 4.537
 },
 {
   "Tenors": "9M",
   "10RR": 0.614,
   "25RR": 0.333,
   "ATM": 4.563
 },
 {
   "Tenors": "1Y",
   "10RR": 0.689,
   "25RR": 0.357,
   "ATM": 4.537
 },
 {
   "Tenors": "18M",
   "10RR": 0.865,
   "25RR": 0.375,
   "ATM": 4.488
 },
 {
   "Tenors": "2Y",
   "10RR": 1.037,
   "25RR": 0.389,
   "ATM": 4.463
 },
 {
   "Tenors": "3Y",
   "10RR": 0.953,
   "25RR": 0.316,
   "ATM": 4.438
 }
]

market_bf =[
 {
   "Tenors": "ON",
   "ATM": 3.7,
   "25BF": -0.301,
   "10BF": -0.278
 },
 {
   "Tenors": "SW",
   "ATM": 5.095,
   "25BF": 0.0775,
   "10BF": 0.437
 },
 {
   "Tenors": "2W",
   "ATM": 5.2,
   "25BF": 0.1425,
   "10BF": 0.5125
 },
 {
   "Tenors": "3W",
   "ATM": 5,
   "25BF": 0.0905,
   "10BF": 0.404
 },
 {
   "Tenors": "1M",
   "ATM": 4.95,
   "25BF": 0.1225,
   "10BF": 0.412
 },
 {
   "Tenors": "2M",
   "ATM": 4.725,
   "25BF": 0.152,
   "10BF": 0.457
 },
 {
   "Tenors": "3M",
   "ATM": 4.625,
   "25BF": 0.149,
   "10BF": 0.477
 },
 {
   "Tenors": "6M",
   "ATM": 4.537,
   "25BF": 0.224,
   "10BF": 0.5205
 },
 {
   "Tenors": "9M",
   "ATM": 4.563,
   "25BF": 0.1515,
   "10BF": 0.488
 },
 {
   "Tenors": "1Y",
   "ATM": 4.537,
   "25BF": 0.1315,
   "10BF": 0.5485
 },
 {
   "Tenors": "18M",
   "ATM": 4.488,
   "25BF": 0.1385,
   "10BF": 0.6075
 },
 {
   "Tenors": "2Y",
   "ATM": 4.463,
   "25BF": 0.1655,
   "10BF": 0.6915
 },
 {
   "Tenors": "3Y",
   "ATM": 4.438,
   "25BF": 0.201,
   "10BF": 0.9595
 }
]
columns = ["Tenors", "1P", "5P", "10P", "15P", "20P", "25P", "30P", "35P", "40P", "45P","ATM",
                     "45C","40C", "35C", "30C", "25C", "20C", "15C", "10C", "5C", "1C"] # Create an empty DataFrame with the specified columns empty_df = pd.DataFrame(columns=columns)

matrix_df = pd.DataFrame(columns=columns)

matrix_df['Tenors'] = [ "ON",
"SW",
"2W",
"3W",
"1M",
"2M",
"3M",
"6M",
"9M",
"1Y",
"18M",
"2Y",
"3Y"]

for rr, bf, index in zip(market_rr, market_bf, enumerate(matrix_df['Tenors'])):
    rr_vals= []
    rr_vals.append(rr['10RR'])
    rr_vals.append(rr['25RR'])

    bf_vals = []
    bf_vals.append(bf['10BF'])
    bf_vals.append(bf['25BF'])

    build_market_matrix(rr['ATM'], rr_vals, bf_vals, rr['Tenors'], matrix_df, index[0])
    print("$$$$$$$$$$$$$$$$$$$$$$$$")

print(matrix_df.to_string())
matrix_df.to_csv('extra_gradient_generate_matrix.csv', index=False)