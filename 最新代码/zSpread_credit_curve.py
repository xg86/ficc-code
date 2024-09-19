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

pd.options.mode.chained_assignment = None
import warnings
warnings.filterwarnings("ignore")

nss_data_proc_path='C://git//ficc-code//nss-data-proc//'
corp_com_data_path= 'C://git//ficc-code//credit-curve//'

end = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
src_files = ['corp-com-yields.xlsx']

static_file = corp_com_data_path+'WIND_BOND.xlsx'
static_df = pd.read_excel(static_file, sheet_name='Sheet1')

#today = datetime.now()
today_str = '2024-09-13 00:00:00'
today = pd.to_datetime(today_str)

def cal_zspread(newdf: DataFrame, yield_str: str, date_str: str, maturity_date: datetime, coupon: float, freq: int):
    return get_zspread(newdf[yield_str]/100, newdf[date_str], maturity_date, coupon/100, freq, '02')

def get_zSpread(src_file: str):
    print("starting reading ")
    request_file = corp_com_data_path + src_file
    src_df = pd.read_excel(request_file)
    codes = src_df.Code.unique()

    filename= str(uuid.uuid4().hex) + "_zSpread_"+ src_file
    writer = pd.ExcelWriter(nss_data_proc_path + filename)
    print("codes length ", len(codes))
    result_df = pd.DataFrame()
    for code in codes:
        if (len(code) > 0):
            print("code is  ", code)
            newdf = src_df[(src_df.Code == code)]
            #newdf = src_df
            #newdf['TradeTime'] = pd.to_datetime(newdf['Date'])
            #newdf.set_index('TradeTime', inplace=True)
            code_df = static_df[(static_df.CODE == code)]
            if(len(code_df) < 1):
                continue
            maturityDates = code_df['MATURITYDATE']
            maturity_date = pd.to_datetime(maturityDates.iloc[0])
            coupon = code_df['COUPONRATE'].iloc[0]
            freq = code_df['INTERESTFREQUENCY'].iloc[0]
            newdf['MATURITYDATE'] = maturity_date
            newdf['coupon'] = coupon
            newdf['freq'] = freq
            #print(">>>>>>>>>>>> pnl maturity_date %s, coupon %s, freq %s" % (maturity_date, coupon, freq))
            newdf['zSpread'] = newdf.apply(cal_zspread, args=('Yield', 'Date', maturity_date, coupon, freq), axis=1)
            parametric_curve =get_gcb_pc_curve(pd.to_datetime(newdf['Date'].iloc[0]), '02')
            gcb_yield = parametric_curve.Ytm(pd.to_datetime(newdf['MATURITYDATE']))
            print(gcb_yield)
            newdf['trading_date_gcb_yield'] = gcb_yield[0] * 100
            #newdf.to_excel(writer, sheet_name=code)
            result_df = pd.concat([result_df, newdf], ignore_index=True)


    nss_credit_curve = McpParameterCurve(today, result_df['MATURITYDATE'], result_df['zSpread']/10000, ParametricCurveModel.NSS)
    nss_curve_spread = nss_credit_curve.Ytm(result_df['MATURITYDATE'])
    #print("nss_curve_spread", nss_curve_spread)
    result_df['nss_curve_spread'] = pd.Series(nss_curve_spread)*10000

    ns_credit_curve = McpParameterCurve(today, result_df['MATURITYDATE'], result_df['zSpread'] / 10000,
                                         ParametricCurveModel.NS)
    ns_curve_spread = ns_credit_curve.Ytm(result_df['MATURITYDATE'])
    result_df['ns_curve_spread'] = pd.Series(ns_curve_spread) * 10000

    result_df['nss_diff'] = result_df['nss_curve_spread'] - result_df['zSpread']
    result_df['ns_diff'] = result_df['ns_curve_spread'] - result_df['zSpread']
    parametric_curve = get_gcb_pc_curve(today, '02')
    curr_date_gcb_yield = parametric_curve.Ytm(pd.to_datetime(result_df['MATURITYDATE']))
    result_df['curr_date_gcb_yield'] = pd.Series(curr_date_gcb_yield) * 100
    result_df['diff_gcb_yield'] = result_df['curr_date_gcb_yield'] - result_df['trading_date_gcb_yield']
    result_df['yield_proposed'] = result_df['curr_date_gcb_yield'] + result_df['nss_curve_spread']/100

    result_df.to_excel(writer)
    writer.close()
    print("ALl done ", src_file)

for src_file in src_files:
    get_zSpread(src_file)
