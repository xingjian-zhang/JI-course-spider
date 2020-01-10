# coding: utf-8
'''
@author: JIM
@file: ji-course-web.py
@time: 2020/1/10
'''

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from data import chromedriver_path
from json import loads
from time import sleep
from bs4 import BeautifulSoup
import data
from ocr import ocr_space_file
import pandas as pd

WAIT_TIME = 5
UPDATE_PERIOD = 20


def init_chrome(headless=True):
    chrome_options = Options()
    # Open the browser silently (i.e. without GUI).
    if headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

    # Instantiate webdriver.
    driver_ = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)

    # Request JI course selection website.
    driver_.get(data.select_course_url)
    return driver_


def get_captcha(driver_):
    """
    Find and save the captcha picture.
    """
    captcha_element = driver_.find_element_by_xpath(data.x_path['captcha'])
    captcha_element.screenshot('captcha.png')


def read_captcha():
    """
    Use a free api provided by @ocr.space to recognize the captcha.
    """

    #  Upload the captcha picture to be identified.
    result = ocr_space_file('captcha.png')

    #  Use json.loads to load the result and retrieve the parsed text.
    result = loads(result)
    parsed_text = result['ParsedResults'][0]['ParsedText']

    #  Keep the letters and delete all other chars.
    parsed_text = parsed_text.strip()
    parsed_text = parsed_text.replace(' ', '').replace('\n', '').replace('\r', '')
    print('Try to recognize the captcha: ' + parsed_text)
    return parsed_text


def select_turn(driver_):
    """
    Use selenium to request the course-selection interface.
    """

    #  Click the button '2020 Spring Undergraduate Course Registration (Round 3)'
    driver_.implicitly_wait(WAIT_TIME)
    turn = driver_.find_element_by_xpath(data.x_path['turn'])
    turn.click()

    # Click the button 'Preview'
    driver_.implicitly_wait(WAIT_TIME)
    preview = driver_.find_element_by_xpath(data.x_path['preview'])
    preview.click()
    driver_.implicitly_wait(WAIT_TIME)


def read_html(driver_):
    """
    Use bs & lxml to parse the html
    """

    sleep(WAIT_TIME)
    main_page = driver_.page_source
    soup = BeautifulSoup(main_page, 'lxml')
    return soup


def fuck_captcha(driver_, captcha_):
    """
    Try to login.
    """
    #  Prepare four elements to be sent keys or clicked.
    user_name_input = driver_.find_element_by_xpath(data.x_path['username_input'])
    pass_word_input = driver_.find_element_by_xpath(data.x_path['password_input'])
    captcha_input = driver_.find_element_by_xpath(data.x_path['captcha_input'])
    login = driver_.find_element_by_xpath(data.x_path['login'])

    # Input username, password and captcha
    user_name_input.send_keys(data.user_name)
    pass_word_input.send_keys(data.pass_word)
    captcha_input.send_keys(captcha_)
    login.click()

    # Detect whether new elements raise
    try:
        driver_.implicitly_wait(WAIT_TIME)
        test_target = driver_.find_element_by_xpath(data.x_path['turn'])
        return True
    except NoSuchElementException:
        print('Fail.')
        return False


def parse_html(html):
    """
    Parse the html and save the data into a list of dicts.
    """

    courses = []
    for course_html in html.find_all('div', attrs={'class': 'row lesson-task'}):
        course_info = {}

        course_code = course_html.find('div', attrs={'class': 'lesson-task-code-circle pull-left'}).getText()
        course_info['code'] = course_code

        course_name_en = course_html.find('a', attrs={'class': 'lesson-task-name'}).getText()
        course_info['name_en'] = course_name_en

        course_name_cn = course_html.find('p').getText()
        course_info['name_cn'] = course_name_cn

        course_teacher = course_html.find('span', attrs={'class': 'firstSpeaker'}).getText()
        course_info['teacher'] = course_teacher

        course_slots = course_html.find('div', attrs={'class': 'progress-bar progress-bar-success'})
        if course_slots is not None:
            course_info['slots'] = course_slots.getText()
        else:
            course_info['slots'] = 'Full'

        courses.append(course_info)

    return courses


def refresh(driver_):
    """
    Refresh the data.
    """
    refresh_button = driver_.find_element_by_xpath(data.x_path['refresh'])
    driver_.implicitly_wait(WAIT_TIME)
    refresh_button.click()


if __name__ == '__main__':

    driver = init_chrome(headless=True)

    #  Repeatedly try to login until succeed.
    success = False
    while not success:
        get_captcha(driver)
        captcha = read_captcha()
        success = fuck_captcha(driver, captcha)

    print('Successfully Login!')
    select_turn(driver)

    #  Repeatedly update the data (once for UPDATE_PERIOD)
    shutdown = False
    while not shutdown:
        content = read_html(driver)
        course_list = parse_html(content)
        course_table = pd.DataFrame(course_list)
        course_table.to_csv('courses.csv', encoding='utf-8-sig')
        print(course_table)
        driver.implicitly_wait(WAIT_TIME)
        sleep(UPDATE_PERIOD)
        refresh(driver)

    driver.close()
