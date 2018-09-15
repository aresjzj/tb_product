# coding=gbk

# ��ȡָ��ҳ�����ƷͼƬ������
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

# ��ȡloggerʵ�����������Ϊ���򷵻�root logger
logger = logging.getLogger("sync-taobao")
# ָ��logger�����ʽ
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

# ����̨��־
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter  # Ҳ����ֱ�Ӹ�formatter��ֵ

# Ϊlogger��ӵ���־������
logger.addHandler(console_handler)

# ָ����־������������Ĭ��ΪWARN����
logger.setLevel(logging.DEBUG)
def getHeadersOptions():
    options = webdriver.ChromeOptions()
    # �ȸ���ͷģʽ
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')
    # ��������
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
    # �����ͬ�����log
    logger.debug(msg)

def getProductInfo(url, browser):
    # ����Ʒҳ��
    browser.get(url)

    title = browser.find_element_by_xpath('//*[@id="mod-detail-title"]/h1').text
    # �ж��Ƿ��������Ŀ¼����������ڣ�����
    if not os.path.exists('images'):
        os.mkdir('images')
    if not os.path.exists('images/'+title):
        os.mkdir('images/' + title)
    if not os.path.exists('images/' + title + '/title'):
        os.mkdir('images/' + title + '/title')

    # ��ȡ̧ͷ��ͼƬ
    getProductTitleImgs(url, browser, title)

    # ��ȡ��ϸ�е�ͼƬ
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
        log('��Ҫ��½��֤���޷���̧ͷ')
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

    # ��ҳ��������ϵ��ײ�
    tryNum = 0
    while tryNum < 5:
        try:
            element = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located((By.ID, "sufei-dialog-close"))
            )
            browser.execute_script("document.getElementById('sufei-dialog-close').click()")
        except:
            log('û����֤����')

        js = "var q=document.documentElement.scrollTop=" + str(10000 + tryNum * 5000)
        browser.execute_script(js)
        tryNum = tryNum + 1
        time.sleep(1)

    urltmp = '//*[@id="desc-lazyload-container"]//img'
    images = browser.find_elements_by_xpath(urltmp)
    imageIndex = 1
    for image in images:
        imageUrl = image.get_attribute("src")
        file = os.path.splitext(imageUrl)
        filename, type = file
        log(str(imageIndex) + ':' + imageUrl)
        if type == '.jpg':
            request.urlretrieve(imageUrl, './images/' + title + '/' + str(imageIndex) + type)
            imageIndex = imageIndex + 1

def readConfig(filename):
    urls = []
    with open(filename, 'r') as file_to_read:
        while True:
            line = file_to_read.readline()  # ���ж�ȡ����
            if not line:
                break
                pass
            urls.append(line)
    return urls

productList = []

# ��ȡ"���в�Ʒ"���棬�����еĲ�Ʒ��ϸ�б�д��url.txt
def writeUrlConfig(urlOfferList, browser):
    log(urlOfferList)
    browser.get(urlOfferList)

    urltmp = "//*[@id='search-bar']/div[2]/div/div/div/ul/li"
    imageCount = browser.find_elements_by_xpath(urltmp).__len__()
    imageIndex = 0
    while imageIndex < imageCount:
        urltmp = "//*[@id='search-bar']/div[2]/div/div/div/ul/li[" + str(imageIndex) + "]/div[1]/a"
        imageUrls = browser.find_elements_by_xpath(urltmp)
        for productUrl in imageUrls:
            productList.append(productUrl.get_attribute('href')+'\n')
        imageIndex = imageIndex + 1

    try:
        element = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "next"))
        )
        nextPageUrl = browser.find_element_by_class_name("next").get_attribute('href')
        writeUrlConfig(nextPageUrl, browser)
    except:
        log('�����ȡ���')
        return

if __name__ == '__main__':
    log("/_/_/_/_/_/_/_/_/_/_����ʼ/_/_/_/_/_/_/_/_/_")
    headerOptions = getHeadersOptions()
    browser = getChromeBrowser(headerOptions)
    try:
        log("--��ȡ<<���в�Ʒ>>���濪ʼ--")
        offerlist = readConfig('url-offerlist.txt')
        for url in offerlist:
            writeUrlConfig(url, browser)
        if productList.__len__() > 0:
            with open('url.txt', 'w') as file_to_write:
                file_to_write.writelines(productList)
        log("--��ȡ<<���в�Ʒ>>�������--")

        urls = readConfig('url.txt')
        for url in urls:
            getProductInfo(url, browser)

    except KeyboardInterrupt:
        log("����ȡ��")
    log("/_/_/_/_/_/_/_/_/_/_�������/_/_/_/_/_/_/_/_/_")

    #browser.quit()