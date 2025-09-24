from time import sleep

import teslapy
from datetime import datetime
import tibber
import requests

TIBBER_API_ENDPOINT = "https://api.tibber.com/v1-beta/gql"

email_address = "mail@example.org"


tibber_access_token =  "asdfghjkl1234567890"
tibber_home_id =  "12345678-1234-4321-2345-123456789012"

tibber_account = tibber.Account(tibber_access_token)
tibber_home = tibber_account.homes[0]


now = datetime.now()
sorted_prices_today = {}
prices_today_and_tomorrow = []
prices_today = []
prices_tomorrow = []
sorted_prices_tomorrow = []
hourlyCurrentPricesLast7Days = [] 

highest_current_price = 0
highest_current_price_hour = 0
lowest_current_price = 0
lowest_current_price_hour = 0
lowestCurrentPriceOfTheWeek = 0
lastCurrentPrice = 0

def sort_prices_by_hour(prices):
    global sorted_prices_today
    # Pair each price with its hour
    hour_price_pairs = list(enumerate(prices))
    # Sort the pairs by price
    sorted_pairs = sorted(hour_price_pairs, key=lambda x: x[1])
    sorted_prices_today = sorted_pairs
    return sorted_pairs


def fetchCurrentPrices():
    global sorted_prices_tomorrow
    global hourlyCurrentPricesLast7Days
    global highest_current_price
    global highest_current_price_hour
    global lowest_current_price
    global lowest_current_price_hour

    prices_today_and_tomorrow = get_prices_for_today_and_tomorrow()
    prices_today = prices_today_and_tomorrow[0:96]

    if len(prices_today_and_tomorrow) > 96:
        prices_tomorrow = prices_today_and_tomorrow[96:192]
        sorted_prices_tomorrow = sort_prices(prices_tomorrow)  # Assuming sort_prices() is defined somewhere

    # Fetch historic price data
    hourlyCurrentPricesLast7Days = fetch_last_7_days_prices()

    # More data extraction logic
    pricesTodayList = prices_today
    if pricesTodayList:
        highest_current_price = max(pricesTodayList)
        highest_current_price_hour = pricesTodayList.index(highest_current_price)
        lowest_current_price = min(pricesTodayList)
        lowest_current_price_hour = pricesTodayList.index(lowest_current_price)


def get_prices_for_today_and_tomorrow():
    # Current time
    current_time = datetime.now()
    
    # Define the GraphQL query
    query = f"""
    {{
      viewer {{
        home(id: "{tibber_home_id}") {{
          currentSubscription {{
            priceInfo (resolution: QUARTER_HOURLY) {{
              current {{
                total
                startsAt
              }}
              today {{
                total
                startsAt
              }}
              tomorrow {{
                total
                startsAt
              }}
            }}
          }}
        }}
      }}
    }}
    """

    headers = {
        "Authorization": "Bearer " + tibber_access_token,
        "Content-Type": "application/json"
    }

    response = requests.post(TIBBER_API_ENDPOINT, json={"query": query}, headers=headers, verify=False)
    data = response.json()

    # Extract the price data for today
    prices_today = [entry["total"] for entry in data["data"]["viewer"]["home"]["currentSubscription"]["priceInfo"]["today"]]

    sort_prices_by_hour(prices_today)
    
    # If it's after 13:05, extract the price data for tomorrow
    if current_time.hour > 13 or (current_time.hour == 13 and current_time.minute >= 5):
        prices_tomorrow = [entry["total"] for entry in data["data"]["viewer"]["home"]["currentSubscription"]["priceInfo"]["tomorrow"]]
        prices_today.extend(prices_tomorrow)

    return prices_today


def fetch_last_7_days_prices():  
    
    hour_data = tibber_home.fetch_consumption("HOURLY", last=168)

    

    for hour in hour_data:
        hourlyCurrentPricesLast7Days.append(hour.unit_price)

    return hourlyCurrentPricesLast7Days



def highest_of_lowest_x_percent(x, arr):
    arr.sort()  # Sort the array
    n = len(arr)  # Length of the array
    count = int((x / 100) * n)  # Number of lowest values to consider
    return arr[count - 1] if count > 0 else None  # Return the highest value among the lowest x% values

def lowestCurrentPriceOfTheWeek(lowestPercentage):

    lowestCurrentPriceOfTheWeek = highest_of_lowest_x_percent(lowestPercentage,hourlyCurrentPricesLast7Days)

    return lowestCurrentPriceOfTheWeek

def currentIsCheap(numHours):

    if numHours <= 0:
        return False

    if lastCurrentPrice < 0:
        return True

    now = datetime.now()

    # Check for Friday and Saturday
    if now.weekday() in [4, 5]:
        return False

    currentHour = now.hour

    # Check if the current hour is within the cheapest numHours of the day
    cheapest_hours = [hour for hour, _ in sorted_prices_today[:numHours]]
    return currentHour in cheapest_hours


def sort_prices(pricesTodayList):

    
    # Create a list of tuples (hour, price) using enumerate
    price_tuples = list(enumerate(pricesTodayList))
    
    # Sort the list of tuples based on the price (second element of the tuple)
    sorted_prices = sorted(price_tuples, key=lambda x: x[1])
    
    return sorted_prices


