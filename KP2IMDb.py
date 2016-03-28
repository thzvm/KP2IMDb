# -*- coding: utf-8 -*-
import configparser
import pandas as pd
from time import sleep, strftime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions as sEx

def import_to_imdb_with_methods(fn):
    """ДЕКОРАТОР: Ищем название фильма на страницы результатов поиска"""

    def search_and_rating_with_methods(self, title, year, rating):
        '''
        1 метод: Название (title) + Год (year)
        2 метод: Название (title)
        3 метод: Название на транслите для русскоязычных фильмов translatetitle(title)
        '''
        # Вводим в строку поиска (q) сформированнный в _importratings() запрос (query)
        find = self.browser.find_element_by_name("q")
        find.send_keys(title)
        find.send_keys(Keys.RETURN)
        # Если результатов не найдено, прерываем цикл в _importratings()
        # для получения следующего запроса или перехода к следующему фильму
        try:
            if "noResults" in self.browser.page_source:
                return False
            else:
                # TODO А вот тут пиздец, так как скорее всего, берется только первый резлуьтат
                # Ищем на странице резултат строкой "Название фильма (Год)"
                # Создаем из этой строки лист, с двумя элементами: Название и Год
                title = str(self.browser.find_element_by_xpath('//div[@class="title"]').text)
                title_year = title.split(' (')
                # Сравниваем полученный Год со страницы и Год из экспорта с КП
                # TODO Иногда есть разница между сервисами у даты выхода фильма в один год
                try:
                    if int(title_year[1][-5:-1]) != int(year):
                        return False
                except ValueError: return False
                # Если проверка на дату выхода фильма пройдена, отдаем фильм на оценку в import_to_imdb()
                else:
                    if fn(self, title, year, rating) is True:
                        return True
                    # TODO Нужно явно указать _importratings(), что проблема в import_to_imdb()
                    else:
                        # TODO Фильм в лог как ненайденный
                        raise NameError(title)
        except sEx.NoSuchElementException as e:
            with open('webError.txt', 'a') as logs:
                logs.write('<<<START REPORT>>> ' + strftime('%d/%m/%Y %H:%M:%S') + '\n')
                logs.write(e)
                logs.write('\n')
                logs.write('\n')
                logs.write(self.browser.page_source + '\n')
                logs.write('<<<END REPORT>>> ' + strftime('%d/%m/%Y %H:%M:%S') + '\n')
                logs.close()
                return False

    return search_and_rating_with_methods

