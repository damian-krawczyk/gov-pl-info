from urllib.request import urlopen
import ssl
from bs4 import BeautifulSoup, SoupStrainer
import datetime
import os
import telegram
import dateparser
import goslate

def get_articles(url):

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    page = urlopen(url, context=ctx)
    html = page.read().decode("utf-8")

    product = SoupStrainer('article')
    soup = BeautifulSoup(html, "html.parser", parse_only=product)

    articles = soup.find_all("li")
    # print(len(articles))
    article_list = []

    number_of_articles =0

    for count, article in enumerate(articles):

        article_date = article.find_all(class_="date")
        article_date = article_date[0].string.strip()
        article_date = datetime.datetime.strptime(article_date, "%d.%m.%Y").strftime("%Y-%m-%d")
        article_list.append({"id": count})
        article_list[count].update({"date": article_date})
        article_name = article.find_all(class_="title")
        article_list[count].update({"title": article_name[0].string})
        article_intro = article.find_all(class_="intro")
        if article_intro:
            article_list[count].update({"intro": article_intro[0].string})
        else:
            article_list[count].update({"intro": None})
        article_urls = article.find_all(href=True)
        article_list[count].update({"url": "https://www.gov.pl"+article_urls[0]['href']})

    return article_list

def show_articles_for_given_date(articles, date):

    article_list = []
    article_number = 0
    for article in articles:
        if article['date'] == date:
            # print(article)
            # print(article_number)
            article_list.append(article)
            article_number+=1

    if not article_number:
        article_list.append({"warning": f"Brak artykułów na dzień {date}"})
    
    return article_list

def send_message(article, feed_name, article_type, channel, test_channel, token):
    gs = goslate.Goslate()

    bot = telegram.Bot(token=token)

    if 'warning' in article:
        info = article['warning']
        info_en = info
        message = f"{feed_name}\n{info}\n{info_en}"
        print(message)
        bot.send_message(test_channel,text=message, parse_mode='Markdown')

    else:
        date = article['date']
        print(f'date: {date}')
        title = article['title']
        print(f'title: {title}')
        title_en = title
        print(f'title en: {title_en}')
        url = article['url']
        print(f'url: {url}')

        intro = article['intro']
        print(f'intro: {intro}')
        if intro:
            intro_en = intro
            print(f'intro en: {intro_en}')
            message = f"`{date}` - {article_type}\n**PL:** {title}\n\n{intro}\n---\n**EN:** {title_en}\n\n{intro_en}\n---\n[Szczegóły / Details]({url})"
        else:
            message = f"`{date}` - {article_type}\n**PL:** {title}\n---\n**EN:** {title_en}\n---\n[Szczegóły / Details]({url})"
        
        print(message)
        bot.send_message(channel,text=message, parse_mode='Markdown')


url = os.environ['FEED_URL']
given_date = dateparser.parse(os.environ['GIVEN_DATE'], date_formats=["%Y-%m-%d"]).strftime("%Y-%m-%d")
feed_name = os.environ['FEED_NAME']
article_type = os.environ['ARTICLE_TYPE']
channel = os.environ['CHANNEL_URL']
test_channel = os.environ['TEST_CHANNEL_URL']
token = os.environ['TELEGRAM_TOKEN']

articles = get_articles(url)

# print(articles)
print('Number of all articles: ', len(articles))

target_articles = show_articles_for_given_date(articles, given_date)

# print(target_articles)
print('Number of target articles: ', len(target_articles))

for article in target_articles:
    # print(article,"\n")
    send_message(article, feed_name, article_type, channel, test_channel, token)