def create_tariff(sorted_prices_list, num_off_peak, num_partial_peak, num_peak, num_super_peak):
    if num_off_peak + num_partial_peak + num_peak + num_super_peak != 96:
        raise ValueError("The sum of the number of values for each price category must be 96.")

    # Initialize the tou_periods and energy_charges dictionaries
    tou_periods = {"SUPER_OFF_PEAK": [], "OFF_PEAK": [], "PARTIAL_PEAK": [], "ON_PEAK": []}
    energy_charges = {"SUPER_OFF_PEAK": None, "OFF_PEAK": None, "PARTIAL_PEAK": None, "ON_PEAK": None}

    # Define the price category thresholds
    thresholds = [num_off_peak, num_off_peak + num_partial_peak, num_off_peak + num_partial_peak + num_peak]

    # Iterate over the sorted_prices_list
    for i, (hour, price) in enumerate(sorted_prices_list):
        # Determine the price category based on the price rank
        if i < thresholds[0]:
            price_category = "SUPER_OFF_PEAK"
        elif i < thresholds[1]:
            price_category = "OFF_PEAK"
        elif i < thresholds[2]:
            price_category = "PARTIAL_PEAK"
        else:
            price_category = "ON_PEAK"
        # Lets calculate the hour and the minute
        minute=hour%4
        hour=hour//4
                    
        if minute == 1:
            minute=15
        elif minute == 2:
            minute=30
        elif minute == 3:
            minute=45
        else:
            if minute != 0:
                print("Minutes are wrong")
                print(minute)

        # Add the hour to the tou_periods
        tou_periods[price_category].append({
            "fromDayOfWeek": 0,
            "fromHour": hour,
            "fromMinute": minute,
            "toDayOfWeek": 6,
            "toHour": hour,
            "toMinute": minute+15,
        })

        # Update the energy_charges if necessary
        if energy_charges[price_category] is None or price < energy_charges[price_category]:
            energy_charges[price_category] = price
    # Get current date and time
    current_datetime = datetime.now()

    # Extract day and month
    day = current_datetime.day
    month = current_datetime.month

    # Format as "DD.MM"
    formatted_date = f"{day:02d}.{month:02d}"

    # Create the tariff_data dictionary
    tariff_data = {
        "daily_charges": [{"name": "Charge", "amount": 0}],
        "demand_charges": {"ALL": {"ALL": 0}, "Summer": {}, "Winter": {}},
        "name": str(formatted_date),
        "utility": "My Energy Provider",
        "seasons": {
            "Summer": {
                "fromMonth": 1,
                "fromDay": 1,
                "toDay": 31,
                "toMonth": 12,
                "tou_periods": tou_periods,
            },
            "Winter": {"tou_periods": {}},
        },
        "energy_charges": {"ALL": {"ALL": 0}, "Summer": energy_charges, "Winter": {}},
        "sell_tariff": {
            "daily_charges": [{"name": "Charge", "amount": 0}],
            "demand_charges": {"ALL": {"ALL": 0}, "Summer": {}, "Winter": {}},
            "name": "My Plan",
            "utility": "My Energy Provider",
            "seasons": {
                "Summer": {
                    "fromMonth": 1,
                    "fromDay": 1,
                    "toDay": 31,
                    "toMonth": 12,
                    "tou_periods": tou_periods,
                },
                "Winter": {"tou_periods": {}},
            },
            "energy_charges": {"ALL": {"ALL": 0.07}, "Summer": {"SUPER_OFF_PEAK": 0.07, "OFF_PEAK": 0.07, "PARTIAL_PEAK": 0.07, "ON_PEAK": 0.07}, "Winter": {}},
        },
    }

    return tariff_data

def setTimeTableForPowerwall():

    try:

        tesla = teslapy.Tesla(email_address)

        battery_list = tesla.battery_list()
        battery = battery_list[0]
        
        priceLevel1 = 0
        priceLevel2 = 0
        priceLevel3 = 0
        priceLevel4 = 0

        # price threshold in percent
        threshold1 = 15
        threshold2 = 15
        threshold3 = 30
        # sanity check
        threshold4 = 50

        minPrice = lowest_current_price
        maxPrice = highest_current_price

        diffPrice = round(maxPrice - minPrice,2)

        # sorted from lowest to highest price -> [price, hour]
        sorted_prices_map = sorted_prices_today


        
        for i in range(0,96):

            if(sorted_prices_map[i][1]) <= minPrice + (diffPrice*(threshold1/100)):
                priceLevel1+=1
            elif(sorted_prices_map[i][1]) <= minPrice + (diffPrice*((threshold1 + threshold2)/100)):
                priceLevel2+=1
            elif(sorted_prices_map[i][1]) <= minPrice + (diffPrice*(((threshold1 + threshold2 + threshold3))/100)):
                priceLevel3+=1
            else:
                priceLevel4+=1

            
        # battery.api("OPERATION_MODE", default_real_mode="autonomous")

        # battery.set_backup_reserve_percent(10)

        # first number is lowest price, last number is highest
        tariff_data = create_tariff(sorted_prices_map,priceLevel1,priceLevel2,priceLevel3,priceLevel4)
        battery.set_tariff(tariff_data)

    
    except Exception as e:
        print(e)

startup = True

while True:
    now = datetime.now()    
    if now.hour == 0 and now.minute == 1 or startup == True:
        
        startup = False

        # Extract day and month
        day = now.day
        month = now.month
        hour = now.hour
        minute = now.minute

        # Format as "DD.MM"
        formatted_date = f"{day:02d}.{month:02d}. {hour:02d}:{minute:02d}"
        
        fetchCurrentPrices()

        setTimeTableForPowerwall()

        print(formatted_date + " - Powerwall Tariff Updated!")

    sleep(60)
