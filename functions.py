import requests
import json
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from rich.console import Console
from rich.table import Table
from pprint import pprint

api_file = open('api_key.txt', 'r')
API_URL = "https://www.alphavantage.co/query"
api_key = str(api_file.readline())

def check_value(fair_value, current_price):
    #Checks if Stocks is UNDERVALUED or OVERVALUED
    if fair_value>current_price:
        recommendation = 'UNDERVALUED'
        change_ratio = (fair_value-current_price)/current_price

    elif fair_value == current_price:
        recommendation = 'FAIR VALUE'
        change_ratio = 0
    else:
        recommendation = 'OVERVALUED'
        change_ratio = (current_price - fair_value)/fair_value

    return recommendation, change_ratio

def get_price(ticker):
    ts = TimeSeries(key = api_key)
    #Get Current Trading Price (5 min interval)
    ts_data, mets_ts = ts.get_intraday(ticker)
    ts_keys = list(ts_data.keys())
    trading_price = float(ts_data[ts_keys[0]]['1. open'])
    return trading_price

def calculate_equity_growth(new, old, time):
    new = int(new)
    old = int(old)
    diff = new-old
    growth_rate = (((new/old)**(1/time))-1)
    return growth_rate

def get_data(console, ticker, ror):
    #This function returns the following details when given a stock ticker/symbol:
        #Earnings per Share, Equity Growth, P/E Ratio
    console.print('Fetching data...', style = "blue")

    fd = FundamentalData(key = api_key)
    data = {
         "function": "OVERVIEW",
         "symbol": ticker,
         "outputsize": "compact",
         "datatype": "json",
         "apikey": api_key,
         }

    #Get Balance Sheet data of past five years
    bs_data, meta = fd.get_balance_sheet_annual(ticker)


    latest_equity = bs_data['totalShareholderEquity'][0]
    oldest_equity = bs_data['totalShareholderEquity'][4]

    #Calculating equity growth over five years
    eq_gr = calculate_equity_growth(latest_equity, oldest_equity, 5)

    #Get TTM EPS & PE Ratio
    response = requests.get(API_URL, data)
    co_data = response.json()
    eps = co_data['EPS']
    per = co_data['PERatio']

    #Get Company Details
    company_name = co_data['Name']
    company_country = co_data['Country']
    company_industry = co_data['Industry']
    company_sector = co_data['Sector']
    company_exchange = co_data['Exchange']

    trading_price = get_price(ticker)

    calculated_data = calculate_fair_value(console, ticker, eps, eq_gr, per, ror, 5)

    company_data = {'company_name': company_name, 'company_country': company_country, 'company_industry': company_industry,
            'company_sector': company_sector, 'company_exchange': company_exchange,'eps':eps, 'eq_gr':eq_gr, 'per': per,
            'trading_price': trading_price, 'calculated_data': calculated_data}

    console.print('Data Fetched!', style = "green bold")


    return company_data

def calculate_fair_value(console, ticker, eps, eq_gr, per, ror, time):
    #Calculate Compound Annual Growth Rate
    # This function calculates a fair value for a stock when provided with the
    # EPS, Equity Growth Rate, PE Ratio, Rate of Return, and Time Period.
    console.print('Calculating Fair Value...', style = "blue")
    ##CAGR = (finalValue/beginValue)^(1/time) - 1
    eps = float(eps)
    eq_gr = float(eq_gr)
    per = float(per)
    time = int(time)
    ror = float(ror/100)
    #print('EPS: %f, Equity Growth: %f, PER: %f' % (eps, eq_gr, per))

    future_per = (eq_gr*100) * 2
    future_eps = (1+eq_gr)**time * eps
    future_value = future_eps * future_per
    #print('Future PER: %f, Future EPS: %f, Future Value: %f' % (future_per, future_eps, future_value))

    fair_value = future_value/(ror +1)**time
    #print('Fair Value: %f' % (fair_value))
    mos_twenty = fair_value*0.8
    mos_thirty = fair_value*0.7

    #Get recommendation and UNDERVALUED/OVERVALUED %
    recommendation, change_ratio = check_value(fair_value, get_price(ticker))

    calculated_data = {'fair_value': fair_value, 'mos_twenty': mos_twenty, 'mos_thirty': mos_thirty, 'recommendation': recommendation, 'change_ratio': change_ratio}
    console.print('Calculations complete!', style = "green bold")
    return calculated_data

def display_results(console, ticker, company_data, calculated_data):
    #Schema of the input Parameters
    #company_data = {company_name, company_country, company_industry, company_sector, company_exchange, eps, eq_gr, per, trading_price, recommendation}
    #calculated_data = {fair_value, mos_twenty, mos_thirty, recommendation, change_ratio}

    overview_table = Table(title="COMPANY OVERVIEW", style = "bold blue")
    print()
    overview_table.add_column("Overview Item", style = "green", justify = "left")
    overview_table.add_column("Details", style = "green", justify = "right")
    overview_table.add_row('Company Name', company_data['company_name'])
    overview_table.add_row('Country', company_data['company_country'])
    overview_table.add_row('Industry', company_data['company_industry'])
    overview_table.add_row('Listed Exchange', company_data['company_exchange'])

    console.print(overview_table)
    # print('Company Name: %s' % company_data['company_name'])
    # print('Country: %s' % company_data['company_country'])
    # print('Industry: %s' % company_data['company_industry'])
    # print('Listed Exchange: %s'% company_data['company_exchange'])

    analysis_table = Table(title="PRICE ANALYSIS", style = "bold blue")
    analysis_table.add_column("Item", style = "green", justify = "left")
    analysis_table.add_column("Details", style = "green", justify = "right")
    analysis_table.add_row("Fair Value", "$%.2f" % calculated_data['fair_value'])
    analysis_table.add_row("Current Price", "$%.2f" % get_price(ticker))
    analysis_table.add_row("Recommendation", calculated_data['recommendation'])

    console.print(analysis_table)
    # print('\nPRICE ANALYSIS')
    # print('Fair Value: $%.2f' % calculated_data['fair_value'])
    # print('Current Price: $%.2f' % get_price(ticker))
    # print('RECOMMENDATION: %s' % calculated_data['recommendation'])

#The below lines are left for debugging purposes.
# company_data = get_data(Console(), 'MSFT')
# print(company_data["company_name"])