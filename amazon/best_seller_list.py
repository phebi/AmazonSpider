import pandas as pd
import requests
from lxml import etree
import re, time
from aip import AipOcr
import random
import os

class BSR:
    info_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
        "Host": "www.amazon.com",
        # "Sec-Fetch-Mode": "navigate",
        # "Sec-Fetch-Site": "same-origin",
        # "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    # proxies = {
    #     "http": "http://49.86.181.43:9999",
    # }

    url_base = "https://www.amazon.com"
    s = requests.Session()
    s.headers.update(headers)
    res = s.get(url=url_base, headers=headers)
    res_row_html = etree.HTML(res.text)
    title = res_row_html.xpath("//title/text()")
    print(title)
    if title == 'Robot Check':
        img_src = res_row_html.xpath("//div[@class='a-row a-text-center']/img/@src")[0]
        print("验证码图片链接：", img_src)
        amzn_code = res_row_html.xpath("//input[@name='amzn']")[0].get('value')
        amzn_r_code = res_row_html.xpath("//input[@name='amzn-r']")[0].get('value')
        ocr_result = input("输入验证码：")
        # ocr_options = {}
        # ocr_options["detect_direction"] = "true"
        # ocr_options["probability"] = "true"
        # ocr_options["language_type"] = "ENG"
        # ocr_json = client.basicAccurate(img_src)
        # print(ocr_json)
        # if ocr_json.get('words_result_num', None) == 1:
        # ocr_result = ocr_json.get('words_result')[0].get('+words')
        print('机器人检测OCR结果为', ocr_result)
        captcha_row_url = "https://www.amazon.com/errors/validateCaptcha?"
        captcha_url = captcha_row_url + "&amzn=" + amzn_code + "&amzn-r=" + amzn_r_code + "&field-keywords=" + \
                      ocr_result
        ocr_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
            "Host": "www.amazon.com",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.amazon.com"
        }
        s.get(captcha_url, headers=ocr_headers)

    def parse(self, url):
        res = self.s.get(url=url)
        if res.status_code != 200:
            print('解析出错')
            return
        res_html = etree.HTML(res.text)
        try:
            category = res_html.xpath("//span[@class='category']/text()")[0]
        except:
            category = None
        goods_content = res_html.xpath("//li[@class='zg-item-immersion']")
        for each in goods_content:
            try:
                rank_in = each.xpath(".//span[@class='zg-badge-text']/text()")[0]
            except:
                rank_in = None
            try:
                goods_url = each.xpath(".//a[@class='a-link-normal']/@href")[0]
                goods_url = 'https://www.amazon.com' + goods_url.split("ref")[0]
            except:
                goods_url = None

            try:
                asin = re.search('dp/(.*)/', goods_url).group().split("/")[1]

            except:
                asin = None
                print("商品排名{}处: asin解析出错/该商品已下线".format(rank_in))
            try:
                goods_review_str = each.xpath(".//a[@class='a-size-small a-link-normal']/text()")[0]
                goods_review_count = int(goods_review_str.replace(',', ''))
            except:
                goods_review_count = 0
            self.info_list.append((category, rank_in, asin, goods_url, goods_review_count))
            #     # pic_url = each.xpath(".//div[@class='a-section a-spacing-small']/img/@src")[0]
            #
            #     # res_pic = s.get(pic_url, headers=headers, proxies=proxies, verify=False)
            #     # file_name = r'E:\爬虫pycharm\data\pic\\' + asin + '.png'
            #     with open(file_name, "wb") as f:
            #         f.write(res_pic.content)
            #         time.sleep(random.random())
            # except Exception as e:
            #     print(e)

    def run(self, url):
        url_2 = url + '?pg=2'
        print(url)
        self.parse(url=url)
        time.sleep(random.uniform(2, 3))
        print(url_2)
        self.parse(url=url_2)
        time.sleep(random.uniform(2, 3))
        aft = time.strftime("_%m%d_%H%M", time.localtime())
        col = ['category', 'rank_in', 'asin', 'goods_url', 'goods_review_count']
        data_pd = pd.DataFrame(self.info_list, columns=col)

        # 文件保存路径判断
        abs_path = os.path.abspath('../')
        data_path = abs_path + "/data/category/"
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        try:
            category = data_pd['category'][0]
        except:
            category = ''
        print('{}类目下的{}条数据收集完毕'.format(category, len(data_pd)))
        data_pd.to_excel(data_path + category + aft + '.xlsx', encoding='utf-8', engine='xlsxwriter')


if __name__ == '__main__':

    bsr = BSR()
    # 输入一个类目的链接 得到了类目产品列表
    url = 'https://www.amazon.com/gp/bestsellers/home-garden/3744511'
    # 链接中的ref信息用来表示跳转信息，存在状态保持 最好滤除
    if re.search('ref', url):
        url = url.split('ref')[0]
    bsr.run(url)
