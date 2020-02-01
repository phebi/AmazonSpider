import pandas as pd
import requests, lxml
from lxml import etree
import re, time, random, datetime
import threading, queue
import os
import urllib
from aip import AipOcr

APP_ID = '11240997'
API_KEY = '6ZU9O51SKfbaZyg0vzAUWXqN'
SECRET_KEY = 'xtCepeZVrdZ6LSHBDf0xNhYq7PEdY8No '
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


class GoodDetail:
    head_user_agent = [
        'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
        'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
        'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
        'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11']

    url_base = "https://www.amazon.ca"

    s = requests.Session()
    row_headers = {
        'User-Agent': random.choice(head_user_agent),
        "Host": "www.amazon.ca",
        "Upgrade-Insecure-Requests": "1",
    }
    ocr_headers = {
        "Host": "www.amazon.ca",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
    pic_headers = {
        "Host": "images-na.ssl-images-amazon.com",
        "Sec-Fetch-Site": "cross-site",  # 这是一个跨域请求
        "Sec-Fetch-Mode": "no-cors",   # 保证其对应的方法只有HEAD，GET或POST方法 跨域限制  表示允许跨域
        "Upgrade-Insecure-Requests": "1",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    s.headers.update(row_headers)
    res = s.get(url=url_base, timeout=20)
    res_row_html = etree.HTML(res.text)
    title = res_row_html.xpath("//title/text()")[0]
    if title == 'Robot Check':
        img_src = res_row_html.xpath("//div[@class='a-row a-text-center']/img/@src")[0]
        res_pic = s.get(img_src, headers=pic_headers).content
        # print("验证码图片链接：", img_src)
        amzn_code = res_row_html.xpath("//input[@name='amzn']")[0].get('value')
        amzn_r_code = res_row_html.xpath("//input[@name='amzn-r']")[0].get('value')
        ocr_options = {}
        ocr_options["detect_direction"] = "true"
        ocr_options["probability"] = "true"
        ocr_options["language_type"] = "ENG"
        print("验证码图片返回：", res_pic)
        ocr_json = client.basicAccurate(res_pic, ocr_options)
        print(ocr_json)
        if ocr_json.get('words_result_num', None) == 1:
            ocr_result = ocr_json.get('words_result')[0].get('words')
            print("验证码图片链接：", img_src)
            print('自动检测OCR结果为', ocr_result)
        else:
            print(res_pic)
            print("---验证码图片链接---：", img_src)
            ocr_result = input("OCR失败，请手动输入上述图片中的验证码：")
            print('机器人检测OCR结果为', ocr_result)
        captcha_row_url = "https://www.amazon.ca/errors/validateCaptcha?"
        captcha_url = captcha_row_url + "&amzn=" + amzn_code + "&amzn-r=" + amzn_r_code + "&field-keywords=" + \
                      ocr_result
        s.get(captcha_url, headers=ocr_headers)

    change_delivery = 'https://www.amazon.ca/gp/delivery/ajax/address-change.html'
    delivery_data = {
        'locationType': 'LOCATION_INPUT',
        'zipCode': 'E4C 6W4',
        'storeContext': 'generic',
        'deviceType': 'web',
        'pageType': 'Gateway',
        'actionSource': 'glow'
    }
    delivery_header = {
        'Host': 'www.amazon.ca',
        'Connection': 'keep-alive',
        # 'Content-Length': '112',
        'Accept': 'text/html,*/*',
        'Origin': 'https://www.amazon.ca',
        'X-Requested-With': 'XMLHttpRequest',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
        #               'Chrome/69.0.3497.100 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Referer': 'https://www.amazon.ca/',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',

    }
    del_res = s.post(change_delivery, headers=delivery_header, data=delivery_data)
    print('地值更换结果：', del_res.status_code)
    print(s.headers.get('User-Agent'))

    def __init__(self):
        self.detail_list = []
        self.rank_list = []
        self.sec_list = []
        self.begin = 0
        self.begin_503 = 0
        self.url_queue = queue.Queue()
        self.error_set = set()

    def get_detail(self, url):
        import re

        if re.search('slredirect', url):
            ad_plus = 1
            ad_headers = {
                "User-Agent": random.choice(self.head_user_agent),
                "Host": "www.amazon.ca",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
            try:
                url = "https://www.amazon.ca" + urllib.parse.unquote(url.split('url=')[1].split("ref")[0])
            except:
                pass
            print(url)
            res = self.s.get(url, headers=ad_headers, timeout=20)
        else:
            ad_plus = 0
            try:
                url = url.split('/ref')[0]
            except:
                pass
            print(url)
            res = self.s.get(url, timeout=20)

        print(self.s.headers)
        print(res.headers)
        res_row_html = etree.HTML(res.text)
        title = res_row_html.xpath("//title/text()")[0]
        print(res.status_code)
        print(title)

        if title == 'Robot Check':
            img_src = res_row_html.xpath("//div[@class='a-row a-text-center']/img/@src")[0]
            # print("验证码图片链接：", img_src)
            res_pic = self.s.get(img_src, headers=self.pic_headers).content
            print("验证码图片返回：", res_pic)
            amzn_code = res_row_html.xpath("//input[@name='amzn']")[0].get('value')
            amzn_r_code = res_row_html.xpath("//input[@name='amzn-r']")[0].get('value')
            ocr_options = {}
            ocr_options["detect_direction"] = "true"
            ocr_options["probability"] = "true"
            ocr_options["language_type"] = "ENG"
            ocr_json = client.basicAccurate(res_pic, ocr_options)
            print(ocr_json)
            if ocr_json.get('words_result_num', None) == 1:
                ocr_result = ocr_json.get('words_result')[0].get('words')
                print("验证码图片链接：", img_src)
                print('自动OCR结果为', ocr_result)
            else:
                print("---验证码图片链接--- :", img_src)
                ocr_result = input("识别失败，请手动输入验证码：")
                print('机器人检测OCR结果为', ocr_result)

            captcha_row_url = "https://www.amazon.com/errors/validateCaptcha?"
            captcha_url = captcha_row_url + "&amzn=" + amzn_code + "&amzn-r=" + amzn_r_code + "&field-keywords=" + \
                          ocr_result
            self.s.get(captcha_url, headers=self.ocr_headers)
            print("状态cookies：", self.s.cookies.items())

        if res.status_code == 404 and re.search('Page Not Found', title):
            try:
                asin_patt = re.compile("dp/([^/]*)/*")
                asin = re.search(asin_patt, url).groups()[0]
                self.each_detail_list = ['page not found', 'no title', asin]
                self.detail_list.append(self.each_detail_list)
                print("未在加拿大站发现该商品".format(asin))
                return
            except:
                try:
                    self.each_detail_list = ['page not found', 'no title', url.split("/")[-1]]
                    self.detail_list.append(self.each_detail_list)
                    print("未在加拿大站发现该商品".format(url))
                    return
                except:
                    self.each_detail_list = ['page not found', 'no title', url]
                    self.detail_list.append(self.each_detail_list)
                    return
        #  如果是广告链接，且未能正确跳转 返回302的再次尝试
        if res.status_code == 302:
            real_url = res.headers.get('location', '')
            print("跳转到真实链接：", real_url)
            self.get_detail(url=real_url)

        #  返回503， 调整请求头 更换UA后再次尝试
        if res.status_code == 503:

            time.sleep(random.uniform(2, 5))
            print("try again because 503")
            self.begin_503 += 1
            if self.begin_503 >= 3:
                print('该链接{}因503跳转访问出错次数超过3次, 请手动尝试添加'.format(url))
                if url not in self.error_set:
                    self.error_set.add(url)
                return
            headers_503 = {
                "User-Agent": random.choice(self.head_user_agent),
                "Host": "www.amazon.ca",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
            self.s.headers.update(headers_503)
            self.get_detail(url=url)
        if res.status_code != 200:
            print("页面错误，状态码为：", res.status_code)
            # print(res.text)
            try:
                print(etree.HTML(res.text).xpath("//title/text()")[0])
                # self.each_detail_list = ['page not found', 'no title', url]
                # self.detail_list.append(self.each_detail_list)
            except:
                pass
            return

        from bs4 import BeautifulSoup
        soup_res = BeautifulSoup(res.text, features='lxml')
        detail_text = soup_res.select('body')
        res_html = etree.HTML(str(detail_text[0]))

        try:
            goods_title = res_html.xpath("string(//span[@id='productTitle'])")
            goods_title = goods_title.replace("\n", '').replace('\t', '').strip()
        except:
            goods_title = None

        if not goods_title:
            time.sleep(random.uniform(2, 5))
            print("try again")
            self.begin += 1
            if self.begin >= 3:
                print('该链接{}访问出错次数超过3次, 请手动尝试添加'.format(url), "可能是不可解析的广告链接")
                self.error_set.add(url)
                return
            self.get_detail(url=url)

        self.begin = 0
        # 不同类别、颜色、款式的编号
        # 仅仅能获取到部分可以直接点击得到的ASIN, 如果需要完整的父子ASIN数据可使用 keepa API
        try:
            sorts_codes = res_html.xpath('//*[starts-with(@id, "size_name")]/@data-defaultasin')[:]
            color_sorts = res_html.xpath('//*[starts-with(@id, "color_name")]/@data-defaultasin')[:]
            style_sorts = res_html.xpath('//*[starts-with(@id, "style_name")]/@data-defaultasin')[:]
            sort_list_raw = sorts_codes + color_sorts + style_sorts
            sort_list = list(set(sort_list_raw))

            if "" in sort_list:
                sort_list.remove('')

            sorts_color_url = res_html.xpath("//*[starts-with(@id, 'color_name')]/@data-dp-url")[:]
            sorts_size_url = res_html.xpath("//*[starts-with(@id, 'size_name')]/@data-dp-url")[:]
            sorts_style_url = res_html.xpath("//*[starts-with(@id, 'style_name')]/@data-dp-url")[:]
            asin_patt = re.compile("dp/(.*)/")
            sort_url_raw = sorts_color_url + sorts_size_url + sorts_style_url
            print("sort_list_raw:", sort_list_raw)
            print("sort_url_raw:", sort_url_raw)

            sort_url_list = [re.search(asin_patt, each).groups()[0] for each in sort_url_raw if each]
            sort_url_list = list(set(sort_url_list))
            if '' in sort_url_list:
                sort_url_list.remove('')
            sort_list.extend(sort_url_list)
        except:
            sort_list = []

        item = {}
        if res_html.xpath('//div[@id="detail-bullets"]//div[@class="content"]/ul/li'):
            print("model-0")
            for each in res_html.xpath('//div[@id="detail-bullets"]//div[@class="content"]/ul/li'):
                li = each.xpath('string(.)')
                li = li.replace('\n', '').replace('\t', '')
                try:
                    key = li.split(":")[0].strip()
                    value = li.split(":")[1].strip()
                except:
                    key = 'miss key'
                    value = 'miss value'
                import re
                if not (re.search('rank', key.lower()) or re.search('review', key.lower())):
                    item[key] = value
            goods_rank = res_html.xpath('string(//li[@id="SalesRank"])')
            item['raw_goods_rank'] = goods_rank

        if res_html.xpath('//*[@id="productDetailsTable"]//div[@class="content"]/ul/li'):
            print("加拿大站-model-0")
            for each in res_html.xpath('//*[@id="productDetailsTable"]//div[@class="content"]/ul/li'):
                li = each.xpath('string(.)')
                li = li.replace('\n', '').replace('\t', '')
                try:
                    key = li.split(":")[0].strip()
                    value = li.split(":")[1].strip()
                except:
                    key = 'miss key'
                    value = 'miss value'
                import re
                if not (re.search('rank', key.lower()) or re.search('review', key.lower())):
                    item[key] = value
            goods_rank = res_html.xpath('string(//li[@id="SalesRank"])')
            item['raw_goods_rank'] = goods_rank

        if res_html.xpath("//div[@class='pdTab']"):
            print('加拿大站-model-1')
            for each in res_html.xpath("//div[@class='pdTab']//tr"):
                key = each.xpath("string(.//td[@class='label'])")
                # print(key, "---")
                value = each.xpath("string(.//td[@class='value'])")
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value



        if res_html.xpath("//div[@id='detailBullets_feature_div']/ul"):
            absr = res_html.xpath('string(//div[@id="dpx-amazon-sales-rank_feature_div"]/li)')
            item['Amazon Best Sellers Rank'] = absr
            print("model-1")
            for each in res_html.xpath('//div[@id="detailBullets_feature_div"]/ul/li'):
                key = each.xpath('.//span/span[1]/text()')
                value = each.xpath('.//span/span[2]/text()')
                if key and value:
                    key = key[0].replace("\n", '').replace("\t", '').strip(": (")
                    value = value[0].replace("\n", '').replace("\t", '').strip(": (")
                    print(key, "---", value)
                    if key != "Customer Reviews":
                        item[key] = value

        if res_html.xpath("//div[@class='a-section table-padding']/table//tr"):
            print("model-2")
            for each in res_html.xpath("//div[@class='a-section table-padding']/table//tr"):
                key = each.xpath("string(.//th)")
                value = each.xpath("string(.//td)")
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value

        if res_html.xpath("//table[@id='productDetails_detailBullets_sections1']"):
            print("model-3")
            for each in res_html.xpath("//table[@id='productDetails_detailBullets_sections1']//tr"):
                key = each.xpath("string(./th)")
                value = each.xpath("string(./td)")
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value

        if res_html.xpath("//table[@id='productDetails_techSpec_section_1']"):
            print("model-4")
            for each in res_html.xpath("//table[@id='productDetails_techSpec_section_1']//tr"):
                key = each.xpath("string(.//th)")
                value = each.xpath("string(.//td)")
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value

        if res_html.xpath("//div[@class='wrapper USlocale']"):
            print("model-5")
            for each in res_html.xpath("////div[@class='wrapper USlocale']//tr"):
                key = each.xpath("string(.//td[@class='label'])")
                value = each.xpath("string(.//td[@class='value'])")
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value
                        print(key, "---", value)

        # 图片路径
        try:
            goods_pic_url = res_html.xpath('//img[@id="landingImage"]/@src')[0]
        except:
            goods_pic_url = None

        asin = item.get('ASIN', None)
        if not asin:
            try:
                asin_patt = re.compile("dp/([^/]*)/*")
                asin = re.search(asin_patt, url).groups()[0]
            except:
                pass

        try:
            sort_list.append(asin)
        except:
            pass
        multi_asin = list(set(sort_list))
        print("-----------")
        print(multi_asin)
        print("-----------")
        product_dimensions = item.get('Product Dimensions', None)
        package_dimensions = item.get('Package Dimensions', None)
        product_weight = item.get('Item Weight', None)
        date_on_shelf = item.get('Date first listed on Amazon', None)
        if not date_on_shelf:
            date_on_shelf = item.get('date_on_shelf', None)
            if not date_on_shelf:
                date_on_shelf = item.get('Date First Available', None)

        feature_list = res_html.xpath("//div[@id='feature-bullets']/ul/li/span/text()")
        features = []
        for feature in feature_list:
            feature = feature.strip()
            features.append(feature)

        goods_ranks = item.get('raw_goods_rank', None)
        goods_each_ranks = goods_ranks
        print(goods_ranks)
        if not goods_ranks:
            goods_ranks = item.get('Best Sellers Rank', None)
            if not goods_ranks:
                goods_ranks = item.get('Amazon Best Sellers Rank', None)
                if not goods_ranks :
                    goods_ranks = item.get('Amazon Bestsellers Rank')

        category_main = None
        rank_main = None
        if not goods_ranks:
            goods_each_ranks = {}
            self.rank_list.append(goods_each_ranks)

        if goods_ranks:
            print("---")
            import re
            weight_str = re.compile(r'\(.*\)')
            goods_rank = goods_ranks.replace("\n", '').replace("\t", '').replace("\xa0", ' ')
            patt = re.compile(r'[\(\{].*[\)\}]')
            patt2 = re.compile(r'\s{2,}')
            goods_rank = re.sub(patt, '', goods_rank)
            goods_rank = re.sub(patt2, ' ', goods_rank)
            goods_each_ranks = {}

            for each in goods_rank.split('#')[1:]:
                goods_rank_num, goods_rank_sort = each.split("in", 1)
                try:
                    goods_rank_num = int(goods_rank_num.replace(',', '').strip())
                except:
                    pass
                goods_rank_sort = re.sub(weight_str, '', goods_rank_sort)
                goods_each_ranks[goods_rank_sort.strip()] = goods_rank_num

            self.rank_list.append(goods_each_ranks)
            print(self.rank_list[-1])

            try:
                category_main = list(self.rank_list[-1].keys())[0]
                rank_main = int(list(self.rank_list[-1].values())[0])
            except:
                category_main, rank_main = None, None
            # print(category_main, rank_main)
        # 评价数量
        try:
            goods_review_count = \
            res_html.xpath('//div[@id="averageCustomerReviews"]//span[@id="acrCustomerReviewText"]/text()')[0]
            goods_review_count = int(goods_review_count.split(" ")[0].replace(",", ""))
        except:
            goods_review_count = 0

        # 评价星级
        try:

            goods_review_star = res_html.xpath('//div[@id="averageCustomerReviews"]//span[@class="a-icon-alt"]/text()')[
                0]
            goods_review_star = float(goods_review_star.split(" ")[0])
        except:
            goods_review_star = None

        try:
            goods_price = res_html.xpath("//span[starts-with(@id,'priceblock')]/text()")[0]
        except:
            goods_price = None

        try:
            brand = res_html.xpath('//a[@id="bylineInfo"]/text()')[0]
        except:
            try:
                brand = res_html.xpath("//a[@id='brand']/text()")[0]
            except:
                brand = None

        # 卖方
        try:
            seller = res_html.xpath('string(//div[@id="merchant-info"])')
            seller = seller.replace("\n", "").split("Reviews")[0].strip()
            if not seller:
                try:
                    seller = res_html.xpath('string(//span[@id="merchant-info"])')
                    seller = seller.replace("\n", "").split("Reviews")[0].strip()
                except:
                    seller = None
        except:
            seller = None

        try:
            seller_cls = seller_handle(seller)
        except:
            seller_cls = None

        each_detail_list = (goods_pic_url, goods_title, asin, brand, ad_plus, goods_price, seller, seller_cls,
                            date_on_shelf, goods_review_count, product_dimensions, package_dimensions,
                            product_weight, goods_review_star, category_main, rank_main, goods_each_ranks)
        # if goods_title:
        self.detail_list.append(each_detail_list)

    def run(self, data_path, start=0, end=None):

        if data_path.endswith('xlsx'):
            data = pd.read_excel(data_path, encoding='utf-8')
            for asin in data['asin'][start: end]:
                if asin:
                    url = "https://www.amazon.ca/dp/" + str(asin)
                    self.url_queue.put(url)
                    print(self.url_queue.qsize())
        if data_path.endswith('csv'):
            data = pd.read_csv(data_path, encoding='utf-8')
            for url in data['goods_url_full'][start: end]:
                if url:
                    self.url_queue.put(url)
                    print(self.url_queue.qsize())

        while True:
            try:
                thread_list = [threading.Thread(target=goods_detail.get_detail, args=(self.url_queue.get(),))
                               for i in range(20) if not self.url_queue.empty()]
                time.sleep(random.uniform(2, 4))

                for each in thread_list:
                    self.s.headers.update({'User-Agent': random.choice(self.head_user_agent)})
                    try:
                        time.sleep(random.random())
                        each.start()
                        print("线程：", each.name)
                    except Exception as e:
                        time.sleep(random.random(2,3))
                        each.start()
                        print(each, "重试中")
                        print(e)
                for each in thread_list:
                    each.join()

            except Exception as e:
                print(e)
            if self.url_queue.empty():
                break

        details_pd = pd.DataFrame(goods_detail.detail_list,
                                  columns=["goods_pic_url", "goods_title", "asin", "brand", "ad_plus", "goods_price",
                                           "seller", "seller_cls", "date_on_shelf", "goods_review_count",
                                           "product_dimensions", "package_dimensions", "product_weight",
                                           "goods_review_star", "category_main", "rank_main", "goods_each_ranks"]
                                  )

        aft = datetime.datetime.now().strftime('%m%d%H%M')

        for base_code_full, asin in zip(details_pd['goods_pic_url'], details_pd['asin']):
            if base_code_full and asin:
                if re.search('data:image', base_code_full):
                    try:
                        base_code = base_code_full.split(',')[1]
                        pic_save(base_code, asin)
                    except Exception as e:
                        print("图片存储错误：", base_code_full, e)
                if re.search('http', base_code_full):
                    try:
                        print(base_code_full)
                        pic_res = self.s.get(base_code_full, headers=self.pic_headers)
                        # print(pic_res.text)
                        if pic_res.status_code == 200:
                            pic_content = pic_res.content
                            if not os.path.exists("../data/pic/"):
                                os.makedirs('../data/pic/')
                            with open(r"../data/pic/" + str(asin) + '.jpg', 'wb') as f:
                                f.write(pic_content)
                        else:
                            print("图片获取结果：{}".format(pic_res.status_code))
                    except:
                        print("ASIN：{}图片保存错误".format(asin))

        time.sleep(3)
        abs_path = os.path.abspath('../')
        data_path = abs_path + "/data/goods_detail/"
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        if end:
            file_name = data_path + aft + "_" + str(start) + "_" + str(end) + "_in_ca.xlsx"
        else:
            file_name = data_path + aft + "_" + str(start) + "all_in_ca.xlsx"
        try:
            details_pd['pic_url'] = abs_path + r"\data\pic\\" + details_pd['asin'] + ".jpg"
            details_pd['pic_table_url'] = '<table> <img src=' + '\"' + details_pd['pic_url'] + '\"' + 'height="140" >'
        # details_pd.sort_values(by=['sales_est'], inplace=True, ascending=False)
        except:
            pass
        details_pd.drop_duplicates(subset=['goods_title', 'asin'], inplace=True)
        details_pd.dropna(subset=['goods_pic_url', 'goods_title'], inplace=True)
        details_pd.to_excel(file_name, encoding='utf-8')
        if self.error_set:
            print("以下链接未能正确解析，请手动查证")
            for each in self.error_set:
                print(each)


def weight_handle(weight):
    # 把kg ounce pound 都转化为数字存储
    weight = weight.lower().replace(',', '')
    if re.search("kg", weight):
        weight_int = float(weight.split(' ')[0]) * 1000

    elif re.search("ounce", weight):
        weight_int = float(weight.split(' ')[0]) * 28.35

    elif re.search("pound", weight):
        weight_int = float(weight.split(' ')[0]) * 453.60

    else:
        try:
            weight_int = float(weight.split(' ')[0])
        except:
            weight_int = weight
    return weight_int


def feature_handle(feature):
    import re
    patt = re.compile('(\d+)[^\d+]*[by\*x]\s*(\d+)')
    res = re.search(patt, feature.lower()).groups()
    return res


def seller_handle(seller):
    # 卖家类型识别
    if not seller:
        return None
    else:
        if re.search('Ships from and sold by Amazon', seller, re.I):
            return 'AMZ'
        elif re.search('Fulfilled by Amazon', seller, re.I):
            return 'FBA'
        else:
            return 'FBM'


def pic_save(base_code, asin):

    import base64
    img_data = base64.b64decode(base_code)
    if not os.path.exists("../data/pic/"):
        os.makedirs('../data/pic/')
    with open(r"../data/pic/" + str(asin) + '.jpg', 'wb') as f:
        f.write(img_data)


if __name__ == '__main__':

    goods_detail = GoodDetail()
    # data_path = r"E:\AmazonPycharm\others\data\hom类目前10000名.xlsx"
    # goods_detail.run(data_path, start=2600, end=2700)