class IMDb2KP():
    '''  '''
    def __init__(self, config_file = 'config.ini'):

        config = configparser.ConfigParser()

        try:
            config.read(config_file)
            TXTLOGS = config.get('SETTINGS', 'LOGS')
            TIME_OUT = int(config.get('SETTINGS', 'TIME_OUT'))
            self.XLSFILE = config.get('SETTINGS', 'FILE')
            self.TIME_SLEEP = int(config.get('SETTINGS', 'TIME_SLEEP'))
            self.CSS = config.get('BROWSER', 'CSS')
            self.IMG = config.get('BROWSER', 'IMG')
            self.FLV = config.get('BROWSER', 'FLV')
            self.IMDb_mail = config.get('IMDb', 'IMDb_mail')
            self.IMDb_pass = config.get('IMDb', 'IMDb_pass')
            self.IMDb_auth = config.get('IMDb', 'IMDb_auth')
            self.IMDb_stat = False

            self.LOGS = open(TXTLOGS, 'a', encoding='utf-8')
            self.LOGS.write('START: ' + strftime('%d/%m/%Y %H:%M:%S') + '\n')

            if self.kinopoisk() == True:
                # TODO webdriver.PhantomJS
                #####################################################################################
                browserProfile = webdriver.FirefoxProfile()                                         #
                browserProfile.set_preference('permissions.default.stylesheet', 1)                  #
                browserProfile.set_preference('permissions.default.image', 2)                       #
                browserProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false') #
                self.browser = webdriver.Firefox(firefox_profile=browserProfile)
                self.browser.set_window_size(350, 650)                                              #
                self.browser.set_page_load_timeout(TIME_OUT)                                        #
                #####################################################################################
                print('Authorization on IMDb')

                #while self.authorization() != True:
                #    print('Sign in to your IMDb account')
                #else:
                self.browser.get('https://m.imdb.com')
                self.importratings()

        except configparser.NoSectionError as e:
            print(config_file, 'error:', e)
        except configparser.NoOptionError as e:
            print(config_file, 'error:', e)

    @staticmethod
    def translatetitle(title):
        """Транслитерация русского алфавита латиницей ISO 9:1995b"""

        dictionary = {'А': 'A', 'а': 'a', 'Б': 'B', 'б': 'b', 'В': 'V', 'в': 'v', 'Г': 'G', 'г': 'g',
                      'Д': 'D', 'д': 'd', 'Е': 'E', 'е': 'e', 'Ё': 'Yo', 'ё': 'yo', 'Ж': 'Zh', 'ж': 'zh',
                      'З': 'Z', 'з': 'z', 'И': 'I', 'и': 'i', 'Й': 'J', 'й': 'j', 'К': 'K', 'к': 'k',
                      'Л': 'L', 'л': 'l', 'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n', 'О': 'O', 'о': 'o',
                      'П': 'P', 'п': 'p', 'Р': 'R', 'р': 'r', 'С': 'S', 'с': 's', 'Т': 'T', 'т': 't',
                      'У': 'U', 'у': 'u', 'Ф': 'F', 'ф': 'f', 'Х': 'H', 'х': 'h', 'Ц': 'Cz', 'ц': 'cz',
                      'Ч': 'Ch', 'ч': 'ch', 'Ш': 'Sh', 'ш': 'sh', 'Щ': 'Shh', 'щ': 'shh', 'Ъ': '', 'ъ': '',
                      'Ы': 'Y', 'ы': 'y', 'Ь': '', 'ь': '', 'Э': 'E', 'э': 'e', 'Ю': 'Yu', 'ю': 'yu',
                      'Я': 'Ya', 'я': 'ya'}

        title = list(title)
        translateTitle = ''
        for i in range(len(title)):
            try:
                translateTitle += dictionary[title[i]]
            except KeyError:
                translateTitle += title[i]
        return translateTitle

    def writelogs(self, title):

        print(title)
        self.LOGS.write(str(title) + '\n')


    def kinopoisk(self):
        ''' Имортируем файл с оценками с помощью модуля pandas'''
        try:
            self.FILMS = [] # Лист для хранения фильмов по которому будем итерироваться в _importratings()
            # Временный лист для экспорта из pandas.DataFrame to Dict
            films_table = pd.read_html(io=self.XLSFILE, encoding='windows-1251', header=0)[0].values.tolist()
            self.writelogs('Total films from Kinopoisk: ' + str(len(films_table)))
            # Итерация по каждому фильму во временном листе
            for film in films_table:
                # Если у фильма есть eng&ru_title и проставлена оценка, то делаем словарь и добавляем в Фильмы
                if str(film[1]) != 'nan' and str(film[7]) != '-':
                    temp_dict = {'lang': 'en', 'title': film[1], 'year': film[2][:4], 'rating': film[7]}
                    #elf.FILMS.append(temp_dict)

                elif str(film[1]) == 'nan' and str(film[7]) != '-':
                    temp_dict = {'lang': 'ru', 'title': film[0], 'year': film[2][:4], 'rating': film[7]}
                    self.FILMS.append(temp_dict)
                # Отсеиваем фильмы без оценок (просмотренные)
                else:
                    self.LOGS.write(strftime('%H:%M:%S ') + 'Film without rating: ' + str(film[0]) + '/'
                                    + str(film[1])+ '/you rating: ' + str(film[7]) + '\n')
            # TODO Счётчик фильмов для статистики
            self.FILMS_qty = len(self.FILMS)
            self.writelogs('Total films for IMDb import: ' + str(self.FILMS_qty))
            return True
        except Exception as e:
            print(e)
            return False

    def authorization(self):
        '''Авторизация на сайте'''
        self.browser.get(self.IMDb_auth)

        try:
            # Заполняем поля данными из config.ini и вводим капчу
            mail_form = self.browser.find_element_by_id("email")
            mail_form.send_keys(self.IMDb_mail)
            pass_form = self.browser.find_element_by_id("password")
            pass_form.send_keys(self.IMDb_pass)
            captcha = input('Enter the name of the movie or person above:')
            captcha_form = self.browser.find_element_by_name('captcha_answer')
            captcha_form.send_keys(captcha)
            login = self.browser.find_element_by_id('submit')
            login.send_keys(Keys.ENTER)
            # TODO Login error (response)
            assert "IMDb" in self.browser.title
            return True
        except:
            return False

    def importratings(self):

        #for i in range(5):
        for film in self.FILMS:
            #film = self.FILMS[i]
            # отдаём query для q
            self.querys = (film['title'] + ' ' + film['year'], film['title'], self.translatetitle(film['title']))
            #self.rating = film['rating']
            #self.year = film['year']
            self.step = 0

            while True:
                try:
                    self.query = self.querys[self.step]
                    if self.import_to_imdb(year=film['year'], title=self.query, rating=int(film['rating'])) == True:
                        break
                    self.step += 1
                except IndexError:
                    print('--RAT!', int(film['rating']), self.query, film['year'])
                    break
                except NameError as e:
                    print('--RAT!', int(film['rating']), self.query, film['year'])
                    break


        self.LOGS.close()
        self.browser.close()

    @import_to_imdb_with_methods
    def import_to_imdb(self, title, year, rating):
        print('++RAT!', rating, title, year)
        sleep(self.TIME_SLEEP)
        return True
        #try:
        #    select = self.browser.find_element_by_name('rating')
        #    select.send_keys(int(self.rating))
        #    select.click()
        #    sleep(2)
        #    select.click()
        #    sleep(0)
        #    sleep(self.TIME_SLEEP)
        #    print('Ставим оценку')
        #    return True
        #except:
        #    print('Я чото хз как ставить, тут же ничего нету, ААА-ААААА-АААААА!')
        #    return False

if __name__ == '__main__':
    main = IMDb2KP()
