from selenium import webdriver  
from selenium.webdriver.common.keys import Keys
from linkedin_scraper import Person, actions
import time
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import numpy as np
from selenium.common.exceptions import InvalidSessionIdException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.service import Service as BraveService
from flask import Response

def videoBilgileriniGetir(link,userid,pass_word,total_records_required):

    req = int(total_records_required)

    link_1 = link.rsplit('&',1)
    link_page_default = link_1[0] + '&page={}'
    
    rounded = ((round(req/10)*10 ) + 10)
    
    page_count = int(rounded/10)

    page_links = []
    for i in range(0, page_count):
        page_link = link_page_default.format(i + 1)
        page_links.append(page_link)
    
    #option = webdriver.ChromeOptions()
    #option.binary_location = brave_path
    #driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
    #driver = webdriver.Chrome(service=BraveService(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()))

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.linkedin.com/")    
    
    email = driver.find_element("xpath","""//*[@id="session_key"]""")
    email.click()
    email.send_keys(userid) # ENTER EMAIL
    driver.implicitly_wait(5) #implicit wait for 5 seconds
    
    password = driver.find_element("xpath","""//*[@id="session_password"]""")
    password.click()
    password.send_keys(pass_word) #ENTER PASSWORD
    driver.implicitly_wait(5) #implicit wait for 5 seconds
    
    driver.find_element("xpath","""//*[@id="main-content"]/section[1]/div/div/form/button""").click() 
    
    driver.implicitly_wait(10) #implicit wait for 10 seconds
    
    time.sleep(5)
    person_link = []
    for i in range(0,len(page_links)):
        driver.get('{}'.format(page_links[i]))
        for j in range(1,11):
            temp = '//*[@id="main"]/div/div/div/ul/li[{}]/div/div/div[2]/div[1]/div[1]/div/span[1]/span/a'.format(j)
            person_link.append(driver.find_element("xpath",temp).get_attribute('href'))
    
    individual_link = []
    for i in range(0,len(person_link)):
        text = person_link[i].split("?",1)
        fin_link = text[0] + '/'
        individual_link.append(fin_link)
                     
    selected_link = []
    for i in range(0,req):
        selected_link.append(individual_link[i])

    source_main = []
    source_skill = []
    source_experience = []
    for i in range(0,req):
        driver.get('{}'.format(selected_link[i]))
        time.sleep(2.5)
        src_main = driver.page_source
        source_main.append(src_main)
                     
        #driver.implicitly_wait(10) #implicit wait for 10 seconds
        
        driver.get('{}'.format(selected_link[i] + 'details/skills/' ))
        time.sleep(2.5)
        src_skill = driver.page_source
        source_skill.append(src_skill)
                     
        #driver.implicitly_wait(10) #implicit wait for 10 seconds
        
        driver.get('{}'.format(selected_link[i] + 'details/experience/' ))
        time.sleep(2.5)
        src_exp = driver.page_source
        source_experience.append(src_exp)
    
    driver.close()
        
    name_list = []
    current_position_list = []
    current_location_list = []
    person_skills_list = []
    person_experience = []
    person_time = []
    
    for i in range(0,len(source_main)):
        
        soup_main = BeautifulSoup(source_main[i],'lxml')
        name_div = soup_main.find('div',{'class':'mt2 relative'})
        name = name_div.find('h1',{'class':'text-heading-xlarge inline t-24 v-align-middle break-words'}).get_text().strip()
        name_list.append(name)
        position = name_div.find('div',{'class':'text-body-medium break-words'}).get_text().strip()
        current_position_list.append(position)
        location = name_div.find('span',{'class':"text-body-small inline t-black--light break-words"}).get_text().strip()
        current_location_list.append(location)
        
        soup_skill = BeautifulSoup(source_skill[i],'lxml')
        skill_div = soup_skill.find_all('span',{'class':'mr1 t-bold'})
        skills = []
        for j in range(0,len(skill_div)):
            skill = skill_div[j].find('span').text
            skills.append(skill)
        person_skills_list.append(set(skills))
        
        soup_exp = BeautifulSoup(source_experience[i],'lxml')
        role_div = soup_exp.find_all('span',{'class':'mr1 t-bold'})
        company_div = soup_exp.find_all('span',{'class':'t-14 t-normal'})
        time_div = soup_exp.find_all('span',{'class':'t-14 t-normal t-black--light'})
        exp = []
        time_list = []
        for j in range(0,len(role_div)):
            role = role_div[j].find('span').text
            company = company_div[j].find('span').text
            temp = []
            for k in range(0,len(time_div)):
                time_val = time_div[k].find('span').text
                temp.append(time_val)
            time_list.append(temp)
            details = role + company
            exp.append(details)
        time_list = list(set([tuple(x) for x in time_list]))
        person_experience.append(exp)
        person_time.append(time_list)
    
    data = {'Link': selected_link,
            'Name':name_list,
            'Current_Position':current_position_list,
            'Current_Location':current_location_list,
            'Person_Skill':person_skills_list,
            'Person_Experience':person_experience,
            'Working_Time':person_time}
    global df
    df = pd.DataFrame(data)
    #csv_name = input("Enter CSV name:")
    df.to_csv('temp.csv')
    #print("CHECK THE FOLDER")
    #html = df.to_html()
    #return html

    return df

from flask import Flask, Markup, render_template, redirect, url_for, request, Response


    
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    
    if request.method == "POST":
        pass

    else:
        return render_template("index.html")

@app.route("/video", methods=["POST", "GET"])
def video_page():
    if request.method == "POST":
        link = request.form.get("link")
        userid = request.form.get("userid")
        pass_word = request.form.get("pass_word")
        total_records_required = request.form.get("total_records_required")
        
        html = videoBilgileriniGetir(link,userid,pass_word,total_records_required)
        
            
        return render_template("video.html")
    else:
        return redirect(url_for("home"))
    

@app.route("/get_csv")
def get_csv():
    return Response(
        df,
        mimetype="text/csv",
        headers={
                 "attachment; filename=myplot.csv"})

@app.errorhandler(500)
@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run()


