import requests
from datetime import *
from datetime import timedelta
import smtplib
from email.mime.text import MIMEText


STOCK = "SLB"
COMPANY_NAME = "Schlumberger"
FUNCTION = "TIME_SERIES_DAILY"
stock_api_key = "your_stock_api_key"
news_api_key = "your_news_api_key"
MY_EMAIL = "email@gmail.com"
PASSWORD = "your_password"


def stock_perc_change():
    params = {
        "function": FUNCTION,
        "symbol": STOCK,
        "outputsize": "compact",
        "datatype": "json",
        "apikey": stock_api_key,
    }

    response = requests.get(url="https://www.alphavantage.co/query", params=params)
    response.raise_for_status()
    stock_data = response.json()["Time Series (Daily)"]

    today = datetime.now()
    yesterday = str(today - timedelta(days=1)).split()[0]
    day_before_yesterday = str(today - timedelta(days=2)).split()[0]

    yesterday_price = float(stock_data[yesterday]["4. close"])
    day_before_yesterday_price = float(stock_data[day_before_yesterday]["4. close"])

    perc_change = 100 * (1 - (day_before_yesterday_price / yesterday_price))

    return perc_change


def get_news():
    params = {
        "q": COMPANY_NAME,
        "language": "en",
        "sortBy": "popularity",
        "apiKey": news_api_key,
    }

    response = requests.get(url="https://newsapi.org/v2/everything", params=params)
    response.raise_for_status()
    news_data = response.json()["articles"]

    news_articles_title_list = [news_data[index]["title"] for index in range(3)]
    news_articles_desc_list = [news_data[index]["description"] for index in range(3)]
    news_articles_url_list = [news_data[index]["url"] for index in range(3)]

    news_article_dict = {
        "title": news_articles_title_list,
        "description": news_articles_desc_list,
        "url": news_articles_url_list
    }

    return news_article_dict


perc_change = stock_perc_change()
news_articles = get_news()

if perc_change <= -5 or perc_change >= 5:
    if perc_change >= 5:
        perc_change_text = "🔺" + str(round(perc_change, 2))
    elif perc_change <= -5:
        perc_change_text = str(round(perc_change, 2)).replace("-", "🔻")

    text = f"""
    SLB: {perc_change_text}%

    Headline: {news_articles["title"][0]}
    
    Brief: {news_articles["description"][0]}
    
    Article url: {news_articles["url"][0]}

    Headline: {news_articles["title"][1]}
    
    Brief: {news_articles["description"][1]}
    
    Article url: {news_articles["url"][1]}

    Headline: {news_articles["title"][2]}
    
    Brief: {news_articles["description"][2]}
    
    Article url: {news_articles["url"][2]}
    """
    message = MIMEText(text, "plain", "utf-8")
    message["Subject"] = "SLB Stock Update"
    message["From"] = MY_EMAIL
    message["To"] = MY_EMAIL

    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=PASSWORD)
        connection.sendmail(
            from_addr=message["From"],
            to_addrs=message["To"],
            msg=message.as_string()
        )

