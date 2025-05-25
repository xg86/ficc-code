import pandas as pd
import numpy as np
from mcp.curve.nss.nss_curve import McpParameterCurve
from datetime import datetime
from mcp.enums import *
from mcp.tools import *
from dateutil.relativedelta import relativedelta

#from butterfly.original.zSpread_cal import zSpreadFsolve
from zSpread_cal import zSpreadFsolve
'''
request_file= 'D://git//strategy-repos-master//butterfly//nss-data//curve-data.csv'
df = pd.read_csv(request_file, encoding='utf-8')
ref_dt = pd.to_datetime('2023-09-22 00:00:00')
df['Dates'] = pd.to_datetime(df['MaturityDates'])
nss_curve = McpParameterCurve(ref_dt, df['Dates'], df['Rates'])
dates =['2024-06-17 00:00:00','2024-06-16 00:00:00','2024-06-15 00:00:00']
#[pd.to_datetime('2024-06-17 00:00:00')])
print(nss_curve.Ytm(pd.to_datetime(dates)))
'''
#file_path= 'D://git//strategy-repos-master//butterfly//nss-data//'
file_path= 'C://git//ficc-code//nss-data//'
#src_files = ['diff_gk.xlsx', 'diff_gz.xlsx', 'diff_nf.xlsx', 'diff_jc.xlsx']
#curve_categories = ['02', '00', '04', '03']

src_files = ['diff_gz.xlsx']
curve_categories = ['00']
'''
src_files = ['diff_gk.xlsx']
curve_categories = ['02']

src_files = ['diff_nf.xlsx']
curve_categories = ['04']

src_files = ['diff_jc.xlsx']
curve_categories = ['03']
'''

one_day_rel = relativedelta(days=1)

src_df_dict = {}
curve_dict = {}
for i in range(len(src_files)):
    request_file = file_path + src_files[i]
    src_df = pd.read_excel(request_file)
    src_df.set_index('Date', inplace=True)
    src_df_dict[curve_categories[i]] = src_df

def get_ylds(ref_date: datetime, category: str, dates: []):
    key= category + ref_date.strftime('%Y-%m-%d')
    if key in curve_dict:
        nss_curve = curve_dict[key]
    else:
        data_df = src_df_dict[category]
        curver_df = data_df.loc[ref_date.strftime('%Y-%m-%d')]
        nss_curve = McpParameterCurve(ref_date, curver_df['MaturityDate'], curver_df['NssZero'], ParametricCurveModel.NSS)
        #nss_curve = McpParametricCurve({
        #    'ReferenceDate': ref_date,
        #    'MaturityDates': [dt.strftime('%Y/%m/%d') for dt in curver_df['MaturityDate']],
        #    'Rates': curver_df['NssZero'].tolist(),
        #    'ParamCurveModel': ParametricCurveModel.NSS,
       # })
        curve_dict[key] = nss_curve
    return nss_curve.Ytm(pd.to_datetime(dates))

def get_gcb_pc_curve(ref_date: datetime, category='00'):
    key= category + ref_date.strftime('%Y-%m-%d')
    if key in curve_dict:
        return curve_dict[key]
    else:
        data_df = src_df_dict[category]
        while True:
            if ref_date.strftime('%Y-%m-%d') in data_df.index :
                curver_df = data_df.loc[ref_date.strftime('%Y-%m-%d')]
                nss_curve = McpParameterCurve(ref_date, curver_df['MaturityDate'], curver_df['NssZero'])
                #parametric_curve = McpParametricCurve({
                #    'ReferenceDate': ref_date,
                #    'MaturityDates': [dt.strftime('%Y/%m/%d') for dt in curver_df['MaturityDate']],
                #    'Rates': curver_df['NssZero'].tolist(),
                #    'ParamCurveModel': ParametricCurveModel.NSS,
                #})
                curve_dict[key] = nss_curve
                return nss_curve #, nss_curve.Ytm(pd.to_datetime(dates))
            else:
                print("@@@@@@@@ missing ref_date %s" % (ref_date.strftime('%Y-%m-%d')))
                ref_date = ref_date-one_day_rel
                print("@@@@@@@@ try ref_date %s" % (ref_date.strftime('%Y-%m-%d')))

    return None

dates =['2024-06-17 00:00:00','2024-06-16 00:00:00','2024-06-15 00:00:00']
ref_dt = pd.to_datetime('2023-10-19 00:00:00')
category = '00'

#print(get_ylds(ref_dt,category, dates))
def get_years( delta: relativedelta):
    year = delta.years
    year_month = delta.months/12
    year_days = delta.days/365
    return year + year_month + year_days

