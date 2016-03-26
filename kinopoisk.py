import configparser
import pandas as pd
from time import sleep, strftime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def initialization(file = 'config.ini'):

    global XLSFILE, TXTLOGS, TIME_OUT, TIME_SLEEP, CSS, IMG, FLV, \
        IMDb_mail, IMDb_pass, IMDb_auth, IMDb_stat, browser, LOGS

    config = configparser.ConfigParser()

    try:
        config.read(file)

        XLSFILE     = config.get('SETTINGS', 'FILE')
        TXTLOGS     = config.get('SETTINGS', 'LOGS')
        TIME_OUT    = int(config.get('SETTINGS', 'TIME_OUT'))
        TIME_SLEEP  = int(config.get('SETTINGS', 'TIME_SLEEP'))
        CSS         = config.get('BROWSER', 'CSS')
        IMG         = config.get('BROWSER', 'IMG')
        FLV         = config.get('BROWSER', 'FLV')
        IMDb_mail   = config.get('IMDb', 'IMDb_mail')
        IMDb_pass   = config.get('IMDb', 'IMDb_pass')
        IMDb_auth   = config.get('IMDb', 'IMDb_auth')
        IMDb_stat   = False

        LOGS       = open(TXTLOGS, 'a')
        LOGS.write('START: ' + strftime('%d/%m/%Y %H:%M:%S') + '\n')

        #####################################################################################
        browserProfile = webdriver.FirefoxProfile()                                         #
        browserProfile.set_preference('permissions.default.stylesheet', 1)                  #
        browserProfile.set_preference('permissions.default.image', 2)                       #
        browserProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false') #
        browser = webdriver.Firefox(firefox_profile=browserProfile)                         #
        browser.set_window_size(350, 650)                                                   #
        browser.set_page_load_timeout(TIME_OUT)                                             #
        #####################################################################################

    except configparser.NoSectionError as e:
        print(file, 'error:', e)
    except configparser.NoOptionError as e:
        print(file, 'error:', e)

def translate(title):

    dict = {'А': 'A', 'а': 'a', 'Б': 'B', 'б': 'b', 'В': 'V',
                    'в': 'v', 'Г': 'G', 'г': 'g', 'Д': 'D', 'д': 'd',
                    'Е': 'E', 'е': 'e', 'Ё': 'Yo', 'ё': 'yo', 'Ж': 'Zh',
                    'ж': 'zh', 'З': 'Z', 'з': 'z', 'И': 'I', 'и': 'i',
                    'Й': 'J', 'й': 'j', 'К': 'K', 'к': 'k', 'Л': 'L',
                    'л': 'l', 'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n',
                    'О': 'O', 'о': 'o', 'П': 'P', 'п': 'p', 'Р': 'R',
                    'р': 'r', 'С': 'S', 'с': 's', 'Т': 'T', 'т': 't',
                    'У': 'U', 'у': 'u', 'Ф': 'F', 'ф': 'f', 'Х': 'H',
                    'х': 'h', 'Ц': 'C', 'ц': 'c', 'Ч': 'Ch', 'ч': 'ch',
                    'Ш': 'Sh', 'ш': 'sh', 'Щ': 'Shh', 'щ': 'shh', 'Ъ': "'",
                    'ъ': "'", 'Ы': 'Y', 'ы': 'y', 'Ь': '"', 'ь': '"',
                    'Э': 'E', 'э': 'e', 'Ю': 'Yu', 'ю': 'yu', 'Я': 'Ya',
                    'я': 'ya'}

    title = list(title)
    string = ''

    for i in range(len(title)):
        try:
            string += dict[title[i]]
        except KeyError:
            string += title[i]

    return string

