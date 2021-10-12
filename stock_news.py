import requests
from send_email import send_email
from datetime import datetime
from decouple import config

API_KEY_ALPHA = config('API_KEY_ALPHA')
API_KEY_NEWS = config('API_KEY_NEWS')
PURCHASE_PRICE = float(config('PURCHASE_PRICE'))
INITIAL_PURCHASE_DATE = config('INITIAL_PURCHASE_DATE')

STOCK = config('STOCK')
COMPANY_NAME = config('COMPANY_NAME')
COMPANY_SHORT = config('COMPANY_SHORT')

parameters_alpha = {
    'apikey': API_KEY_ALPHA,
    'symbol': STOCK,
    'function': 'TIME_SERIES_DAILY',
}

STOCK_ENDPOINT = "https://www.alphavantage.co/query"

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

response_stock = requests.get(url=STOCK_ENDPOINT, params=parameters_alpha)
response_stock.raise_for_status()

data = response_stock.json()['Time Series (Daily)']
date_list = [date for date, value in data.items()]
yesterday = date_list[1]
today = date_list[0]
news_articles = ''
week_ago = date_list[6]
month_ago = date_list[20]
total_history = date_list[99]
date = datetime.today().strftime('%Y/%m/%d')
complete_date_list = [yesterday, week_ago, month_ago, total_history]


def get_news():
    parameters_news = {
        'apiKey': API_KEY_NEWS,
        'q': COMPANY_SHORT,
        'from_param': yesterday,
        'to': today,
    }
    response_news = requests.get(url=NEWS_ENDPOINT, params=parameters_news)
    response_news.raise_for_status()
    data_news = response_news.json()
    global news_articles
    news_articles = data_news['articles']


def retrieve_close(full_list):
    percent_change_total = []
    for date in full_list:
        action_last_day = data[today]
        finish_last_day = float(action_last_day['4. close'])
        action = data[date]
        finish = float(action['4. close'])
        difference = round((finish_last_day - finish), 3)
        percent_change = (round(((difference / finish) * 100), 3))
        percent_change_total.append(percent_change)
    return percent_change_total


def up_down_change(full_list):
    up_down_total = []
    for num in full_list:
        if num >= 0:
            up_down = "🔺"
        else:
            up_down = "🔻"
        up_down_total.append(up_down)
    return up_down_total


percent_change_list = retrieve_close(complete_date_list)

percent_change_total_account = round(((float(data[today]['4. close']) - PURCHASE_PRICE) / PURCHASE_PRICE) * 100, 3)

get_news()

up_down_list = up_down_change(percent_change_list)

up_down_total_account = "🔺" if percent_change_total_account >= 0 else "🔻"

total_message = f'''
TOTAL CHANGE:
        {STOCK}     {up_down_total_account} {percent_change_total_account}'''
daily_message = f'''
Daily Change:
        {STOCK}     {up_down_list[0]}   {percent_change_list[0]}%'''
weekly_message = f'''
Week on Week Change:
        {STOCK}     {up_down_list[1]}   {percent_change_list[1]}%'''
monthly_message = f'''
Month on Month Change:
        {STOCK}     {up_down_list[2]}   {percent_change_list[2]}%'''
last_message = f'''
Total on file history Change:
        {STOCK}     {up_down_list[3]}   {percent_change_list[3]}%'''
message_body = ''

for item in range(0, len(news_articles) - 1):
    message_body += (
        f'''
        Headline: {news_articles[item]['title']}
        Brief: {news_articles[item]['description']}
        URL: {news_articles[item]['url']}\n
        '''
    )

right_arrow = "➡️"

message = f"""
{total_message}
        {right_arrow}       Since: {INITIAL_PURCHASE_DATE}
{daily_message}   
        {right_arrow}       Since: {yesterday}
{weekly_message}
        {right_arrow}       Since: {week_ago}
{monthly_message}
        {right_arrow}       Since: {month_ago}

{message_body}
"""

send_email(message=message, subject=f'TSLA Daily Info: {date}')