def get_zspread(yld: float,
                ref_date: datetime,
                bond_mat_date: datetime,
                bond_coupon: float,
                freq: int = Frequency.Annual,
                category='00'):
    frb = McpFixedRateBond({
        'ValuationDate': ref_date.strftime('%Y/%m/%d'),
        'MaturityDate': bond_mat_date.strftime('%Y/%m/%d'),
        'Coupon': bond_coupon,
        'Frequency': freq,
        'DayCounter': DayCounter.ActActXTR,
        #'Calendar': McpCalendar(),
        #'FaceValue': 100,
        #'IssueDate': '2020-05-12', 
        #'prevCpnDate': '2022-05-13',
        #'lastCpnDate': '2023-11-13',
        #'firstCouponDate': '2020-11-13',
        #'dateAdjuster': 5,
        #'endToEnd': True, 
        #'longStub': False,
       # 'endStub': False,
        #'applyDayCount': False
        })
    dirty_price = frb.DirtyPriceFromYieldCHN(yld, True)
    #print(dirty_price)

    pay_dates = frb.PaymentDates()
    print(pay_dates)
    pay_years = [get_years(relativedelta(pay_date, ref_date)) for pay_date in pd.to_datetime(pay_dates)]
    #print(pay_years)

    cash_flows = frb.Payments()
    #print(cash_flows)
    #print(">>>>>>>>>>>> cur_date %s " % (cur_date))
    parametric_curve = get_gcb_pc_curve(ref_date, category)
    if parametric_curve != None:
        #print(rates)
        #frb_zSpread= frb.ZSpread(yld, parametric_curve.getCurve())*10000
        #print(">>>>>>>>>>>> frb_zSpread %s " % (frb_zSpread))
        rates = parametric_curve.Ytm(pd.to_datetime(pay_dates))
        #rate_discount_factor = parametric_curve.DiscountFactor(pd.to_datetime(pay_dates))
        zSpreadFsolver = zSpreadFsolve(dirty_price, cash_flows, pay_years, rates)
        #print(">>>>>>>>>>>> zSpreadF %s " % (zSpreadF))
        return zSpreadFsolver.zSpread_fsolve()*10000
    return 0

def get_discount_factor(
                ref_date: datetime,
                bond_mat_date: datetime,
                bond_coupon: float,
                freq: int = Frequency.Annual,
                category='00'):
    frb = McpFixedRateBond({
        'ValuationDate': ref_date.strftime('%Y/%m/%d'),
        'MaturityDate': bond_mat_date.strftime('%Y/%m/%d'),
        'Coupon': bond_coupon,
        'Frequency': freq,
        'DayCounter': DayCounter.ActActXTR,
        #'Calendar': McpCalendar(),
        #'FaceValue': 100,
        #'IssueDate': '2020-05-12',
        #'prevCpnDate': '2022-05-13',
        #'lastCpnDate': '2023-11-13',
        #'firstCouponDate': '2020-11-13',
        #'dateAdjuster': 5,
        #'endToEnd': True,
        #'longStub': False,
       # 'endStub': False,
        #'applyDayCount': False
        })
    #dirty_price = frb.DirtyPriceFromYieldCHN(yld, True)
    #print(dirty_price)

    pay_dates = frb.PaymentDates()
    print(pay_dates)
    #pay_years = [get_years(relativedelta(pay_date, ref_date)) for pay_date in pd.to_datetime(pay_dates)]
    #print(pay_years)

    #cash_flows = frb.Payments()
    #print(cash_flows)
    print(">>>>>>>>>>>> cur_date %s " % (cur_date))
    parametric_curve = get_gcb_pc_curve(ref_date, category)
    if parametric_curve != None:
        for mDate in pay_dates:
            print(mDate)
            rate_discount_factor = parametric_curve.wrapper.DiscountFactor(mDate)
            print(rate_discount_factor)
    return 0

cur_date = pd.to_datetime('2025-03-24 00:00:00') #2023/03/02
mat_date = pd.to_datetime('2027-09-13 00:00:00') #2032/7/18
mkt_yld = 0.01739
bond_coupon= 0.0167

print('get_zspread')
print(get_zspread(mkt_yld, cur_date, mat_date, bond_coupon, 1))
#print('get_discount_factor')
#print(get_discount_factor(cur_date, mat_date, bond_coupon, 1))

#today = pd.to_datetime('2025-03-24 00:00:00') #2032/7/18
'''
ref_dates =['2025-01-14',
             '2025-01-14',
             '2025-02-19',
             '2025-02-06',
             '2025-01-09',
             '''
ref_dates =[
'2025-03-06',
'2025-01-15',
'2025-01-06'
             ]

'''
mat_dates = ['2029-07-15',
             '2034-05-25',
             '2031-09-15',
             '2027-09-13',
             '2029-09-03',
 '''
mat_dates = [
'2035-01-03',
'2027-06-16',
'2027-01-05'
             ]
'''
today = pd.to_datetime('2025-03-24 00:00:00') #2032/7/18
parametric_curve = get_gcb_pc_curve(pd.to_datetime(today), '02')
mat_date2 = '2029-09-3 00:00:00'
#curr_date_nf_yield = parametric_curve.wrapper.ZeroRate(mat_date2)
curr_date_nf_yield = parametric_curve.Ytm(pd.to_datetime(mat_dates))
print(curr_date_nf_yield)

for mat_date, today in zip(mat_dates,ref_dates):
    parametric_curve = get_gcb_pc_curve(pd.to_datetime(today), '02')
    curr_date_gcb_yield = parametric_curve.wrapper.ZeroRate(mat_date)
#print(curr_date_gcb_yield)
    print(f"today {today}, mat_date {mat_date}, curr_date_gcb_yield is: {curr_date_gcb_yield * 1_00:.4f}")
'''