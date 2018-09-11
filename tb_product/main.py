# coding=gbk

# ��ȡָ��ҳ�����ƷͼƬ������
#
#import urllib.request
#import requests
import time
from datetime import datetime as dt
from urllib import parse
from urllib import request
from selenium import webdriver
#from bs4 import BeautifulSoup
##import http
##import re
import os
import logging
import sys
import json
import sqlite3

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
    log(url)
    browser.get(url)
    time.sleep(5)

    # �ж��Ƿ��������Ŀ¼����������ڣ�����
    if not os.path.exists('images'):
        os.mkdir('images')

    title = browser.find_element_by_xpath('//*[@id="mod-detail-title"]/h1').text
    if not os.path.exists('images/'+title):
        os.mkdir('images/'+title)

    # ��ҳ��������ϵ��ײ�
    js = "var q=document.documentElement.scrollTop=10000"
    browser.execute_script(js)
    time.sleep(15)

    index = 0
    while index < 200:
        urltmp = '//*[@id="desc-lazyload-container"]/p[' + str(index) + ']/span/strong/span/img'
        images = browser.find_elements_by_xpath(urltmp)
        if images.__len__() == 0:
            urltmp = '//*[@id="desc-lazyload-container"]/p[' + str(index) + ']/span/strong/img'
            images = browser.find_elements_by_xpath(urltmp)
        if images.__len__() == 0:
            urltmp = '//*[@id="desc-lazyload-container"]/p[' + str(index) + ']/span/img'
            images = browser.find_elements_by_xpath(urltmp)
        imageIndex = 1
        for image in images:
            log(image.get_attribute("src"))
            request.urlretrieve(image.get_attribute("src"), './images/' + title + '/' + str(imageIndex) + '.jpg')
            imageIndex = imageIndex + 1
        index = index + 1

def readConfig():
    filename = 'url.txt'
    urls = []
    with open(filename, 'r') as file_to_read:
        while True:
            line = file_to_read.readline()  # ���ж�ȡ����
            if not line:
                break
                pass
            urls.append(line)
    return urls

if __name__ == '__main__':
    log("/_/_/_/_/_/_/_/_/_/_����ʼ/_/_/_/_/_/_/_/_/_")
    headerOptions = getHeadersOptions()
    browser = getChromeBrowser(headerOptions)
    try:
        urls = readConfig()
        for url in urls:
            getProductInfo(url, browser)

    except KeyboardInterrupt:
        log("����ȡ��")
    log("/_/_/_/_/_/_/_/_/_/_�������/_/_/_/_/_/_/_/_/_")

    browser.quit()