def export_from_kp(file):

    films = []
    films_temp = pd.read_html(io=file, encoding='windows-1251', header=0)[0].values.tolist()

    LOGS.write('Total films export from Kinopoisk: ' + str(len(films_temp)) + '\n')

    for film in films_temp:

        if str(film[1]) != 'nan' and str(film[7]) != '-':
            temp_dict = {'lang' : 'en', 'title': film[1], 'year': film[2][:4], 'rating' : film[7]}
            #films.append(temp_dict)

        elif str(film[1]) == 'nan' and str(film[7]) != '-':
            temp_dict = {'lang' : 'ru', 'title': film[0], 'year': film[2][:4], 'rating': film[7]}
            films.append(temp_dict)
            print(temp_dict)

        else:
            LOGS.write(strftime('%H:%M:%S ') + 'Film without rating: ' + str(film[0]) + '/' + str(film[1])
                        + '/you rating: ' + str(film[7]) + 'from ' + XLSFILE + '\n')

    LOGS.write('Total films for import to IMDb: ' + str(len(films)) + '\n')
    return films

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

def import_to_imdb(data):
    browser.get('http://m.imdb.com')
    assert "IMDb" in browser.title

    def yearKPIMDb(KP, IMDb):
        title = str(IMDb.find_element_by_xpath('//div[@class="title"]').text)
        title = title.split(' (')
        if int(title[1][-5:-1]) == int(KP):
            return True
        else:
            return False

    for i in range(len(data)):
        try:
            if data[i]['lang'] == 'en':
                query = data[i]['title'] + ' ' + data[i]['year']
                find = browser.find_element_by_name("q")
                find.send_keys(query)
                find.send_keys(Keys.RETURN)

                if "No Results" in browser.page_source:
                    query = data[i]['title']
                    find = browser.find_element_by_name("q")
                    find.send_keys(query)
                    find.send_keys(Keys.RETURN)
                    if "No Results" in browser.page_source:
                        raise NameError
                    if yearKPIMDb(KP=data[i]['year'], IMDb=browser) == False:
                        raise NameError

                if yearKPIMDb(KP=data[i]['year'], IMDb=browser) == False:
                    raise NameError

            elif data[i]['lang'] == 'ru':
                query = data[i]['title']
                find = browser.find_element_by_name("q")
                find.send_keys(query)
                find.send_keys(Keys.RETURN)

                if "No Results" in browser.page_source:
                    query = translate(data[i]['title'])
                    find = browser.find_element_by_name("q")
                    find.send_keys(query)
                    find.send_keys(Keys.RETURN)
                    if "No Results" in browser.page_source:
                        raise NameError
                    if yearKPIMDb(KP=data[i]['year'], IMDb=browser) == False:
                        raise NameError

                if yearKPIMDb(KP=data[i]['year'], IMDb=browser) == False:
                    raise NameError

        except NameError:
            print(data[i]['lang'], data[i]['title'], data[i]['year'])
            '''try:
            title = str(browser.find_element_by_xpath('//div[@class="title"]').text)
            #print(title)
            #title = title.split(' (')
            #print(int(title[1][-5:-1]))
            #print(int(data[i]['year']))
            #if int(title[1][-5:-1]) == int(data[i]['year']):
            #    print('True')
            #else:
            #    print('False')
            #print(query)
            #print(title)
            #print('________________')
            #result = browser.find_element_by_link_text(title[0])
            #result.send_keys(Keys.ENTER)
            assert "No results found." not in browser.page_source
            #select = browser.find_element_by_name('rating')
            #select.send_keys(int(data[i]['rating']))
            #select.click()
            #sleep(2)
            #select.click()
            #sleep(0)
            #sleep(TIME_SLEEP)
        except Exception as e:
            print('FAIL:', query)
            sleep(TIME_SLEEP)'''

if __name__ == '__main__':

    try:
        initialization()
        #while IMDb_stat != True:
        #    IMDb_stat = authorization(page=IMDb_auth, mail=IMDb_mail, password=IMDb_pass)
        import_to_imdb(data=export_from_kp(file=XLSFILE))
        export_from_kp(file=XLSFILE)
        LOGS.write('END: ' + strftime('%d/%m/%Y %H:%M:%S') + '\n')
        LOGS.close()

    except Exception as e:
        print(e)
        LOGS.write(str(e) + '\n')
        LOGS.write('END: ' + strftime('%d/%m/%Y %H:%M:%S') + '\n')
        LOGS.close()

