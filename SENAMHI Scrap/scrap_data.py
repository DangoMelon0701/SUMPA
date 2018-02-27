# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 02:17:11 2018

@author: Gerardo A. Rivera  Tello
"""

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ast import literal_eval

#%%
def load_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    
    driver = webdriver.Chrome(chrome_options=options)
    return driver

#%%
def load_url(driver,url,to_find,by,ref,_type=False,name='main'):
    driver.get(url)
    try:
        WebDriverWait(driver,10).until(EC.presence_of_element_located((by,ref)))
    except:
        driver.implicitly_wait(10)
#    driver.get_screenshot_as_file("{}.png".format(name))
    
    source = BeautifulSoup(driver.page_source,'lxml')
    if _type:
        search = source.findAll(to_find,type=_type)
    else:
        search = source.findAll(to_find)
    return search

#%%
def parse_data(js_body):
    ix = js_body.find('ubica0')
    info = js_body[ix:-6].split('var')
    
    df = pd.DataFrame(columns=['Estacion', 'Latitud', 'Longitud', 'Altitud',\
                               'Departamento', 'Provincia', 'Distrito',\
                               'Codigo', 'Tipo', 'Tecnologia' ,'Estado'],\
                        index = range(len(info)))
    
    for num,line in enumerate(info):
        dummy = line.split(';',1)
        lat,lon = literal_eval(dummy[0][dummy[0].find('('):dummy[0].find(')')+1])
        
        meta =  [dat_str.replace("'","") for dat_str in dummy[1][28:-3].split(',')]
        
        df.loc[num]=pd.Series({'Estacion':meta[1].split('-')[0], 'Latitud':lat, 'Longitud':lon,\
              'Departamento':meta[6], 'Provincia':meta[7], 'Distrito':meta[8],\
              'Codigo':meta[9], 'Tipo':meta[10], 'Tecnologia':meta[2],'Estado':meta[11]})
    return df

#%%
def get_url(code):
    base_url = 'http://www.senamhi.gob.pe/include_mapas/_dat_esta_tipo.php?estaciones={}'
    return base_url.format(code)

#%%
def get_altitude(driver,est_data):
    codes = est_data['Codigo'].copy()
    codes = codes.apply(get_url)

    for num,row in enumerate(codes):
        while True:
            try:
                search = load_url(driver,row,'td',By.ID,'estaciones', name='{}_{}'.format(num\
                                        ,est_data.loc[num][0].lower().encode('utf8')\
                                          .replace('\xc3','n').replace('\xb1a','a')))
                est_data.loc[num][3]=float(search[14].text.replace("'",""))
                print 'Done {}'.format(num)
                break
            except:
                print 'Failed ... Retrying'
    return est_data

#%%
if __name__ == '__main__':
    map_est = "http://www.senamhi.gob.pe/include_mapas/_map_data_hist.php?drEsta=15"
    driver = load_driver()
    print 'Loading {}'.format(map_est)
    script_data = load_url(driver,map_est,'script',By.CLASS_NAME,'gm-style-mtc',_type='text/javascript')
    print 'Done\n'
    raw_data = script_data[1].text
    est_data = parse_data(raw_data)
    print 'Getting altitudes'
    est_data = get_altitude(driver,est_data)
    print 'Done'
    driver.quit()
    #%%
    est_data2 = est_data.copy()
#    for column in est_data2:
#        if (column != 'Latitud') and (column != 'Longitud') and (column != 'Altitud'):
#            est_data2[column] = est_data2[column].str.encode('utf8')
#        else:
#            continue
    writer = pd.ExcelWriter('estaciones_senamhi.xlsx')
    est_data2.to_excel(writer,'Estaciones_Senamhi',index=None)
    writer.save()