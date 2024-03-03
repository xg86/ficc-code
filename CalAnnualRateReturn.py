import uuid

import pandas as pd
import numpy as np
from pandas import DataFrame
from datetime import datetime
from mcp.enums import *
from mcp.tools import *
from dateutil.relativedelta import relativedelta

pd.options.mode.chained_assignment = None
import warnings

warnings.filterwarnings("ignore")

file_path = 'E://meridian//债券//信号统计//RV//'
src_files = ['trades-jc-zero.csv']


static_file = 'D://git//strategy-repos-master//butterfly//nss-data//WIND_BOND.xlsx'
static_df = pd.read_excel(static_file, sheet_name='Sheet1')
amt_unit = 10000
deal_amt = 1000
excel_ext = '.xlsx'

one_day_rel = relativedelta(days=1)

def get_years(delta: relativedelta):
    year = delta.years
    year_month = delta.months / 12
    year_days = delta.days / 365
    return year + year_month + year_days

def skip_weekend(ref_date: datetime):
    while ref_date.day_of_week > 4:
        ref_date = ref_date+one_day_rel
    return ref_date

def get_bond_accrued_interest(
        ref_date: datetime,
        bond_mat_date: datetime,
        bond_coupon: float,
        freq: int = Frequency.Annual):
    return McpFixedRateBond({
        'ValuationDate': ref_date.strftime('%Y/%m/%d'),
        'MaturityDate': bond_mat_date.strftime('%Y/%m/%d'),
        'Coupon': bond_coupon,
        'Frequency': freq,
        'DayCounter': DayCounter.ActActXTR,
        # 'Calendar': McpCalendar(),
        # 'FaceValue': 100,
        # 'IssueDate': '2020-05-12',
        # 'prevCpnDate': '2022-05-13',
        # 'lastCpnDate': '2023-11-13',
        # 'firstCouponDate': '2020-11-13',
        # 'dateAdjuster': 5,
        # 'endToEnd': True,
        # 'longStub': False,
        # 'endStub': False,
        # 'applyDayCount': False
    })
    #return frb.AccruedInterestCHN(), frb.AccruedDaysCHN()


def get_bond_interest_amt(
        from_date: datetime,
        to_date: datetime,
        mat_date: datetime,
        bond_coupon: float,
        amt: float,
        freq: int = Frequency.Annual):
    from_date = skip_weekend(from_date)
    to_date = skip_weekend(to_date)

    frb1 = get_bond_accrued_interest(from_date, mat_date, bond_coupon, freq)
    interest_1 = frb1.AccruedInterestCHN()
    #print("accruedInterest:%f" % ( interest_1))

    frb2= get_bond_accrued_interest(to_date, mat_date, bond_coupon, freq)
    interest_2 = frb2.AccruedInterestCHN()
    #print("accruedInterest:%f" % (interest_2))

    #pay_dates1 = frb1.PaymentDates()
    #print(pay_dates1)

    pay_dates2 = frb2.PaymentDates()
    #print(pay_dates2)

    interest_amt = 0
    interest_change = 0

    interest_change = (interest_2 - interest_1) * amt / 100
    delta = relativedelta(to_date, from_date)
    if delta.years >= 1:# and (delta.months > 0 or delta.months > 0 ):
        interest_amt = amt * bond_coupon * delta.years  # annual, semi,
    if delta.months >=6 and freq == 2 and  pd.to_datetime(pay_dates2[0]) < to_date:
        interest_amt =  interest_amt + amt * bond_coupon
    if delta.months >= 6 and freq == 2 and  pd.to_datetime(pay_dates2[0]) >= to_date:
        interest_amt = interest_amt + amt * bond_coupon/freq
    if delta.months >=3 and freq == 4 and  pd.to_datetime(pay_dates2[0]) < to_date:
        interest_amt =  interest_amt + amt * bond_coupon
    if delta.months >= 3 and freq == 4 and  pd.to_datetime(pay_dates2[0]) >= to_date:
        interest_amt = interest_amt + amt * bond_coupon/freq
    if interest_change < 0 and interest_amt == 0:
        interest_amt = amt * bond_coupon/freq

    print("interest_amt:%f, interest_change:%f" % (interest_amt, interest_change))
    return interest_amt + interest_change


