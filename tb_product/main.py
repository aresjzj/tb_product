# coding=gbk

# 获取指定页面的商品图片并保存
import time
from datetime import datetime as dt
from urllib import parse
from urllib import request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import logging
import sys

# 获取logger实例，如果参数为空则返回root logger
logger = logging.getLogger("sync-taobao")
# 指定logger输出格式
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

# 控制台日志
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter  # 也可以直接给formatter赋值

# 为logger添加的日志处理器
logger.addHandler(console_handler)

# 指定日志的最低输出级别，默认为WARN级别
logger.setLevel(logging.DEBUG)
def getHeadersOptions():
    options = webdriver.ChromeOptions()
    # 谷歌无头模式
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')
    # 设置中文
    options.add_argument('lang=zh_CN.UTF-8')
    with open('headers.conf') as file_object:
        for line in file_object:
            arr = str(line).split(':')
            header = arr[0] + '="' + arr[1].strip() + '"'
            options.add_argument(header)
            #log(header)
    return options

def getChromeBrowser(chromeOptions):
    browser = webdriver.Chrome(executable_path='./chromedriver.exe', chrome_options=chromeOptions)
    return browser

def log(msg):
    # 输出不同级别的log
    logger.debug(msg)

def getProductInfo(url, browser):
    # 打开商品页面
    browser.get(url)

    title = browser.find_element_by_xpath('//*[@id="mod-detail-title"]/h1').text
    # 判断是否存在下载目录，如果不存在，创建
    if not os.path.exists('images'):
        os.mkdir('images')
    if not os.path.exists('images/'+title):
        os.mkdir('images/' + title)
    if not os.path.exists('images/' + title + '/title'):
        os.mkdir('images/' + title + '/title')

    # 获取抬头的图片
    getProductTitleImgs(url, browser, title)

    # 获取明细中的图片
    getProductDetailImgs(url, browser, title)

def getProductTitleImgs(url, browser, title):
    titleImgUrl = url.replace('offer', 'pic')
    log(titleImgUrl)
    browser.get(titleImgUrl)

    try:
        element = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, "dt-bp-tabnavnext"))
        )
        tryNum = 0
        while tryNum < 5:
            browser.execute_script("document.getElementById('dt-bp-tabnavnext').click()")
            time.sleep(1)
            tryNum = tryNum + 1
    except:
        log('需要登陆验证，无法打开抬头')
        return

    urltmp = '//*[@id="dt-bp-tab-nav"]/div/ul/li'
    imagea = browser.find_elements_by_xpath(urltmp)
    index = 0
    while index <= imagea.__len__():
        urltmp = '//*[@id="dt-bp-tab-nav"]/div/ul/li['+str(index)+']/div/a/img'
        images = browser.find_elements_by_xpath(urltmp)
        for image in images:
            imgUrl = str(image.get_attribute("src")).replace('64x64.', '').replace('_.webp', '')
            log(str(index) + ':' + imgUrl)
            request.urlretrieve(imgUrl, './images/' + title + '/title/' + str(index) + '.jpg')
        index = index + 1

def getProductDetailImgs(url, browser, title):
    log(url)
    browser.get(url)
    time.sleep(3)

    # 将页面滚动条拖到底部
    tryNum = 0
    while tryNum < 5:
        try:
            element = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located((By.ID, "sufei-dialog-close"))
            )
            browser.execute_script("document.getElementById('sufei-dialog-close').click()")
        except:
            log('没有验证窗口')

        js = "var q=document.documentElement.scrollTop=" + str(10000 + tryNum * 5000)
        browser.execute_script(js)
        tryNum = tryNum + 1
        time.sleep(1)

    urltmp = '//*[@id="desc-lazyload-container"]/p'
    imageP = browser.find_elements_by_xpath(urltmp)
    index = 0
    while index < imageP.__len__():
        urltmp = '//*[@id="desc-lazyload-container"]/p[' + str(index) + ']/span/strong/span/img'
        images = browser.find_elements_by_xpath(urltmp)
        if images.__len__() == 0:
            urltmp = '//*[@id="desc-lazyload-container"]/p[' + str(index) + ']/span/strong/img'
            images = browser.find_elements_by_xpath(urltmp)
        if images.__len__() == 0:
            urltmp = '//*[@id="desc-lazyload-container"]/p[' + str(index) + ']/span/img'
            images = browser.find_elements_by_xpath(urltmp)
        if images.__len__() == 0:
            urltmp = '//*[@id="desc-lazyload-container"]/p[' + str(index) + ']/strong/span/img'
            images = browser.find_elements_by_xpath(urltmp)
        if images.__len__() == 0:
            urltmp = '//*[@id="desc-lazyload-container"]/p[' + str(index) + ']/span/strong/img'
            images = browser.find_elements_by_xpath(urltmp)
        imageIndex = 1
        for image in images:
            log(str(imageIndex) + ':' + image.get_attribute("src"))
            request.urlretrieve(image.get_attribute("src"), './images/' + title + '/' + str(imageIndex) + '.jpg')
            imageIndex = imageIndex + 1
        index = index + 1

def readConfig():
    filename = 'url.txt'
    urls = []
    with open(filename, 'r') as file_to_read:
        while True:
            line = file_to_read.readline()  # 整行读取数据
            if not line:
                break
                pass
            urls.append(line)
    return urls

if __name__ == '__main__':
    log("/_/_/_/_/_/_/_/_/_/_任务开始/_/_/_/_/_/_/_/_/_")
    headerOptions = getHeadersOptions()
    browser = getChromeBrowser(headerOptions)
    try:
        urls = readConfig()
        for url in urls:
            getProductInfo(url, browser)

    except KeyboardInterrupt:
        log("任务被取消")
    log("/_/_/_/_/_/_/_/_/_/_任务结束/_/_/_/_/_/_/_/_/_")

    browser.quit()