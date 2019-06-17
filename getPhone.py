from bs4 import BeautifulSoup
from lxml import html
# import xml
import requests
import re
import csv
import sys
import time

send_headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
              "Connection":"keep-alive",
              "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
              "Accept-Language":"zh-CN,zh;q=0.8"}

# savefile = open('myphone.txt', 'w')
url = "http://detail.zol.com.cn/cell_phone_index/subcate57_list_1.html"

def main(argv):
    print('-------------start get phone-------------')
    pcount = len(argv)
    isAll = False
    if pcount==1:
        #获取全部
        isAll = True
    # isOverContinue = False
    html_doc = requests.get(url,headers=send_headers)                 #Get该网页从而获取该html内容
    soup = BeautifulSoup(html_doc.content, "lxml")  #用lxml解析器解析该网页的内容
    for k in soup.find_all('div',class_='brand-hot brand-list'):#找到div并且class为brand-hot brand-list的标签
        for a in k.find_all('a'):       #在每个对应div标签下找a标签
            # savefile.write(a.string+'\n')#写入[品牌]
            bandstr = a.string
            if isAll == False and bandstr not in argv:
                continue
            # if bandstr!='海信' and isOverContinue==False:
            #     continue
            # isOverContinue = True
            print('get->'+bandstr+' start...')
            csvfile = a.string+'.csv'
            out = open(csvfile,'a', newline='')
            csv_write = csv.writer(out,dialect='excel')
            csv_head = ['型号','出厂系统内核','操作系统','CPU型号']
            csv_write.writerow(csv_head)
            pageindex = 1
            isNoBox = False
            while(isNoBox != True):
                url2 = "http://detail.zol.com.cn"+a.attrs['href']
                url2 = url2[:-5]+'_0_1_2_0_'+str(pageindex)+'.html'
                html_doc2 = requests.get(url2,headers=send_headers)                 #Get该网页从而获取该html内容
                soup2 = BeautifulSoup(html_doc2.content, "lxml")  #用lxml解析器解析该网页的内容          
                for nobox in soup2.find_all('div',class_='no-result-box'):
                    isNoBox = True
                    break       
                if isNoBox == True:
                    continue
                pageindex = pageindex+1
                for i in soup2.find_all('h3'):#,找到div并且class为h3的标签
                    for j in i.find_all('a'):       
                        #savefile.write(j.attrs['title']+'\n')
                        #savefile.write(j.attrs['href']+'\n')
                        time.sleep(1) #等1秒 装的慢一些
                        url3 = "http://detail.zol.com.cn"+j.attrs['href']
                        html_doc3 = requests.get(url3,headers=send_headers)                 #具体的品牌页面
                        soup3 = BeautifulSoup(html_doc3.content, "lxml")  #用lxml解析器解析该网页的内容
                        node_name = soup3.find('h1',class_='product-model__name')#获取[参数]页面
                        if node_name is None:
                            continue
                        node_param = soup3.find('a',href=re.compile(r"param.shtml"))#获取[参数]页面
                        # savefile.write(node_name.string+'\n')
                        # savefile.write(node_param.attrs['href']+'\n')     
                        print(node_name.string) #打印型号
                        #print(node_param.attrs['href']) 
                        url4 = "http://detail.zol.com.cn"+node_param.attrs['href']
                        html_doc4 = requests.get(url4,headers=send_headers)                 #具体的品牌页面
                        soup4 = BeautifulSoup(html_doc4.content, "lxml")  #用lxml解析器解析该网页的内容                
                        tables = soup4.findAll('table')
                        tab = tables[0]   #取得第一个table

                        csv_kernal = ''
                        csv_os = ''
                        csv_cpu = ''

                        for tr in tab.findAll('tr'):   
                            for th in tr.findAll('th'):
                                thstr = th.getText().strip()                       
                                if thstr=='出厂系统内核':
                                    print (thstr)
                                    td = tr.find('td')
                                    span_kernal = td.find('span')
                                    if span_kernal is not None:
                                        csv_kernal=span_kernal.getText()
                                        print(csv_kernal)                                    
                                elif thstr=='操作系统':
                                    print (thstr)
                                    td = tr.find('td')
                                    span_os = td.find('span')
                                    if span_os is not None:
                                        csv_os=span_os.getText() 
                                        print(csv_os)                             
                                elif thstr=='CPU型号':
                                    print (thstr)
                                    td = tr.find('td')
                                    span_cpu = td.find('span',id=re.compile(r"newPmVal"))                                
                                    if span_cpu is not None:                                                             
                                        csv_cpu=span_cpu.next.string
                                        print(csv_cpu)
                        csv_kernal = csv_kernal.replace(u'\xa0', u'')
                        csv_os = csv_os.replace(u'\xa0', u'')
                        csv_cpu = csv_cpu.replace(u'\xa0', u'')                  
                        csv_data = [node_name.string,csv_kernal,csv_os,csv_cpu]
                        csv_write.writerow(csv_data) 
            print('get->'+bandstr+' over!')                                                
    print('-------------over get phone-------------')

if __name__ == "__main__":
    main(sys.argv)