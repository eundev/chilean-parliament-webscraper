import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

BASE_INFORMATION_LINK = "https://www.camara.cl/camara/diputado_detalle.aspx?prmid="
TRANSPARENCY_LINK = "https://www.camara.cl/camara/transparencia_diputado.aspx?prmId="

chrome_options = Options()
chrome_options.add_argument("no-sandbox")
chrome_options.add_argument("headless")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--disable-notifications")
driver = webdriver.Chrome("./chromedriver", options=chrome_options)

months = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


def get_basic_info(driver, id):
    print("\n\nINFORMACION BASE")
    PROFILE_LINK = BASE_INFORMATION_LINK + str(id)
    diputado = {"id": id}
    driver.get(PROFILE_LINK)
    name = driver.find_element_by_tag_name("h3").text
    test = driver.find_elements_by_css_selector("div[class=summary] > p")
    diputado["nombre"] = " ".join(
        [sname.lower().capitalize() for sname in name.split(" ")][1:]
    )
    diputado["email"] = driver.find_element_by_css_selector("li[class=email] > a").text
    diputado["comunas"] = test[0].text
    diputado["distrito"] = test[1].text
    diputado["region"] = test[2].text
    diputado["comite"] = test[3].text
    try:
        facebook = driver.find_element_by_css_selector(
            "li[class=facebook] > a"
        ).get_attribute("href")
        diputado["facebook"] = facebook
    except Exception as E:
        diputado["facebook"] = None
    # NOTE: Some have or dont have facebook
    try:
        twitter = driver.find_element_by_css_selector(
            "li[class=twitter] > a"
        ).get_attribute("href")
        diputado["twitter"] = twitter
    except Exception as E:
        diputado["twitter"] = None

    return diputado


def get_expenditure_data(driver, id):
    print("\n\nTransparencia")
    SPECIFIC_TRANSPARENCY_LINK = TRANSPARENCY_LINK + str(id)

    driver.get(SPECIFIC_TRANSPARENCY_LINK)

    select_dates = driver.find_elements_by_css_selector(
        "div[id=ctl00_mainPlaceHolder_UpdatePanel1] > p "
    )
    gastos_mensuales = []

    for i in range(1, 13):
        time.sleep(0.5)
        select = Select(
            driver.find_element_by_xpath(
                "//select[@name='ctl00$mainPlaceHolder$ddlMes']"
            )
        )
        select.select_by_value(str(i))
        time.sleep(0.5)
        table = driver.find_elements_by_css_selector(
            "table[id=table_gasop] > tbody > tr"
        )
        costos = {}
        costos["year"] = 2019
        costos["month"] = months[i - 1].capitalize()
        gasto_total = 0
        for row in table:
            cells = row.find_elements_by_tag_name("td")
            costos[cells[0].text.lower().capitalize()] = int(
                cells[1].text.replace(".", "")
            )
            gasto_total += int(cells[1].text.replace(".", ""))
        costos["total"] = gasto_total
        gastos_mensuales.append(costos)
    return gastos_mensuales


try:
    print("\n")
    diputado_id = input("ID de diputado: ")
    print(get_basic_info(driver, diputado_id))
    gastos = get_expenditure_data(driver, diputado_id)
    total = 0
    for gasto in gastos:
        total += gasto["total"]
    print("Gastos desde Enero a Junio: %s" % total)
    print("\n")
    time.sleep(2)
    driver.quit()
    driver.close()
except Exception as E:
    print(E)
