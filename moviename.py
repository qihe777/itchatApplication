# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class spider:
    def __init__(self):
        self.browser = webdriver.Chrome(executable_path='data\chromedriver.exe')
        # 设置等待时间为10s，超时则会报错
        self.wait = WebDriverWait(self.browser, 10)
        self.browser.get('https://movie.douban.com/')

    def search(self, word):
        # 等待输入框加载完毕
        input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#inp-query'))
        )
        # 等待【搜索】按钮标签加载完毕
        submit = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        '#db-nav-movie > div.nav-wrap > div >     div.nav-search > form > fieldset > div.inp-btn > input[type="submit"]'))
        )
        print('输入搜索的内容【{}】'.format(word))
        input.clear()
        # 输入搜索内容
        input.send_keys('{}'.format(word))
        # 点击确认
        submit.click()
        # 第一个标签为sc-bZQynM
        active = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"sc-bZQynM")]/div/div/div/a'))
        )
        return active.text, active.get_attribute('href')


if __name__ == '__main__':
    mysprider = spider()
    mysprider.search('Inception')
    mysprider.search('Avatar‎')