def cal_pnl(df1: DataFrame, sell_col1: str, buy_col2: str, amt_col3: str):
    if df1['方向'] == '卖出' and pd.to_datetime(df1['from_time']) < pd.to_datetime(df1['创建时间']):
        return (df1[sell_col1] - df1[buy_col2])*df1[amt_col3]*amt_unit/100
    else:
        return 0

def cal_holding_days(df1: DataFrame, sell_col1: str, buy_col2: str,):
    if df1['方向'] == '卖出' and pd.to_datetime(df1['from_time']) < pd.to_datetime(df1['创建时间']):
        days_diff = pd.to_datetime(df1[sell_col1]) - pd.to_datetime(df1[buy_col2])
        return days_diff.days
    else:
        return 0

def cal_interest_paid(df1: DataFrame, buy_col1: str, sell_col2: str, mat_date: datetime, coupon: float, amt_col3: int, freq: int):
    if df1['方向'] == '卖出' and pd.to_datetime(df1['from_time']) < pd.to_datetime(df1['创建时间']):
        return get_bond_interest_amt( pd.to_datetime(df1[buy_col1]),  pd.to_datetime(df1[sell_col2]), mat_date, coupon, df1[amt_col3]*amt_unit,freq)
    else:
        return 0

def get_annual_return(src_file: str):
    print("starting reading ", src_file)
    src_df = pd.read_csv(file_path + src_file, encoding='utf-8')
    # src_df = src_df.drop('Yld', axis=1)
    src_df['Code'] = src_df['债券代码']
    codes = src_df.Code.unique()

    filename = str(uuid.uuid4().hex) + "_backtest_" + src_file + excel_ext
    writer = pd.ExcelWriter( file_path + filename)
    print("codes length ", len(codes))
    for code in codes:
        if (len(code) > 0):
            newdf = src_df[(src_df.Code == code)]
            #newdf['TradeTime'] = pd.to_datetime(newdf['创建时间'])
            #newdf.set_index('Date', inplace=True)
            # print('bond code  = ', code)
            code_df = static_df[(static_df.CODE == code)]
            if (len(code_df) < 1):
                continue
            maturityDates = code_df['MATURITYDATE']
            maturity_date = pd.to_datetime(maturityDates.iloc[0])
            coupon = code_df['COUPONRATE'].iloc[0]
            freq = code_df['INTERESTFREQUENCY'].iloc[0]

            newdf['from_time'] = newdf['创建时间'].shift(1, fill_value=0)
            newdf['buy_price'] = newdf['净价'].shift(1, fill_value=0)

            newdf['pnl'] = newdf.apply(cal_pnl, args=('净价','buy_price','订单量'), axis=1)
            newdf['holding_days'] = newdf.apply(cal_holding_days, args=('创建时间', 'from_time'), axis=1)
            newdf['interest_paid'] = newdf.apply(cal_interest_paid, args=('from_time', '创建时间', maturity_date, coupon/100, '订单量', freq),axis=1)
            newdf.to_excel(writer, sheet_name=code)
            pnl_total = newdf['pnl'].sum()
            interest_total = newdf['interest_paid'].sum()
            holding_days_total = newdf['holding_days'].sum()
            anunal_ret_rate = ((pnl_total+interest_total)/(deal_amt*amt_unit)) / (holding_days_total/365) * 100
            print(
                "%%%%%%%%%%%% code {0} total-PnL {1}, interest_total {2}, holding_days_total {3}, anunal_ret_rate {4} "
                    .format(code, pnl_total, interest_total, holding_days_total, anunal_ret_rate))
    writer.close()
    print("ALl done ", src_file)

#from_date = pd.to_datetime('2023-05-11 00:00:00')  # 2023/03/02
#to_date = pd.to_datetime('2023-05-29 00:00:00')  # 2023/03/02
#190006.IB
#mat_date = pd.to_datetime('2029-05-23 00:00:00')  # 2032/7/18
#bond_coupon = 0.0329
#220025.IB
#mat_date = pd.to_datetime('2032-11-15 00:00:00')  # 2032/7/18
#bond_coupon = 0.028
#print(get_bond_accrued_interest(from_date, mat_date, bond_coupon, Frequency.Semiannual))
#print(get_bond_accrued_interest(to_date, mat_date, bond_coupon, Frequency.Semiannual))
#print(get_bond_interest_amt(from_date, to_date, mat_date, bond_coupon, 1000*10000,Frequency.Semiannual))

for src_file in src_files:
    get_annual_return(src_file)
