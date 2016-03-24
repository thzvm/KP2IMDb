from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

mail =  'thzvme@gmail.com'
password = 'Test123Test'
auth_page = 'https://secure.imdb.com/oauth/m_login'
auth_status = None


filename = '1.csv'
time_sleep = 1

data = []
with open(filename, 'r') as csvfile:

    for line in csvfile:

        data_line = line.replace('\n', '').split(',')
        print(data_line[1])

        if len(data_line[1]) == 0:
            data_line[1] = data_line[0]
            temp_dict = {'ru' : data_line[0], 'en' : data_line[1], 'year' : data_line[2][:4],
                         'rating' : data_line[3]}
            data.append(temp_dict)
        else:
            temp_dict = {'ru': data_line[0], 'en': data_line[1], 'year': data_line[2][:4],
                         'rating': data_line[3]}
            #data.append(temp_dict)


browserProfile = webdriver.FirefoxProfile()
browserProfile.set_preference('permissions.default.stylesheet', 1)
browserProfile.set_preference('permissions.default.image', 2)
browserProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
browser = webdriver.Firefox(firefox_profile=browserProfile)
browser.set_window_size(400, 600)

def authorization(page , mail, password):

        browser.get(page)

        try:
            mail_form = browser.find_element_by_id("email")
            mail_form.send_keys(mail)

            pass_form = browser.find_element_by_id("password")
            pass_form.send_keys(password)

            captcha = input('CAPTCHA:')
            captcha_form = browser.find_element_by_name('captcha_answer')
            captcha_form.send_keys(captcha)

            login = browser.find_element_by_id('submit')
            login.send_keys(Keys.ENTER)

            assert "IMDb" in browser.title
            return True
        except:
            return False

def ratingtoimdb():
     
if __name__ == '__main__':

    while auth_status != True:
        auth_status = authorization(page=auth_page, mail=mail, password=password)

    for i in range(len(data)):
        browser.get('http://m.imdb.com')
        assert "IMDb" in browser.title
        query = data[i]['en']
        find = browser.find_element_by_name("q")
        find.send_keys(query)
        find.send_keys(Keys.RETURN)
        assert "No results found." not in browser.page_source
        try:
            title = str(browser.find_element_by_xpath('//div[@class="title"]').text)
            title = title.split(' (')
            result = browser.find_element_by_link_text(title[0])
            result.send_keys(Keys.ENTER)
            assert "No results found." not in browser.page_source
            select = browser.find_element_by_name('rating')
            select.send_keys(int(data[i]['rating']))
            select.click()
            sleep(2)
            select.click()
            sleep(0)
            sleep(time_sleep)
        except Exception as e:
            print('FAIL:', query)
            sleep(time_sleep)
