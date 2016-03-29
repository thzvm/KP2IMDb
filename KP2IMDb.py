# -*- coding: utf-8 -*-
import sys
import configparser
import pandas as pd
from time import sleep, strftime, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions as seleniumExceptions

__author__ = 'thzvme'

def import_to_imdb_with_methods(fn):
    """Ищем название фильма на страницы результатов поиска"""

    def search_and_rating_with_methods(self, title, year, rating):
        '''
        1 метод: Название (title) + Год (year)
        2 метод: Название (title)
        3 метод: Название на транслите + год
        4 метод: Название на транслите
        '''
        # Вводим в строку поиска (q) сформированнный в importratings() запрос (query)
        find = self.browser.find_element_by_name("q")
        find.send_keys(title)
        find.send_keys(Keys.RETURN)
        # Если результатов не найдено, прерываем цикл в importratings()
        # для получения следующего запроса или перехода к следующему фильму
        try:
            if "noResults" in self.browser.page_source:
                return False
            else:
                # Ищем на странице первый результат: "Название фильма (Год)"
                # Создаем из этой строки лист, с двумя элементами: Название и Год
                title = str(self.browser.find_element_by_xpath('//div[@class="title"]').text)
                title_year = title.split(' (')
                # Сравниваем полученный Год со страницы и Год из экспорта с КП
                # Иногда есть разница между сервисами у даты выхода фильма в один год
                years = (int(year) - 1, int(year), int(year) + 1)
                # Проверям совпадение в дате выхода фильма
                try:
                    if int(title_year[1][-5:-1]) not in years:
                        return False

                except ValueError:
                    return False
                # Если проверка на дату выхода фильма пройдена, отдаем фильм на оценку в import_to_imdb()
                else:
                    if fn(self, title, year, rating) is True:
                        return True
                    # TODO Нужно явно указать importratings(), что проблема в import_to_imdb()
                    else:
                        # TODO Фильм в лог как ненайденный
                        raise NameError(title)
        except seleniumExceptions.NoSuchElementException:
                 return False # иногда проскакивало при малой задержки

    return search_and_rating_with_methods

