#Stonks will output a fair value of a stock ticker in the US and compare it with the current price of that stock
from functions import *
from rich.console import Console

api_file = open('api_key.txt', 'r')
API_URL = "https://www.alphavantage.co/query"
api_key = str(api_file.readline())

console = Console()
console.print("Welcome to Stonks!", justify = 'center', style= "bold blue")
data_entered = False
while data_entered == False:
    try:
        #Get Ticker from User
        ticker = str(input("Please enter stock symbol:")).upper()
        ror = int(input("Please enter your desired rate of return (without % sign): "))
        print()

        data_entered = True

    except:
        console.print("Input Error! Please enter valid information.\n", style = "red")
    try:
        #Fetch Data using alphavantage
        company_data = get_data(console, ticker)

        #Calculate fair value of the stock ticker
        calculated_data = calculate_fair_value(console, ticker, company_data['eps'], company_data['eq_gr'], company_data['per'], ror, 5)

        #Program output
        display_results(console, ticker, company_data, calculated_data)
        #Test print statements
        #print(equity_growth(latest_equity, oldest_equity, 5))
        #print(fair_value)

    except:
        console.print('ERROR! Please try again later!', style = "red")

api_file.close()
