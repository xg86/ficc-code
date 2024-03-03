import uuid

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

import statsmodels.tsa.stattools as tsa
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
from pandas import DataFrame
from sklearn import preprocessing
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import seaborn as sn
from datetime import datetime
import datetime as dt
from timeit import default_timer as timer
from dateutil.relativedelta import relativedelta

from mcpParamCurve import *

import warnings
import pandas as pd
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=(SettingWithCopyWarning))


#start = '2022-01-4 00:00:00'
#cutoff = '2023-10-1 00:00:00'
src_file = 'local_gcb.xlsx'

spread_file = 'D://git//strategy-repos-master//butterfly//nss-data//WIND_BOND.xlsx'
ref_data_df = pd.read_excel(spread_file, sheet_name='Sheet1')

def get_half_life2(z_array: pd.Series):
    z_lag = np.roll(z_array, 1)
    z_lag[0] = 0
    z_ret = z_array - z_lag
    z_ret[0] = 0
    # adds intercept terms to X variable for regression
    z_lag2 = sm.add_constant(z_lag)
    model = sm.OLS(z_ret, z_lag2)
    res = model.fit()
    halflife = -np.log(2) / res.params[1]
    #print('Halflife = ', halflife)
    return halflife
def get_half_life(data: pd.Series):
    if (len(data) < 2):
        return -1
    data_lag = data.shift(1)
    Y = data[1:] - data_lag[1:]
    X = sm.add_constant(data_lag[1:])  # Adds a column of ones to an array
    model = sm.OLS(Y, X)
    res = model.fit()
    np_log = -np.log(2)
    if(len(res.params) < 2):
        return -1
    res_params = res.params.iloc[1]
    param_1 = np_log / res_params
    halflife = round(param_1, 0)
    return halflife

def stationary_test(data2: pd.Series):
    # compute ADF test statistic
    adf_ = tsa.adfuller(data2,maxlag=1)
    #print('adf', adf_[0])
    #print('p-value', adf_[1])
    #print('T values', adf_[4])
    return adf_[1] < 0.1

def getYield(df1: DataFrame, col1: str, col2: str):
    if df1[col2] >= 1:
        return df1[col1]
def getPnl(df2: DataFrame, col1: str, col2: str, multiplier: int, isYield: bool):
    #if df['Buy'] == 1 and df['SellYield'] != None and df['BuyYield'] > 0 and df['SellYield'] > 0 :
    if df2['Sell'] == 1 and df2[col1] != None and df2[col1] > 0 and df2[col2] > 0:
        if isYield:
            return (df2[col1] - df2[col2]) * multiplier
        return (df2[col2] - df2[col1])* multiplier
#one buy one sell
def calculatePnl(df3: DataFrame):
    df3['BuyYield'] = df3.apply(getYield, args=('Yield', 'Buy'), axis=1)
    df3['SellYield'] = df3.apply(getYield, args=('Yield', 'Sell'), axis=1)
    #df['BuyDirtyPrice'] = df.apply(getYield, args=('ValuationDirtyPrice', 'Buy'), axis=1)
    #df['SellDirtyPrice'] = df.apply(getYield, args=('ValuationDirtyPrice', 'Sell'), axis=1)
   #if len(df[df['Sell'] == 1]) > 1:
   #     df['SellYield'].fillna(method='bfill', inplace=True)
    b_yield = -1
    b_yield_zSpread= -1
    for index, row in df3.iterrows():
        #print(row["Name"], row["Age"])
        if row['Buy'] == 1 and b_yield < 0:
            b_yield = row['BuyYield']
            b_yield_zSpread = row['zSpread']
        elif row['Sell'] == 1 and b_yield > 0:
            df3.at[index, 'BuyYield'] = b_yield
            df3.at[index, 'b_yield_zSpread'] = b_yield_zSpread
            b_yield = -1
            b_yield_zSpread = -1

    df3['PnLYield'] = df3.apply(getPnl, args=('BuyYield', 'SellYield', 100, True), axis=1)
    #df['PnLPrice'] = df.apply(getPnl, args=('BuyDirtyPrice', 'SellDirtyPrice', 100*1000, False), axis=1)
    return df3['PnLYield'].sum() #, df['PnLPrice'].sum()


def check_spread(spread_trades: pd.Series, spread_sigal: pd.Series, code: str, pnlY: float, left_year, side: str, trades_time: pd.Series):

    #code_df = ref_data_df[(ref_data_df.Code == code)]
    b_a_spread = 0
    #if len(code_df) > 0 :
    #    b_a_spread = code_df['spread'].tolist()[0]
    min_val = spread_trades.min()
    for indx, val in spread_sigal.items():
        if val > min_val:
            #print("diff yield {0}, bid-ask spread {1} for code {2}".format (val, b_a_spread, code))
            print("%%%%%%%%%%%% {5}  for code {0} on {7}, total PnL {1}, diff zSpread {2}, bid-ask spread {3}, zs-b-a_sprd {6} left {4} "
                  .format(code, pnlY, val - min_val, b_a_spread, left_year, side, val - min_val - b_a_spread, trades_time.max()))
            return True
    return False
    pass


def get_left_year(maturity_date: datetime):
    now = datetime.now()
    return relativedelta(maturity_date, now)
    pass

