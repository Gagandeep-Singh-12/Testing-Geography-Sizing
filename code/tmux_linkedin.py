from lib2to3.pgen2 import driver
import time
import os
import json
import re
import datetime
import os
import pickle
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import  TimeoutException 
from bs4 import BeautifulSoup
import numpy as np
#import pandas as pd
chrome_options = Options()  
#chrome_options.add_argument("--headless") 
#chrome_options.add_argument("--window-size=1920,1080")
#chrome_options.add_argument("--start-maximized")

class LinkedIn():
    
    def __init__(self,company_name, company_website, driver):
        self.company_name = company_name
        self.company_website = company_website
        self.sales_data = None
        self.locations_data = None
        self.headquarter = None
        self.error_dict = {}
        self.error_dict['company_name'] = self.company_name
        self.error_dict['company_website'] = self.company_website
        self.error_dict['data_error1'] = np.nan
        self.error_dict['data_error2'] = np.nan
        self.error_dict['scraper_error'] = np.nan
        self.error_dict['select_section'] = np.nan
        self.restricted = False
        self.authwall = False
        #self.cookie_path = cookie_path
        self.linkedin_url = None
        #getting driver
        #if not driver_path:
        #    raise ValueError("Chrome driver Error!!!")
        #elif driver_path:
        #    print("Taking passed chrome driver")
        #    self.driver_path = driver_path
            
        #s = Service(self.driver_path)

        #Intializing chrome Driver
        #self.driver = webdriver.Chrome('/home/celebal/.wdm/drivers/chromedriver/linux64/99.0.4844.51/chromedriver',options=chrome_options)
        self.driver = driver
        self.driver.maximize_window()
        #self.driver.implicitly_wait(5)
        #self.driver.maximize_window()
        
        
    #main method to get desired results  
    def get_results(self):
        print("company : {}  & company_website : {}".format(self.company_name, self.company_website))
        file = open("logs/scraper_log_cookie_celebal.txt", "a")
        file.write("company : {}  & company_website : {}".format(self.company_name, self.company_website))
        file.write("\n")
        #self.load_cookies()
        time.sleep(random.randint(15,30))
        #self.login()
        results = False
        linkedin_link = self.search_company_webiste()
        time.sleep(random.randint(15,30))
        if linkedin_link:
            self.write_content()
            results = self.scraper(linkedin_link)
        else:
            linkedin_link = self.search_google()
            time.sleep(random.randint(15,30))
            #website has been verified and the correspoding content has been written
            if linkedin_link:
                results = self.scraper(linkedin_link)
                
        #self.close_drivers()
        
        output = {'company_name': self.company_name,
                  'company_website': self.company_website}
        
        if results:
            output['sales_data'] = self.sales_data
            output['locations_data'] = self.locations_data
        else:
            output['error'] = 'company not found on linkedin'
        output['timestamp'] = datetime.datetime.now()
        return output

