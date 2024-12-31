from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import time
import pandas as pd
from utils import configure_driver

def load_full_page(url):
    driver = configure_driver()
    driver.get(url)
    time.sleep(10)

    while True:
        try:
            button_more = driver.find_element(By.XPATH, "/html/body/div[4]/div[4]/div/div/div/div/div/div/div/div/div/div/div[2]/button")
            button_more.send_keys(Keys.RETURN)
            time.sleep(5)
        except (NoSuchElementException, ElementNotInteractableException):
            print("Todos os parceiros foram carregados ou o botão não está mais disponível.")
            break
    
    page_content = driver.page_source
    driver.quit()
    return page_content

def extract_main_data(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    card_selector = 'body > div.sc-81390cec-0.cgVNna > div:nth-child(4) > div > div > div > div > div > div > div > div > div > div > div > div > div'
    name_selector = 'p.sc-599fa389-68.sc-599fa389-201.iSwRRm.jizqnC'
    plan_selector = f'{card_selector} > a > div.sc-599fa389-8.kJcdgt > div.sc-599fa389-90.bIbdOT > span'
    link_selector = f'body > div.sc-81390cec-0.cgVNna > div:nth-child(4) > div > div > div > div > div > div > div > div > div > div > div.sc-599fa389-8.fgYahR > div > div > a'

    names, plans, links = [], [], []
    cards = soup.select(card_selector)
    for card in cards:
        name = card.select_one(name_selector)
        plan = card.select_one(plan_selector)
        link = card.select_one(link_selector)
        names.append(name.text if name else "N/A")
        plans.append(" ".join(plan.text.split()[4:]) if plan else "N/A")
        links.append(link.get('href') if link else "N/A")
    return pd.DataFrame({'name': names, 'base_plan': plans, 'links': links})

def extract_detailed_data(links):
    names, addresses, services, comorbidities = [], [], [], []
    for link in links:
        driver = configure_driver()
        driver.get(f"https://wellhub.com/{link}")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        address = soup.select_one('body > div.sc-81390cec-0.cgVNna > div.sc-3e899c21-0.bjuvVE > div.sc-599fa389-55.sc-c531bbc2-0.ldNeDQ.rDsOg > div > div > div > div.sc-599fa389-8.eGFUOy > div:nth-child(1) > div.sc-cdf5f068-1.fFzbcC > p')
        service_elements = soup.select('span.sc-599fa389-92.cfdBOy')
        comorbidity_elements = soup.select('p.sc-599fa389-74.sc-178740bd-5.LNliJ.gbrHZH')

        addresses.append(address.text if address else "N/A")
        services.append(",".join([s.text for s in service_elements]))
        comorbidities.append(",".join([c.text for c in comorbidity_elements]))
    return pd.DataFrame({'address': addresses, 'services': services, 'comorbidities': comorbidities})