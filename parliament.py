import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import requests

BASE_INFORMATION_LINK = "https://www.camara.cl/camara/diputado_detalle.aspx?prmid="
TRANSPARENCY_LINK = "https://www.camara.cl/camara/transparencia_diputado.aspx?prmId="

chrome_options = Options()
chrome_options.add_argument("no-sandbox")
chrome_options.add_argument("headless")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--disable-notifications")
driver = webdriver.Chrome("./chromedriver", options=chrome_options)

months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

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
        facebook = driver.find_element_by_css_selector("li[class=facebook] > a").get_attribute("href")
        diputado["facebook"] = facebook
    except Exception as E:
        diputado["facebook"] = None   
    #NOTE: Some have or dont have facebook
    try:
        twitter = driver.find_element_by_css_selector("li[class=twitter] > a").get_attribute("href")
        diputado["twitter"] = twitter
    except Exception as E:
        diputado["twitter"] = None  
    

    return diputado


def post(id, month=3, year=2019):
    CAMARA_LINK = 'https://www.camara.cl/camara/transparencia_diputado.aspx?prmId=%s' % id
    params={
    'ctl00$ArbolPlaceHolder$ScriptManager1':'ctl00$mainPlaceHolder$UpdatePanel1|ctl00$mainPlaceHolder$ddlMes',
    'ctl00$mainPlaceHolder$ddlDiputados': id,
    'ctl00$mainPlaceHolder$ddlMes:': 3,
    'ctl00$mainPlaceHolder$ddlAno': 2019
    }
    response = requests.post(CAMARA_LINK, data=params)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id": "table_gasop"}).find_all("tr")
    labels = []
    values=[]
    costos = {}
    costos["month"] = months[month-1]
    costos["year"] = year
    for row in table:
        try:
            costos[row.find_all("td")[0].get_text().strip()] = row.find_all("td")[1].get_text().replace("\r", "").strip()
        except:
            pass
    print(costos)
    print("\n")


def get_expenditure_data(driver, id):
    print("\n\nTransparencia")
    SPECIFIC_TRANSPARENCY_LINK = TRANSPARENCY_LINK + str(id)
    
    driver.get(SPECIFIC_TRANSPARENCY_LINK)
    
    select_dates = driver.find_elements_by_css_selector("div[id=ctl00_mainPlaceHolder_UpdatePanel1] > p ")
    select = select_dates[0].find_element_by_tag_name('select')

    table = driver.find_elements_by_css_selector("table[id=table_gasop] > tbody > tr")
    costos = {}
    costos["year"] = 2019
    costos["month"] = "Enero"
    gasto_total = 0
    for row in table:
        cells = row.find_elements_by_tag_name("td")
        costos[cells[0].text.lower().capitalize()] = int(cells[1].text.replace(".",""))
        gasto_total += int(cells[1].text.replace(".",""))
    print("Gasto total del mes %s año %s es %s" % ("Enero", "2019", str(gasto_total)))
    print(costos)
    print("\n")



try:
    #gets info such as name, email, SS.MM, etc.

    print("\n")
    diputado_id = input("ID de diputado: ")
    print(get_basic_info(driver, diputado_id))
    get_expenditure_data(driver, diputado_id)
    time.sleep(4)
    driver.quit()
    driver.close()
  
    '''
    for z in range(1,13):
        print(z)
        time.sleep(4)
        post(1009, z, 2019)
    '''
    #post(1009)
except Exception as E:
    print(E)
