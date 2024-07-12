# https://github.com/joeyism/linkedin_scraper.git

from linkedin_scraper import Person, actions
from selenium import webdriver

import json


driver = webdriver.Chrome()
driver.implicitly_wait(60)

login = json.loads(open("login.json").read())
actions.login(
    driver, login["email"], login["password"]
)  # if email and password isnt given, it'll prompt in terminal
person = Person("https://www.linkedin.com/in/ruiyangji/", driver=driver)

print(person, dir(person))


data = {
    "linkedin_url": person.linkedin_url,
    "name": person.name,
    "about": person.about,
    "experiences": person.experiences,
    "education": person.education,
    "interests": person.interests,
    "accomplishment": person.accomplishment,
    "company": person.company,
    "job_title": person.job_title,
}

print("Data: ", data)

driver.close()