def cal_zspread(newdf: DataFrame, yield_str: str, date_str: str, maturity_date: datetime, coupon: float, freq: int):
    return get_zspread(newdf[yield_str]/100, newdf[date_str], maturity_date, coupon/100, freq)

def get_rv_signal(src_df: DataFrame):
    print("starting reading ")
    codes = src_df.Code.unique()

    filename= str(uuid.uuid4().hex) + "local_gcb_zSpread_"+ src_file
    writer = pd.ExcelWriter("D://git//strategy-repos-master//butterfly//nss-data-proc//"+filename)
    print("codes length ", len(codes))
    for code in codes:
        if(len(code) > 0 ):
            newdf = src_df[(src_df.Code == code)]
            #newdf['TradeTime'] = pd.to_datetime(newdf['Date'])
            #newdf.set_index('Date', inplace=True)
            #print('bond code  = ', code)
            code_df = ref_data_df[(ref_data_df.CODE == code)]
            maturityDates=code_df['MATURITYDATE']
            maturity_date = pd.to_datetime(maturityDates.iloc[0]) 
            coupon = code_df['COUPONRATE'].iloc[0]
            freq = code_df['INTERESTFREQUENCY'].iloc[0]
            newdf['zSpread'] = newdf.apply(cal_zspread, args=('Yield', 'TradeTime', maturity_date, coupon, freq), axis=1)
            halflife_Yield = get_half_life(newdf["Yield"])
            #print('halflife_Zero = ', halflife_Zero)
            #halflife_NssZero = get_half_life(newdf["NssZero"])
            #print('halflife_NssZero = ', halflife_NssZero)
            if(halflife_Yield > 1 ):
                window_size = int(np.rint(halflife_Yield))
                #newdf['AbsDiffZero'] = np.abs(newdf["NssZero"]-newdf["Zero"])*10000
                newdf['ave_'+str(window_size)] = newdf['zSpread'].rolling(window=int(window_size), center=False).mean()
                newdf['std_'+str(window_size)] = newdf['zSpread'].rolling(window=int(window_size), center=False).std(ddof=0)
                newdf['zscore_'+str(window_size)] = (newdf['zSpread'] - newdf['ave_'+str(window_size)])/newdf['std_'+str(window_size)]

                newdf['Buy'] = np.where(newdf['zscore_'+str(window_size)] >= 1, 1, 0)
                newdf['Sell'] = np.where(newdf['zscore_'+str(window_size)] <= -1, 1, 0)

                pnlY = calculatePnl(newdf)
                print(">>>>>>>>>>>> pnl yield %s, for code %s" % (pnlY, code))
              
                tmp20 = newdf.tail(20)
                left_year = get_left_year(maturity_date)
                print("$$$$$$$$$ for code {0}, mat {4} min Zspread {1}, Max zSpread {2}, min-max spread {3}, left {5}"
                  .format(code,tmp20['zSpread'].min(), tmp20['zSpread'].max(), tmp20['zSpread'].max() - tmp20['zSpread'].min(), maturity_date, left_year))
                newdf.to_excel(writer, sheet_name=code)
                tmp = newdf.tail(2)
                p_val = stationary_test(newdf['zSpread'])
                if (len(tmp[tmp['Buy'] == 1]) > 0 or len(tmp[tmp['Sell'] == 1]) > 0) and pnlY > 0 and p_val:
                    tradedf = newdf[(newdf.PnLYield > 0)]
                    if (len(tradedf) <= 2):
                        continue
                    check_spread(tradedf['b_yield_zSpread'], tmp['zSpread'], code, pnlY, left_year, 'Buy' if len(tmp[tmp['Buy'] == 1]) > 0 else 'Sell', tmp['TradeTime'])

                   #if len(tmp[tmp['Sell'] == 1]) > 0 :
                    #    print("############ Sell trading sigal for code is  ", code)
                    #print("done for code is  ", code)

    writer.close()
    print("ALl done ", src_file)

def process_data():
    df = pd.read_csv('E://meridian//债券//信号统计//每日-地方债收盘历史.csv')
    df.drop(df[df.成交量 == 0.0].index, inplace=True)
    df = df[~(df.时间.str.contains('IB'))]
    df = df[~(df.时间.str.contains('SZ'))]
    df = df[~(df.时间.str.contains('SH'))]

    cutoff = '2022-1-4 00:00:00'
    # df = pd.read_csv ('E://meridian//债券//信号统计//out.csv')
    df['Date'] = pd.to_datetime(df['时间'])
    df['TradeTime'] = df['Date']
    df.set_index('Date', inplace=True)
    cutoff_df = df.loc[cutoff:]
    cutoff_df['bond_id'] = cutoff_df['代码']

    df1 = cutoff_df['bond_id'].value_counts()
    # get top 20
    top20_series = df1.nlargest(20)
    cutoff_df_new = cutoff_df[cutoff_df['bond_id'].isin(top20_series.index)]
    cutoff_df_new['Yield'] = cutoff_df_new['收益率']
    cutoff_df_new['Code'] = cutoff_df_new['bond_id']
    return cutoff_df_new


cutoff_df_new = process_data()
get_rv_signal(cutoff_df_new)
