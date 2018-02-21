from bs4 import BeautifulSoup
from selenium import webdriver

url = "http://www.senamhi.gob.pe/include_mapas/_map_data_hist.php?drEsta=15"
options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(chrome_options=options)
driver.get(url)

driver.implicitly_wait(15)
driver.get_screenshot_as_file("test.png")