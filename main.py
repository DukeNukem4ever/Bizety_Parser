# Импорт библиотек
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import csv
import json
import re
import chromedriver_binary

# Запуск веб-драйвера
option = Options()
option.add_argument("--disable-infobars") 
browser = webdriver.Chrome()


# Извлечение данных из статьи
def extract_info(url):
    browser.get(url)
    soup = BeautifulSoup(browser.page_source,
                         features="lxml")

    info = browser.find_elements(By.XPATH, "//script[@class = 'yoast-schema-graph']")[0]
    info_json = json.loads(info.get_attribute('innerHTML'))
    information = info_json['@graph']
    key_inf = information[0]

    # Достаём заголовок
    title = soup.find_all("h1", {"class": "elementor-heading-title elementor-size-default"})[0].text.replace(
        '\n','').replace(
            '\t','').replace(
                '\r','')
    print(title)

    # Достаём автора
    author = key_inf['author']['name']
    if author == '':
        author = 'None'
    print(author)

    # Достаём дату
    date = key_inf['datePublished']
    date = re.sub('T.+', '', date)
    print(date)

    # Достаём текст
    text = soup.find_all("div", {"class": "elementor-widget-container"})[-2].text.replace('\n',' ').replace('\r', ' ')
    text = re.sub('   FacebookTwitterРесурс  ', '', text)
    if text.startswith(' '):
        text = text[1:]
    if text.endswith(' '):
        text = text[:-1]

    # Собираем всё воедино
    page_info = {
                'title': title, 
                'author': author,
                'date': date,
                'url': url,
                'text': text
                }
    
    return page_info


urls = []

# Нумерация страниц начнётся с 1
page_num = 1

# Обработка всех статей на страницах
while True:
    base_url = "https://bizety.com/page/%s" % str(page_num)
    browser.get(base_url)
    print()
    print(browser.current_url)
    print()
    try: 
        soup = BeautifulSoup(browser.page_source,
                            features="lxml")
        post_check = soup.find_all("div", {"class": "elementor-post__text"})
        if post_check != []:
            for tag in set(soup.find_all("a", {"class": "elementor-post__read-more"})):
                url = tag['href']
                urls.append(extract_info(url))
                print()
                time.sleep(10)
            print("Analysis complete")
            page_num += 1
        else:
            break
    except IndexError:
        browser.close()
        browser = webdriver.Chrome()
        
# Удаляем копии
urls = [dict(t) for t in {frozenset(d.items()) for d in urls}]
urls_full = []

# Назначаем каждой записи идентификатор
u_id = 0

for u in urls:
    u1 = {"id": u_id}
    u, u1 = u1, u
    u.update(u1)
    urls_full.append(u)
    u_id += 1


# Всё записываем в csv-файл
head = urls[0].keys()
with open('output_table.csv', 'w', newline='', encoding="utf-8") as output:
    dict_writer = csv.DictWriter(output, head)
    dict_writer.writeheader()
    dict_writer.writerows(urls)
    print("Done!")
