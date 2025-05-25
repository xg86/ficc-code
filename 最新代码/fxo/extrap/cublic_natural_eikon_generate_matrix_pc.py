import numpy as np
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d, CubicSpline
from numpy.polynomial.polynomial import Polynomial

class FXOptionCubicDeltaExtrapolator:
    def __init__(self, deltas, vols):
        """
        Initialize the extrapolator with FX option Delta RR and BF values

        :param deltas: List of delta values [10, 25, 50]
        :param rr_values: Corresponding Risk Reversal (RR) values
        :param bf_values: Corresponding Butterfly (BF) values
        """
        # Convert to numpy arrays for robust handling
        self.deltas_values = np.array(deltas)
        self.vol_values = np.array(vols)
        #self.coeffs_left = Polynomial.fit(self.deltas_values[:4], self.vol_values[:4], deg=2).convert().coef
        #self.coeffs_right = Polynomial.fit(self.deltas_values[-4:], self.vol_values[-4:], deg=2).convert().coef
        #self.cubic_interp = interp1d(self.deltas_values, self.vol_values, kind='cubic', fill_value="extrapolate")
        self.cubic_interp = CubicSpline(self.deltas_values, self.vol_values, bc_type='natural', extrapolate=True)

    # Define the cubic extrapolators
    #def cubic_extrapolate_left(self, xval):
        #return self.coeffs_left[0] + self.coeffs_left[1] * xval + self.coeffs_left[2] * xval ** 2

    #def cubic_extrapolate_right(self, xval):
        #return self.coeffs_right[0] + self.coeffs_right[1] * xval + self.coeffs_right[2] * xval ** 2

    # Combined interpolator and extrapolator
    def cubic_interp_extrap(self, xval):
        return self.cubic_interp(xval)


        '''
        if xval < self.deltas_values[0]:
            return self.cubic_extrapolate_left(xval)
        elif xval > self.deltas_values[-1]:
            return self.cubic_extrapolate_right(xval)
        else:
            return self.cubic_interp(xval)
        elif xval > 25 and xval < 50:
            return cubic_extrapolate_right(xval)
        elif xval > 50 and xval < 75:
            return cubic_extrapolate_left(xval)
        '''

def build_market_matrix(atm: float,vols:np.array, tenor:str, delta_df: DataFrame, index:int):
    # Example usage with different delta values
    # Inputs: 10D RR, 25D RR, 50D RR

    deltas = np.array([10, 25, 50, 75, 90])

    extrapolator = FXOptionCubicDeltaExtrapolator(deltas, vols)

    # Linear Extrapolation for 5 Delta RR and BF
    '''
    rr_5d_linear, bf_5d_linear = extrapolator.linear_extrapolation(15)
    print("Linear Extrapolation:")
    print("5 Delta RR:", rr_5d_linear)
    print("5 Delta BF:", bf_5d_linear)
    '''
    target_deltas = np.array([15, 20, 30, 35, 40, 45, 55, 60, 65, 70, 80, 85])

    # Weighted Interpolation for 5 Delta RR and BF

    for target_delta in target_deltas:
        vol_val = extrapolator.cubic_interp_extrap(target_delta)

        print(f"{tenor} {target_delta} Delta RR:  {vol_val:.6f}")
        #print(f"{tenor} {target_delta} Delta BF:  {bf_val:.6f}")
        if target_delta < 50:
            delta_df.at[index, str(target_delta)+'P'] = vol_val
        else:
            delta_df.at[index, str(100-target_delta) + 'C'] = vol_val
        #delta_df.at[index, str(target_delta)+'C'] = (atm + bf_val + rr_val/2)/100
        delta_df.at[index, 'ATM'] = atm




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

market_vols =[
 {
   "Tenors": "ON",
   "10P": 3.32,
   "25P": 3.224,
   "ATM": 3.7,
   "25C": 3.574,
   "10C": 3.524
 },
 {
   "Tenors": "SW",
   "10P": 5.389,
   "25P": 5.035,
   "ATM": 5.095,
   "25C": 5.31,
   "10C": 5.675
 },
 {
   "Tenors": "2W",
   "10P": 5.509,
   "25P": 5.195,
   "ATM": 5.2,
   "25C": 5.49,
   "10C": 5.916
 },
 {
   "Tenors": "3W",
   "10P": 4.935,
   "25P": 4.886,
   "ATM": 5,
   "25C": 5.295,
   "10C": 5.873
 },
 {
   "Tenors": "1M",
   "10P": 5.19,
   "25P": 4.954,
   "ATM": 4.95,
   "25C": 5.191,
   "10C": 5.534
 },
 {
   "Tenors": "2M",
   "10P": 4.98,
   "25P": 4.756,
   "ATM": 4.725,
   "25C": 4.998,
   "10C": 5.384
 },
 {
   "Tenors": "3M",
   "10P": 4.908,
   "25P": 4.644,
   "ATM": 4.625,
   "25C": 4.904,
   "10C": 5.296
 },
 {
   "Tenors": "6M",
   "10P": 4.772,
   "25P": 4.615,
   "ATM": 4.537,
   "25C": 4.907,
   "10C": 5.343
 },
 {
   "Tenors": "9M",
   "10P": 4.744,
   "25P": 4.548,
   "ATM": 4.563,
   "25C": 4.881,
   "10C": 5.358
 },
 {
   "Tenors": "1Y",
   "10P": 4.741,
   "25P": 4.49,
   "ATM": 4.537,
   "25C": 4.847,
   "10C": 5.43
 },
 {
   "Tenors": "18M",
   "10P": 4.663,
   "25P": 4.439,
   "ATM": 4.488,
   "25C": 4.814,
   "10C": 5.528
 },
 {
   "Tenors": "2Y",
   "10P": 4.636,
   "25P": 4.434,
   "ATM": 4.463,
   "25C": 4.823,
   "10C": 5.673
 },
 {
   "Tenors": "3Y",
   "10P": 4.921,
   "25P": 4.481,
   "ATM": 4.438,
   "25C": 4.797,
   "10C": 5.874
 }
]

columns = ["Tenors", "1P", "5P", "10P", "15P", "20P", "25P", "30P", "35P", "40P", "45P","ATM",
                     "45C","40C", "35C", "30C", "25C", "20C", "15C", "10C", "5C", "1C"] # Create an empty DataFrame with the specified columns empty_df = pd.DataFrame(columns=columns)

matrix_df = pd.DataFrame(columns=columns)

matrix_df['Tenors'] = [
"ON",
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

for vol, index in zip(market_vols, enumerate(matrix_df['Tenors'])):
    vol_vals= []
    vol_vals.append(vol['10P'])
    vol_vals.append(vol['25P'])
    vol_vals.append(vol['ATM'])
    vol_vals.append(vol['25C'])
    vol_vals.append(vol['10C'])

    build_market_matrix(vol['ATM'], vol_vals, vol['Tenors'], matrix_df, index[0])
    print("$$$$$$$$$$$$$$$$$$$$$$$$")

print(matrix_df.to_string())
matrix_df.to_csv('cublic_natural_eikon_generate_matrix_pc.csv', index=False)