class IMDb2KP():
    '''  '''
    def __init__(self, config_file = 'config.ini'):

        config = configparser.ConfigParser()

        try:
            config.read(config_file)
            self.XLSFILE = config.get('SETTINGS', 'FILE')
            self.TIME_SLEEP = int(config.get('SETTINGS', 'TIME_SLEEP'))
            self.IMDb_mail = config.get('IMDb', 'IMDb_mail')
            self.IMDb_pass = config.get('IMDb', 'IMDb_pass')
            self.IMDb_auth = config.get('IMDb', 'IMDb_auth')
            self.IMDb_stat = False
            self.browser_path = sys.path[0] + config.get('BROWSER', 'PATH')
            self.rating_movies = 0
            self.LOGS = open(config.get('SETTINGS', 'LOGS'), 'a', encoding='utf-8')
            self.LOGS.write('START: ' + strftime('%d/%m/%Y %H:%M:%S') + '\n')

            if self.kinopoisk() == True:
                # PhantomJS
                #########################################################################
                self.browser = webdriver.PhantomJS(executable_path=self.browser_path)   #
                self.browser.set_page_load_timeout(config.get('SETTINGS', 'TIME_OUT'))  #
                self.browser.set_script_timeout(config.get('SETTINGS', 'TIME_OUT'))     #
                #########################################################################

                print('Authorization on IMDb')
                while self.authorization() != True:
                    print('Sign in to your IMDb account')

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
                      'У': 'U', 'у': 'u', 'Ф': 'F', 'ф': 'f', 'Х': 'H', 'х': 'h', 'Ц': 'Ts', 'ц': 'ts',
                      'Ч': 'Ch', 'ч': 'ch', 'Ш': 'Sh', 'ш': 'sh', 'Щ': 'Shh', 'щ': 'shh', 'Ъ': '', 'ъ': '',
                      'Ы': 'Y', 'ы': 'y', 'Ь': '', 'ь': '', 'Э': 'E', 'э': 'e', 'Ю': 'Yu', 'ю': 'yu',
                      'Я': 'Ya', 'я': 'ya'}

        Title = list(title)
        translateTitle = ''
        for i in range(len(Title)):
            try:
                translateTitle += dictionary[Title[i]]
            except KeyError:
                translateTitle += Title[i]
        return translateTitle

    def logs(self, title):
        print(title)
        #self.LOGS.write(str(title) + '\n')


    def kinopoisk(self):
        ''' Имортируем файл с оценками с помощью модуля pandas'''
        try:
            self.FILMS = [] # Лист для хранения фильмов по которому будем итерироваться в importratings()
            # Временный лист для экспорта из pandas.DataFrame to Dict
            films_table = pd.read_html(io=self.XLSFILE, encoding='windows-1251', header=0)[0].values.tolist()
            self.logs('Total films from Kinopoisk: ' + str(len(films_table)))
            # Итерация по каждому фильму во временном листе
            for film in films_table:
                # Если у фильма есть eng&ru_title и проставлена оценка, то делаем словарь и добавляем в Фильмы
                if str(film[1]) != 'nan' and str(film[7]) != '-':
                    temp_dict = {'lang': 'en', 'title': film[1], 'year': film[2][:4], 'rating': film[7]}
                    self.FILMS.append(temp_dict)

                elif str(film[1]) == 'nan' and str(film[7]) != '-':
                    temp_dict = {'lang': 'ru', 'title': film[0], 'year': film[2][:4], 'rating': film[7]}
                    self.FILMS.append(temp_dict)
                # Отсеиваем фильмы без оценок (просмотренные)
                else:
                    self.LOGS.write(strftime('%H:%M:%S ') + 'Film without rating: ' + str(film[0]) + '/'
                                    + str(film[1])+ '/you rating: ' + str(film[7]) + '\n')
            # TODO Счётчик фильмов для статистики
            self.FILMS_qty = len(self.FILMS)
            self.logs('Total films for IMDb import: ' + str(self.FILMS_qty))
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
            # TODO Капча
            self.browser.get_screenshot_as_file('IMDb_capcha.png')
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
        ''''''
        for film in self.FILMS:
            self.step = 0
            # Создаём запросы для поиска (4)
            self.querys = (film['title'] + ' ' + film['year'], film['title'], self.translatetitle(film['title'])
                           + ' ' + film['year'], self.translatetitle(film['title']))
            while True:
                try:
                    self.query = self.querys[self.step]
                    if self.import_to_imdb(year=film['year'], title=self.query, rating=int(film['rating'])) == True:
                        break
                    self.step += 1

                except IndexError:
                    with open('notrat.txt', 'a') as logs:
                        logs.write('---;' + film['rating'] + ' ' + film['title'] + ' ' + film['year'] + '\n')
                    break

                except NameError as e:
                    with open('notrat.txt', 'a') as logs:
                        logs.write('---;' + film['rating'] + ' ' + film['title'] + ' ' + film['year'] + '\n')
                    break

        self.LOGS.close()
        self.browser.close()

    @import_to_imdb_with_methods
    def import_to_imdb(self, title, year, rating):
        ''' '''
        print(self.rating_movies, '/', self.FILMS_qty, ':', title, year)

        if int(rating) == 1:
            rating = 2
        try:
            title = title.split(' (')
            result = self.browser.find_element_by_link_text(title[0])
            result.send_keys(Keys.ENTER)
            select = self.browser.find_element_by_name('rating')
            select.send_keys(rating)
            select.click()
            sleep(1)
            select.click()
            sleep(self.TIME_SLEEP)
            self.rating_movies += 1
            return True
        except:
            return False

if __name__ == '__main__':

    start = time()
    main = IMDb2KP()
    print('Process finished at ', round(float(format(time() - start)), 2))