###########################           UTILITIES            ##########################
    '''
    def load_cookies(self):
        cookie = pickle.load(open(self.cookie_path, "rb"))
        self.driver.get('https://www.linkedin.com/')
        self.driver.add_cookie(cookie)
        self.driver.refresh() 
        self.linkedin_url=self.driver.current_url 
        print(self.linkedin_url)
        file = open("logs/scraper_log_cookie_celebal.txt", "a")
        file.write("linkedin url after adding cookie -> {}\n".format(self.linkedin_url))
    '''
   
    
    def wait(self, condition, delay):
        return WebDriverWait(self.driver, delay).until(condition)

    def wait_for_element(self, selector, delay=10):
        return self.wait(
            EC.presence_of_element_located((
                By.XPATH, selector)),delay
            )
    '''
     def close_drivers(self):
        self.driver.quit()
    '''
   
        
    # Regex method for website filter
    def regex(self,item):
        try:
            m = re.search("(https)?(http)?(://)?(www.)?([A-Za-z_0-9.-]+).*", item)
            #print(m)
            if m:
                #print(item, m.group(5)) 
                return str(m.group(5)).lower()
        except Exception as e:
            print(e)
            
    def select_section(self, driver, section):
        try:
            self.linkedin_url = driver.current_url
            file = open("logs/scraper_log_cookie_celebal.txt", "a")
            file.write("linkedin url in select section -> {}\n".format(self.linkedin_url))
            
            if driver.current_url.find('authwall?') != -1:
                self.authwall = True
                file = open("logs/scraper_log_cookie_celebal.txt", "a")
                file.wrie("authwall = True\n")
                self.close_drivers()
            
            self.wait_for_element("//ul[@class='org-page-navigation__items ']/li/a")
            time.sleep(10)
            ##Random 
            time.sleep(random.randint(15,30))
            ##
            org_page_navigation_items = self.driver.find_elements(By.XPATH, "//ul[@class='org-page-navigation__items ']/li/a")
            #locate hyperlinks to required Section
            sections = [my_elem.get_attribute('href') for my_elem in org_page_navigation_items]
            link = [sec for sec in sections if sec.split('/')[-2] == section][0]
            ##Random 
            time.sleep(random.randint(15,30))
            ##
            driver.get(link)
            ##vhecking for wether linkedin has restricted your account
            if section == 'people':
                checking = self.check_for_restriction()
                if checking:
                    self.restricted = True
                    file = open("logs/scraper_log_cookie_celebal.txt", "a")
                    file.write('Restricted')

            ##
         
        except TimeoutException as e:
            #print(e)
            print("select section error for section {}".format(section))
            file = open("logs/scraper_log_cookie_celebal.txt", "a")
            file.write("select section error for section {}".format(section))
            file.write("\n")
            self.error_dict['select_section'] = "select section error for section {}".format(section)
            pass

    def check_for_restriction(self):
        try:
            self.wait_for_element('//p')
            time.sleep(4)
            p_elems = self.driver.find_elements(By.XPATH, '//p')
            check = 'The filters applied did not return any results. Try clearing some filters and try again.'
            if check in [e.text for e in p_elems] :
                return True
            return False 
        except:
            return False

    ##this will write locations content and when this function is called, driver is at the about section
    def write_content(self):
    
        about_source = self.driver.page_source
        global linkedin_soup
        linkedin_soup = BeautifulSoup(about_source.encode("utf-8"), "html")
        content = linkedin_soup.prettify()
        with open('content.txt', 'w') as f:
            f.write(content)
            
        with open('content.txt') as f1:
            for line in f1.readlines():
                if (line.find("confirmedLocations")!=-1):
                    #print("Y")
                    with open('locations_content.txt','w') as lc:
                        lc.write(line)
                    break
                
    def find_locations(self, content):
   
        with open(content, 'r') as f:
            d = f.read()
        res = json.loads(d)
        #locations => keys-country, values = city
        locations = {}
        headquarter_loc = {}
        
        for item in res['included']:
            if 'confirmedLocations' in item.keys():
                #print(len(item['confirmedLocations']))
                for loc_dict in item['confirmedLocations']:      
                    try:
                        if loc_dict['city']:
                            city = loc_dict['city']
                    except:
                        city = np.NaN
                        
                    if loc_dict['headquarter']:
                        headquarter_loc['country'] = loc_dict['country']
                        headquarter_loc['city'] = city
                    #data about locations where headquarter = false        
                    if loc_dict['country'] in locations.keys():
        
                        locations[loc_dict['country']].append(city)
                    else:
                        locations[loc_dict['country']] = []
                        locations[loc_dict['country']].append(city)
                break
            
        if len(locations) == 0:
            self.error_dict['locations'] = True
            
        return locations, headquarter_loc 
    
    def find_locations2(self,content):
   
        with open(content, 'r') as f:
            d = f.read()
        res = json.loads(d)
        #locations => keys-country, values = city
        locations = {}
        headquarter_loc = {}
        
        for item in res['included']:
            if 'confirmedLocations' in item.keys():
                #print(item['confirmedLocations'])
                #print(len(item['confirmedLocations']))
                for loc_dict in item['confirmedLocations']:      
                    try:
                        if loc_dict['city']:
                            city = loc_dict['city']
                    except:
                        city = np.NaN
                        
                    if loc_dict['headquarter']:
                        headquarter_loc['country'] = loc_dict['country']
                        headquarter_loc['city'] = city
                    #data about locations where headquarter = false        
                    if loc_dict['country'] in locations.keys():
        
                        locations[loc_dict['country']].append(city)
                    else:
                        locations[loc_dict['country']] = []
                        locations[loc_dict['country']].append(city)
                break
        #'locations not found in included key'   
        if len(locations) == 0:
            self.error_dict['data_error1'] = True
        #when data is in data key though leading to discrpancy
        try:
            
            if len(locations) == 0:
                for loc_dict in res['data']['confirmedLocations']:
                    try:
                        if loc_dict['city']:
                            city = loc_dict['city']
                    except:
                        city = np.nan
                    if loc_dict['headquarter']:
                        headquarter_loc['country'] = loc_dict['country']
                        headquarter_loc['city'] = loc_dict['city']
                    if loc_dict['country'] in locations.keys():
                            locations[loc_dict['country']].append(city)
                    else:
                        locations[loc_dict['country']] = []
                        locations[loc_dict['country']].append(city)
        except:
            #print('finding locations in data key')
            self.error_dict['data_error2'] = True
             
        return locations, headquarter_loc
    
    def get_sales_data(self):
        try:
            self.select_section(self.driver, 'people')

            ##Random 
            time.sleep(random.randint(15,30))
            ##
            #click next button
            self.wait_for_element('//button[@aria-label="Next"]').click()
            time.sleep(random.randint(15,30))
            self.wait_for_element('//div[@class="insight-container"]//h4[text()="What they do"]')
            
            #caculation for applying sales filter
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            res = soup.find_all('h4')
            for i in res:
                if i.text.strip() == 'What they do':
                    buttons1 = i.findParent('div').find_next_siblings('button')
                    id = i.findParent('div').parent.parent.attrs['id']
            
            #which button is for sales?
            c = 1
            for i in buttons1:
                span = i.find('span')
                if span.text == 'Sales':
                    #print(span.find_parent('button'))
                    #print(c)
                    break
                c += 1
                
            sales_filter = '//*[@id="{}"]/div/button[{}]'.format(id,c)
            ##Random 
            time.sleep(random.randint(15,30))
            ##
            #click show more if present
            try:
                time.sleep(random.randint(15,30))
                self.wait_for_element('//*[@id="main"]/div[2]/div/div[1]/div[2]/button').click()
            except:
                pass
            
            try:
                time.sleep(random.randint(15,30))
                WebDriverWait(self.driver, 25).until(
                    EC.element_to_be_clickable((By.XPATH,sales_filter))
                ).click()
            except Exception as e:
                print('Time out at sales filter')
                file = open("logs/scraper_log_cookie_celebal.txt", "a")
                file.write('Time out at sales filter\n')
                pass
                #print('Time out at sales filter')
                #self.error_dict['get_sales_data1']= 'Time out at sales filter'
                #print(e)
            time.sleep(random.randint(15,30))
            self.wait_for_element('//div[@class="artdeco-card p4 m2 org-people-bar-graph-module__geo-region"]//button/div/strong')
            #get employee counts
            time.sleep(random.randint(15,30))
            emp_counts =self.driver.find_elements(By.XPATH, '//div[@class="artdeco-card p4 m2 org-people-bar-graph-module__geo-region"]//button/div/strong')
            time.sleep(random.randint(15,30))
            emp_counts = [elem.text for elem in emp_counts]  
            #get country names
            country_names = self.driver.find_elements(By.XPATH, '//div[@class="artdeco-card p4 m2 org-people-bar-graph-module__geo-region"]//button/div/span')
            time.sleep(random.randint(15,30))
            country_names = [country.text for country in country_names]
            
            sales_dic = {"country":country_names, "sales_count":emp_counts}
            return sales_dic
        
        #there are no members belonging to sales
        except Exception as e:
            print('exception inside get_sales_data_func')
            #print(e)
            #self.error_dict['get_sales_data2'] = 'inside get_sales_data_func'
            #print(e)
            return None
        
    def search_google(self):
        try:
            google_search_url = "https://www.google.com/search?q="+self.company_name+"+linkedin"
            time.sleep(random.randint(15,30))
            self.driver.get(google_search_url)
            time.sleep(random.randint(15,30))
            self.wait_for_element("//div[@id='search']")
            time.sleep(random.randint(15,30))
            linkedin_URLS = [my_elem.get_attribute("href") for my_elem in self.driver.find_elements(By.XPATH,"//div[@class='yuRUbf']/a")]
            #ensuring all links contain linkedin
            time.sleep(random.randint(15,30))
            linkedin_URLS = [link for link in linkedin_URLS if link.find('linkedin')!= -1 and link.find('company')!=-1]
            #print(linkedin_URLS)
            
            #eg. obj3 = LinkedIn(cookie, 'AppYea, Inc.', 'https://www.sleepxclear.com/')
            if len(linkedin_URLS) == 0:
                #print('YYYYY')
                m = re.search("(https)?(http)?(://)?(www.)?([A-Za-z_0-9-]+).*", self.company_website)
                search = m.group(5)
                time.sleep(random.randint(15,30))
                google_search_url = "https://www.google.com/search?q="+search+"+linkedin"
                time.sleep(random.randint(15,30))
                self.driver.get(google_search_url)
                time.sleep(random.randint(15,30))
                self.wait_for_element("//div[@id='search']")
                linkedin_URLS = [my_elem.get_attribute("href") for my_elem in self.driver.find_elements(By.XPATH,"//div[@class='yuRUbf']/a")]
                #ensuring all links contain linkedin
                time.sleep(random.randint(15,30))
                linkedin_URLS = [link for link in linkedin_URLS if link.find('linkedin')!= -1 and link.find('company')!=-1]
                #print(linkedin_URLS)
                            
            #verification
            for link_suggestion in linkedin_URLS:
                time.sleep(random.randint(15,30))
                if self.verify_website(link_suggestion):
                    return self.driver.current_url
            return False
                
        except Exception as e:
            #print('Error in google search')
            #print(e)
            return False       
        
    def verify_website(self, link):
        try:
            if ~(link.startswith('https://www.linkedin.com/company')):
                link = "https://www.linkedin.com/company"+link.split("company")[-1] 
                print(link)
            time.sleep(random.randint(15,30))
            self.driver.get(link)
            ##Random 
            time.sleep(random.randint(15,30))
            ##
            self.select_section(self.driver, 'about')
            self.wait_for_element('//section[@class="artdeco-card p5 mb4"]')
            self.write_content()
            
            for h in linkedin_soup.find_all('dt'):   
                if h.text.strip().lower() == 'website':
                    #print("y")
                    website = h.findNextSibling().find('a').attrs['href']
                    print("Website Checking : {} & {}".format(website,self.company_website))
                    web1 = self.regex(website)
                    web2 = self.regex(self.company_website)
                    print('web1 : {} & web2 : {}'.format(web1,web2))
                    
                    #if website is verified then we will collect required data
                    if web1 == web2:
                        #print('match')
                        return True
                    #case = where website mentioned in linkedin doesn't match with given company website
                    #but if we visit it, there is a match 
                    #eg.=>company_website=https://4sight.cloud/about & linkedin = http://www.4sightholdings.com
                    else:
                        path = '/home/celebal1/LinkedIn/chromedriver'
                        self.driver2 = webdriver.Chrome(path,options=chrome_options)
                        time.sleep(random.randint(15,30))
                        self.driver2.get(website)
                        time.sleep(random.randint(15,30))
                        website = self.driver2.current_url
                        time.sleep(random.randint(15,30))
                        self.driver2.close()
                        web1 = self.regex(website)
                        web2 = self.regex(self.company_website)
                        print('web1 : {} & web2 : {}'.format(web1,web2))
                        if web1 == web2:
                            return True
        
            return False
        #for case when we open a link of the employee belonging to a company
        except:
            return False     
    
    #if we find linked_link driver will open it &this func returns that linkedin link
    #here we don't need to verify the website
    def search_company_webiste(self):
        try:
            self.driver.get(self.company_website)
            time.sleep(random.randint(15,30))
            self.wait_for_element('//a')
            time.sleep(random.randint(15,30))
            links = [elem.get_attribute('href') for elem in self.driver.find_elements(By.XPATH, '//a')]
            
            #checking if link is in area tag (eg. 'https://www.01com.com/')
            try:
                area_links = self.driver.find_elements(By.XPATH, '//map/area[@href]')
                time.sleep(random.randint(15,30))
                links.extend([elem.get_attribute('href') for elem in area_links])
                time.sleep(random.randint(15,30))
            except:
                pass
            
            #checking for linkedin link
            for link in links:
                if link.find('https://www.linkedin.com/company') != -1:
                    time.sleep(random.randint(15,30))
                    self.driver.get(link)
                    time.sleep(random.randint(15,30))
                    self.select_section(self.driver, 'about')
                    time.sleep(random.randint(15,30))
                    return self.driver.current_url
            return False
            
        except Exception as e:
            #print(e)
            return False

    #scraper will assume that write_content() has already been called on 'About' section
    def scraper(self, company_link):
        try:
            #getting locations data
            locations, headquarter_loc  = self.find_locations2('locations_content.txt')
            self.locations_data = locations
            self.headquarter = headquarter_loc
            ##Random 
            time.sleep(random.randint(15,30))
            ##
            sales_dic = self.get_sales_data() 
            self.sales_data = sales_dic
            #if everything is scraped fine
            return True
            
        except Exception as e:
            print("ERROR : ",e)
            file = open("logs/scraper_log_cookie_celebal.txt", "a")
            file.write("Error inside scarper\n")
            print('error inside scraper')
            self.error_dict['scraper_error'] = True








