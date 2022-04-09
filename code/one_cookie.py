#importing the required modules
import pandas as pd
import pickle
from tmux_linkedin import *
from tmux_linkedin import LinkedIn
import random
import os
import time
from pyvirtualdisplay import Display
 # Starting Display for 
display = Display(visible=0, size=(1920, 1080))  
display.start()
#driver
chrome_options = Options()  
#chrome_options.add_argument("--headless") 
path = '/home/celebal1/LinkedIn/chromedriver'
driver = webdriver.Chrome(path,options=chrome_options)

#cookie
cookie_path = "cookies/{}".format('cookies_john_smith.pkl')
file = open("logs/scraper_log_cookie_celebal.txt", "a")
file.write('current cookie : {}\n'.format(cookie_path))

#Add LinkedIn cookie
def load_cookies():
    cookie = pickle.load(open(cookie_path, "rb"))
    driver.get('https://www.linkedin.com/')
    driver.add_cookie(cookie)
    driver.refresh() 
    linkedin_url=driver.current_url 
    #print(linkedin_url)
    file = open("logs/scraper_log_cookie_celebal.txt", "a")
    file.write("linkedin url after adding cookie -> {}\n".format(linkedin_url))

df1 = pd.read_csv('data/companies_data.csv')
df1 = df1.iloc[:100]

outputs, errors, detailed_results = [], [], []
Results = pd.DataFrame()

load_cookies()
counter = 0
for i in range(5000):
    counter += 1
    file = open("logs/scraper_log_cookie_celebal.txt", "a")
    file.write('counter : {}\n'.format(counter))
    results_d = {}
    ##getting company name and company website
    j = i%100
    company_name = df1.iloc[j,3]
    company_website = df1.iloc[j, 0]
    
    
    obj=LinkedIn(company_name, company_website, driver) 
    output_ = obj.get_results()
    print(output_)
    ##appending results
    errors.append(obj.error_dict)
    outputs.append(output_)
    detailed_results.append(results_d)
    ## saving results in a dataframe
    results_d['company'] = company_name
    results_d['website'] = company_website
    results_d['locations'] = obj.locations_data
    results_d['sales_data'] = obj.sales_data
    results_d['restricted'] = obj.restricted
    results_d['authwall'] = obj.authwall
    results_d['data_error1'] = obj.error_dict['data_error1']
    results_d['data_error2'] = obj.error_dict['data_error2']
    results_d['scraper_error'] = obj.error_dict['scraper_error']
    results_d['select_section_error'] = obj.error_dict['select_section']
    results_d['linkedin_url'] = obj.linkedin_url
    Results = Results.append(results_d, ignore_index=True)
    ##Saving outputs
    Results.to_csv("outputs/TmuxResults_cookie_celebal.csv")
    pickle.dump(outputs, open('outputs/TmuxOutputs_cookie_celebal.pkl','wb'))
    pickle.dump(errors, open('outputs/TmuxErrors_cookie_celebal.pkl', 'wb'))
    pickle.dump(detailed_results, open('outputs/detailed_results_cookie_celebal.pkl', 'wb'))
    
    if obj.authwall:
        print('##########AUTHWALL#############################')
        file = open("logs/scraper_log_cookie_celebal.txt", "a")
        file.write('##########AUTHWALL#############################\n')
        break
    if obj.restricted:
        print("!!!!!!!!!!!!!!!!!!!!RESTRICTED!!!!!!!!!!!!!!!!")
        file = open("logs/scraper_log_cookie_celebal.txt", "a")
        file.write("!!!!!!!!!!!!!!!!!!!!RESTRICTED!!!!!!!!!!!!!!!!\n")
        break
    if obj.linkedin_url.find('checkpoint') != -1 :
        print("##########Checkpoint##############")
        file = open("logs/scraper_log_cookie_celebal.txt", "a")
        file.write("##########Checkpoint##############\n")
        break

    ##to ensure same file is not being used
    if 'error' not in output_.keys():
        try:
            os.remove('content.txt')
            os.remove('locations_content.txt')
        except Exception as e:
            print('File!!!!!!!!!!!')
            print(e)
    
    min_ = random.randint(1,3)
    time.sleep(min_*60)
    
driver.close()
display.stop()
