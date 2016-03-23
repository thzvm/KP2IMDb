from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains as AC
from time import sleep


url = 'http://m.imdb.com'
name = 'The Idiots'
year = '1998'
query = 'Кавказская пленница, или Новые приключения Шурика'
auth = 'https://secure.imdb.com/oauth/m_login'
driver = webdriver.Firefox()


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

#driver.get(url)


find = driver.find_element_by_name("q")
find.send_keys(query)
find.send_keys(Keys.RETURN)

title = driver.find_element_by_xpath('//div[@class="title"]')
print(title.text)
result = driver.find_element_by_link_text('Kidnapping, Caucasian Style')
result.send_keys(Keys.ENTER)

assert "No results found." not in driver.page_source

select = driver.find_element_by_name('rating')
select.send_keys(5)
#action = AC(driver)
#action.context_click(select)
select.click()
sleep(2)
select.click()
sleep(6)
driver.refresh()


input('')
driver.quit()