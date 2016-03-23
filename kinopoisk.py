from time import sleep

filename = 'kinopoisk.csv'
time_sleep = 1

data = []
with open(filename, 'r') as csvfile:
    for line in csvfile:

        data_line = line.replace('\n', '').split(';')

        if len(data_line[1]) == 0:
            data_line[1] = data_line[0]
            temp_dict = {'ru' : data_line[0], 'en' : data_line[1], 'year' : data_line[2][:4],
                         'rating' : data_line[3]}
            data.append(temp_dict)
        else:
            temp_dict = {'ru': data_line[0], 'en': data_line[1], 'year': data_line[2][:4],
                         'rating': data_line[3]}
            #data.append(temp_dict)

print(len(data))

for i in range(len(data)):
    print(data[i])

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()

auth = 'https://secure.imdb.com/oauth/m_login'
#auth

driver.get(auth)
auth_done = None

while auth_done != True:
    try:
        mail = 'thzvme@gmail.com'#input('MAIL:')
        mail_form = driver.find_element_by_id("email")
        mail_form.send_keys(mail)

        password = 'Test123Test'#input('PASS:')
        pass_form = driver.find_element_by_id("password")
        pass_form.send_keys(password)

        captcha = input('CAPTCHA:')
        captcha_form = driver.find_element_by_name('captcha_answer')
        captcha_form.send_keys(captcha)

        login = driver.find_element_by_id('submit')
        login.send_keys(Keys.ENTER)

        assert "IMDb" in driver.title
        auth_done = True

    except:
        auth_done = False

for i in range(len(data)):
    driver.get('http://m.imdb.com')
    assert "IMDb" in driver.title
    query = data[i]['en']
    find = driver.find_element_by_name("q")
    find.send_keys(query)
    find.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source
    try:
        title = str(driver.find_element_by_xpath('//div[@class="title"]').text)
        title = title.split(' (')
        result = driver.find_element_by_link_text(title[0])
        result.send_keys(Keys.ENTER)
        assert "No results found." not in driver.page_source
        select = driver.find_element_by_name('rating')
        select.send_keys(int(data[i]['rating']))
        select.click()
        sleep(2)
        select.click()
        sleep(0)
        sleep(time_sleep)
    except Exception as e:
        print('FAIL:', query)
        sleep(time_sleep)
