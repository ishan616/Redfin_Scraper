from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import csv

df = pd.DataFrame(columns=['Address', 'Location', 'ZipCode',
                  'Price', 'Beds', 'Baths', 'sqft', 'ppsqft'])

borough = 'Staten Island'

zipList = []

with open('nyc-zip-codes.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if row[0] == borough:
            zipList.append(row[2])

zipList = zipList[1:]

# configure webdriver
options = Options()
options.headless = True  # hide GUI

# op = webdriver.ChromeOptions()
# op.add_argument('headless')

driver = webdriver.Chrome(options=options)

for zip in zipList:
    URL = f'https://www.redfin.com/zipcode/{zip}'
    driver.get(URL)
    driver.find_element(By.CLASS_NAME, 'modeOptionInnard.table').click()

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    pageButtons = driver.find_elements(By.CLASS_NAME, 'clickable.goToPage')
    if pageButtons:
        numPages = int(pageButtons[-1].text)
    else:
        numPages = 0

    for i in range(len(pageButtons)):
        pageButtons[i].click()

        page = driver.page_source

        soup = BeautifulSoup(page, 'html.parser')

        addressList = soup.find_all('a', attrs={'class': 'address'})
        locationList = soup.find_all('div', attrs={'class': 'location'})
        priceList = soup.find_all(
            'td', attrs={'class': 'column column_3 col_price'})
        bedsList = soup.find_all(
            'td', attrs={'class': 'column column_4 col_beds'})
        bathsList = soup.find_all(
            'td', attrs={'class': 'column column_5 col_baths'})
        sqftList = soup.find_all(
            'td', attrs={'class': 'column column_6 col_sqft'})
        ppsqftList = soup.find_all(
            'td', attrs={'class': 'column column_7 col_ppsqft'})

        for i in range(len(addressList)):
            datapoint = {'Address': addressList[i].text,
                         'Location': locationList[i].text,
                         'ZipCode': f'{zip}',
                         'Price': priceList[i].text[1:].replace(',', ''),
                         'Beds': bedsList[i].text,
                         'Baths': bathsList[i].text,
                         'sqft': sqftList[i].text.replace(',', ''),
                         'ppsqft': ppsqftList[i].text[1:].replace(',', '')}
            df.loc[len(df)] = datapoint

driver.quit()

df.to_csv(f'{borough}_data.csv', sep=',')
pass
