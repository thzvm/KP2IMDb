from time import sleep, strftime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

IMDb_mail = 'thzvme@gmail.com'
IMDb_pass = 'Test123Test'
IMDb_auth = 'https://secure.imdb.com/oauth/m_login'

#####################################################################################
browserProfile = webdriver.FirefoxProfile()  #
browserProfile.set_preference('permissions.default.stylesheet', 1)  #
browserProfile.set_preference('permissions.default.image', 2)  #
browserProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')  #
browser = webdriver.Firefox(firefox_profile=browserProfile)  #
browser.set_window_size(350, 650)  #
browser.set_page_load_timeout(10)  #
#####################################################################################

def authorization(page , mail, password):

        browser.get(page)

        try:
            mail_form = browser.find_element_by_id('email')
            mail_form.send_keys(mail)

            pass_form = browser.find_element_by_id('password')
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

def import_to_imdb(data):
    browser.get('http://m.imdb.com')
    assert "IMDb" in browser.title

    for i in range(len(data)):
        query = data[i]['title'] + ' ' + data[i]['year']
        find = browser.find_element_by_name('q')
        find.send_keys(query)
        find.send_keys(Keys.RETURN)
        assert 'No results found.' not in browser.page_source
        try:
            title = str(browser.find_element_by_xpath('//div[@class="title"]').text)
            print(title)
            title = title.split(' (')
            print(int(title[1][-5:-1]))
            print(int(data[i]['year']))
            if int(title[1][-5:-1]) == int(data[i]['year']):
                print('True')
            else:
                print('False')
            print(query)
            print(title)
            print('________________')
            result = browser.find_element_by_link_text(title[0])
            result.send_keys(Keys.ENTER)
            assert 'No results found.' not in browser.page_source
            #select = browser.find_element_by_name('rating')
            #select.send_keys(int(data[i]['rating']))
            #select.click()
            #sleep(2)
            #select.click()
            #sleep(0)
            #sleep(2)
        except Exception as e:
            print('FAIL:', query)
            sleep(2)

if __name__ == '__main__':

    data = ({'year': '2002', 'title': 'Gangs of New York', 'rating': '7'},
            {'year': '1971', 'title': '12 стульев', 'rating': '8'},
            {'year': '2011', 'title': 'Sherlock Holmes: A Game of Shadows', 'rating': '8'},
            {'year': '1997', 'title': 'Намедни. Наша эра. 1961-2003', 'rating': '10'},
            {'year': '1995', 'title': 'La haine', 'rating': '9'},
            {'year': '2012', 'title': 'This Means War', 'rating': '4'},
            {'year': '2010', 'title': "The King's Speech", 'rating': '8'},
            {'year': '1982', 'title': 'Gandhi', 'rating': '10'},
            {'year': '1964', 'title': "A Hard Day's Night", 'rating': '9'},
            {'year': '2011', 'title': 'Бабло', 'rating': '3'},
            {'year': '1989', 'title': 'Dead Poets Society', 'rating': '8'})

    IMDb_stat = False
    #while IMDb_stat != True:
    #    IMDb_stat = authorization(page=IMDb_auth, mail=IMDb_mail, password=IMDb_pass)
    import_to_imdb(data=data)
