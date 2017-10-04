import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pandas import DataFrame
import sys
import time
import os

path = './data/'  # set the path to your files here. Don't forget tot add '/' in the end.

if not os.path.exists(path):
    os.mkdir('./data')


print('Date should be in format: MM-DD-YYYY')
start_date = input('Enter the start date: ')
end_date = input('Enter the end date: ')
dt_start = ''
dt_end = ''


def generate_error_file(error):
    ts = time.time()
    st = datetime.fromtimestamp(ts).strftime('%m-%d-%Y_%H:%M:%S')
    file_name = f'Error_Log_{st}'
    f = open(f'{file_name}.txt', 'w')
    f.write(error)
    f.close()


def generate_file_name(current_day):
    file_year = current_day.strftime('%Y')
    file_month = current_day.strftime('%m')
    file_day = current_day.strftime('%d')
    return f'Insider_{file_month}{file_day}{file_year}'


def each_day_data(url, current_day):
    """ This function scraps the data for each specific date """

    try:
        r = requests.get(url)
        html = r.content
    except requests.exceptions.RequestException as error:
        print('Request error')
        generate_error_file(str(error))
        sys.exit()

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('tbody', {'id': 'insidertab'}).find_all('tr')

    results = []
    for row in table:
        d = {}
        reported_time = row.find_all('td')[0].text[0:10]
        transaction_time = row.find('font').text[0:10]
        d['Reported Time'] = datetime.strptime(reported_time, '%Y-%m-%d').strftime('%m-%d-%Y')
        d['Transaction Date'] = datetime.strptime(transaction_time, '%Y-%m-%d').strftime('%m-%d-%Y')
        d['Order Type'] = row.find('font').text[12:]
        d['Company '] = row.find_all('td')[2].text.replace(',', '')
        d['Ticker'] = row.find_all('td')[3].text
        d['Insider'] = row.find_all('td')[4].text.replace(',', '')
        d['Shares Trader'] = row.find_all('td')[5].text.replace(',', '')
        d['Avg Price'] = row.find_all('td')[6].text.replace('$', '')
        d['Value'] = row.find_all('td')[7].text.replace('$', '').replace(',', '')
        results.append(d)

    df = DataFrame(results)
    file_name = generate_file_name(current_day)
    df.to_csv(f'{path}{file_name}.csv', index_label='RowNo')


try:
    dt_start = datetime.strptime(start_date, '%m-%d-%Y')
    dt_end = datetime.strptime(end_date, '%m-%d-%Y')
except ValueError as error:
    print('Incorrect date format')
    generate_error_file(str(error))
    sys.exit()

delta = dt_end - dt_start  # difference between start and end date

for i in range(delta.days + 1):
    current_day = dt_start + timedelta(days=i)
    year = current_day.strftime('%Y')
    month = current_day.strftime('%m')
    day = current_day.strftime('%d')
    url = f'http://relationalstocks.com/showinsiders.php?date={year}-{month}-{day}'
    each_day_data(url, current_day)
