import pandas as pd
import requests
from lxml import etree
import re, time, random, datetime
import pymysql
import os
import urllib
from aip import AipOcr

# User_Agent 库 随机选取作为请求头
head_user_agent = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]


def weight_handle(weight):
    """
    :param 重量:
    :return: 把千克、磅、盎司统一转化为克重
    """
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


# def feature_handle(feature):
#     """
#     正则， 特征处理 返回尺寸 实际未使用该函数
#     :param feature:
#     :return:
#     """
#     import re
#     patt = re.compile('(\d+)[^\d+]*[by\*x]\s*(\d+)')
#     res = re.search(patt, feature.lower()).groups()
#     return res


def seller_handle(seller):
    """
    卖家处理 识别为AMZ/FMA/FBM
    :param seller: 卖家字段
    :return:
    """
    if not seller:
        return None
    else:
        if re.search('sold by Amazon.com', seller, re.I):
            return 'AMZ'
        elif re.search('Fulfilled by Amazon', seller, re.I):
            return 'FBA'
        else:
            return 'FBM'


def get_sales(rank, cate="Home & Kitchen"):
    """
    请求估算销量的接口
    :param rank: 排名
    :param cate: 根类目名称
    :return: 销量数据
    """
    import requests
    import urllib
    s = requests.Session()
    row_headers = {
        "User-Agent": random.choice(head_user_agent),
    }
    sales_url = "https://amzscout.net/extensions/scoutlite/v1/sales?"
    full_url = sales_url + "domain=COM&category=" + urllib.parse.quote(cate)+ "&rank=" + str(rank)
    print(full_url)
    s.headers.update(row_headers)

    try:
        res = s.get(full_url, timeout=10)
        return res.json().get('sales')
    except:
        return None


# 定义一个获取详情页的类
class GoodDetail:
    # headers = {
    #     # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"
    # }

    # proxies = {
        # "https": "https://114.239.198.228:9999",
    # }
    # 美国站 初次请求 用来保存请求状态
    url_base = "https://www.amazon.com"

    # 连接数据库 将数据写入指定表格中
    conn = pymysql.connect(host='localhost', port=3306, db='amazon_test', user='root', passwd='1118')
    s = requests.Session()
    row_headers = {
        'User-Agent': random.choice(head_user_agent),
        "Host": "www.amazon.com",
        "Upgrade-Insecure-Requests": "1",
    }
    ocr_headers = {
        "Host": "www.amazon.com",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
    pic_headers = {
        "Host": "images-na.ssl-images-amazon.com",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    s.headers.update(row_headers)
    # 在初次请求后修改请求头
    res_row = s.get(url=url_base)
    s.headers.update({
        "Host": "www.amazon.com",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",  # 是否通过键盘鼠标操作得到的链接 是
        "Upgrade-Insecure-Requests": "1",
    })
    res_row_html = etree.HTML(res_row.text)
    title = res_row_html.xpath("//title/text()")[0]
    print(title)
    # 初次请求的机器人识别 ：如果返回的数据是机器人检测的页面 识别到指定的验证码图片，人工识别后输入
    if title == 'Robot Check':
        img_src = res_row_html.xpath("//div[@class='a-row a-text-center']/img/@src")[0]
        print("验证码图片链接：", img_src)
        amzn_code = res_row_html.xpath("//input[@name='amzn']")[0].get('value')
        amzn_r_code = res_row_html.xpath("//input[@name='amzn-r']")[0].get('value')
        ocr_result = input("输入验证码：")
        # 常使用百度智能的 OCR算法直接机器识别，但是准确率较低，故需人工识别
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

        s.get(captcha_url, headers=ocr_headers)
    print("状态cookies：", s.cookies.items())

    delivery_data = {
        'locationType': 'LOCATION_INPUT',
        'zipCode': '90014',
        'storeContext': 'generic',
        'deviceType': 'web',
        'pageType': 'Gateway',
        'actionSource': 'glow'
    }
    delivery_header = {
        'Host': 'www.amazon.com',
        'Connection': 'keep-alive',
        # 'Content-Length': '112',
        'Accept': 'text/html,*/*',
        'Origin': 'https://www.amazon.com',
        'X-Requested-With': 'XMLHttpRequest',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
        #               'Chrome/69.0.3497.100 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Referer': 'https://www.amazon.com/',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    change_delivery = 'https://www.amazon.com/gp/delivery/ajax/address-change.html'
    deliver_res = s.post(change_delivery, headers=delivery_header, data=delivery_data)
    print(deliver_res)

    def __init__(self):
        # 初始化一些用来存储信息的列表
        self.detail_list = []
        self.rank_list = []
        self.sec_list = []
        self.begin = 0  # 请求出错计数
        self.begin_503 = 0  # 503请求出错计数
        self.error_list = []  # 未能正确请求的链接 再所有请求结束后 会再次请求（再尝试一次 不会循环）

    def get_detail(self, url):
        import re
        if re.search('slredirect', url):
            ad_plus = 1
            ad_headers = {
                "User-Agent": random.choice(head_user_agent),
                "Host": "www.amazon.com",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",   # 是否通过键盘鼠标操作操作发出请求
                "Upgrade-Insecure-Requests": "1",
            }
            try:
                url = "https://www.amazon.com" + urllib.parse.unquote(url.split('url=')[1].split("ref")[0])
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
            res = self.s.get(url, timeout=20,)
        print(self.s.headers)
        print(res.headers)
        res_row_html = etree.HTML(res.text)
        title = res_row_html.xpath("//title/text()")[0]
        print(res.status_code)
        print(title)
        # 请求过程中的机器人识别
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
            self.s.get(captcha_url, headers=self.ocr_header)
            print("状态cookies：", self.s.cookies.items())

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
                if url not in self.error_list:
                    self.error_list.append(url)
                return
            headers_503 = {
                "User-Agent": random.choice(head_user_agent),
                "Host": "www.amazon.com",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
            self.s.headers.update(headers_503)
            self.get_detail(url=url)
        if res.status_code != 200:
            print("页面错误，状态码为：", res.status_code)
            print(res.text)
            try:
                print(etree.HTML(res.text).xpath("//title/text()")[0])
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
                print('该链接{}访问出错次数超过3次, 请手动尝试添加'.format(url),"可能是不可解析的广告链接")
                return
            self.get_detail(url=url)

        self.begin = 0
        # 类别
        kinds = res_html.xpath("//div[@class='twisterTextDiv text']/span[@class='a-size-base' and 1]/text()")[:]

        # sort_list = []
        if not kinds:
            kinds = res_html.xpath('//div[@class="a-section a-spacing-none twisterShelf_displaySection"]/span/text()')[:]

        # 不同类别、颜色、款式的编号
        # 仅仅能获取到部分可以直接点击得到的ASIN, 如果需要完整的父子ASIN数据可使用keepa API
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

            sort_url_raw = sorts_color_url + sorts_size_url + sorts_style_url
            print("sort_list_raw:", sort_list_raw)
            print("sort_url_raw:", sort_url_raw)
            asin_patt = re.compile("dp/([^/]*)/*")
            sort_url_list = [re.search(asin_patt, each).groups()[0] for each in sort_url_raw if each]
            sort_url_list = list(set(sort_url_list))
            if '' in sort_url_list:
                sort_url_list.remove('')
            sort_list.extend(sort_url_list)
        except:
            sort_list = []

        try:
            choosen_kinds = res_html.xpath('//div[starts-with(@id, "variation")]/div/span/text()')
            if choosen_kinds:
                choose_kind = choosen_kinds[0].strip()
            else:
                choose_kind = res_html.xpath('//span[@class="shelf-label-variant-name"]/text()')[0].strip()
        except:
            choose_kind = "Just One Kind"

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

        if res_html.xpath("//div[@id='detailBullets_feature_div']/ul"):
            absr = res_html.xpath('string(//div[@id="dpx-amazon-sales-rank_feature_div"]/li)')
            item['Amazon Best Sellers Rank'] = absr
            print("model-1")
            for each in res_html.xpath('//div[@id="detailBullets_feature_div"]/ul/li'):
                key = each.xpath('.//span/span[1]/text()')
                # print(key)
                value = each.xpath('.//span/span[2]/text()')
                # print(value)
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
                # print(key, "---")
                value = each.xpath("string(.//td)")
                #     print(key, value)
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value

        if res_html.xpath("//table[@id='productDetails_detailBullets_sections1']"):
            print("model-3")
            for each in res_html.xpath("//table[@id='productDetails_detailBullets_sections1']//tr"):
                # print("model1--in")
                key = each.xpath("string(./th)")
                # print(key, "---")
                value = each.xpath("string(./td)")
                # print(key, value)
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value

        if res_html.xpath("//table[@id='productDetails_techSpec_section_1']"):
            print("model-4")
            for each in res_html.xpath("//table[@id='productDetails_techSpec_section_1']//tr"):
                key = each.xpath("string(.//th)")
                # print(key, "---")
                value = each.xpath("string(.//td)")
                # print(key, value)
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value

        if res_html.xpath("//div[@class='wrapper USlocale']"):
            print("model-5")
            for each in res_html.xpath("////div[@class='wrapper USlocale']//tr"):
                # print("model3--in")
                key = each.xpath("string(.//td[@class='label'])")
                # print(key, "---")
                value = each.xpath("string(.//td[@class='value'])")
                # print(key, "---", value)
                if key and value:
                    key = key.replace("\n", '').replace("\t", '').strip()
                    value = value.replace("\n", '').replace("\t", '').strip()
                    if key != "Customer Reviews":
                        item[key] = value
                        print(key,"---", value)

        # 图片路径
        try:
            goods_pic_url = res_html.xpath('//img[@id="landingImage"]/@src')[0]
        except:
            goods_pic_url = None

        asin = item.get('ASIN', None)

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

        if product_weight:
            product_weight = weight_handle(product_weight)
        ship_weight = item.get('Shipping Weight', None)
        if ship_weight:
            ship_weight = weight_handle(ship_weight)

        feature_list = res_html.xpath("//div[@id='feature-bullets']/ul/li/span/text()")
        features = []
        for feature in feature_list:
            feature = feature.strip()
            features.append(feature)

        rank_in_hk = None
        goods_ranks = item.get('raw_goods_rank', None)
        goods_each_ranks = goods_ranks
        print(goods_ranks)
        if not goods_ranks:
            goods_ranks = item.get('Best Sellers Rank', None)
            if not goods_ranks:
                goods_ranks = item.get('Amazon Best Sellers Rank', None)

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
                    goods_rank_num = int(goods_rank_num.replace(',','').strip())
                except:
                    pass
                goods_rank_sort = re.sub(weight_str, '', goods_rank_sort)
                goods_each_ranks[goods_rank_sort.strip()] = goods_rank_num
                if re.search('Home & Kitchen', goods_rank_sort):
                    try:
                        rank_in_hk = int(goods_rank_num)
                    except:
                        rank_in_hk = None

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
            goods_review_count = res_html.xpath('//div[@id="averageCustomerReviews"]//span[@id="acrCustomerReviewText"]/text()')[0]
            goods_review_count = int(goods_review_count.split(" ")[0].replace(",", ""))
        except:
            goods_review_count = 0

        # 评价星级
        try:

            goods_review_star = res_html.xpath('//div[@id="averageCustomerReviews"]//span[@class="a-icon-alt"]/text()')[0]
            goods_review_star = float(goods_review_star.split(" ")[0])
        except:
            goods_review_star = None

        # 高频评价
        fre_words = res_html.xpath('//*[@id="cr-lighthut-1-"]/div/span/a/span/text()')[:]
        high_fre_words = [each.strip() for each in fre_words if each]

        try:
            goods_price = res_html.xpath("//span[starts-with(@id,'priceblock')]/text()")[0]
        except:
            goods_price =None

        import json
        try:
            brand = res_html.xpath('//a[@id="bylineInfo"]/text()')[0]
        except:
            try:
                brand = res_html.xpath("//a[@id='brand']/text()")[0]
            except:
                brand = None
        try:
            buy_box_info = res_html.xpath('//*[@id="turboState"]/script/text()')[0]
            buy_box_json = json.loads(buy_box_info)
            stockOnHand = buy_box_json['eligibility']['stockOnHand']
        except:
            stockOnHand = None

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

        seller_name, seller_months, seller_review_count = None, None, None
        if seller_cls == 'FBA' or 'FBM':
            try:
                seller_href = res_html.xpath("//div[@id='merchant-info']/a[1]/@href")[0]
                seller_url = "https://www.amazon.com" + seller_href
                seller_res = self.s.get(seller_url, timeout=20)
                if seller_res.status_code != 200:
                    print('{}卖家信息查询出错'.format(url))
                    print(seller_res.text)
                seller_res_html = etree.HTML(seller_res.text)

                try:
                    seller_name = seller_res_html.xpath("//h1[@id='sellerName']/text()")[0]
                except:
                    print("未解析到卖家名称")
                    pass

                try:
                    seller_review_str = \
                    seller_res_html.xpath("//a[@class='a-link-normal feedback-detail-description']/text()")[0]
                    try:
                        count_patt = re.compile('in the last (.*) months \((.*) ratings\)')
                        a, b = re.search(count_patt, seller_review_str).groups()
                        seller_months, seller_review_count = int(a), int(b)
                    except:
                        pass

                    if not seller_review_count:
                        try:
                            another_patt = re.compile('(\d+) total ratings\)')
                            seller_months = 0
                            seller_review_count = int(re.search(another_patt, seller_review_str).group(1))
                        except:
                            print("新卖家年评论量解析出错")
                except:
                    print("卖家年评论数量解析出错")
                    pass
            except:
                print("未解析到卖家信息")
                pass
        sales_est = None
        if category_main and rank_main:
            print(category_main, rank_main, '销量预测中...')
            try:
                sales_est = int(get_sales(cate=category_main, rank=rank_main))
                # if sales_est >= 2000:
                #     sales_est = int(sales_est*1)
                # elif sales_est >= 1000:
                #     sales_est = int(sales_est*1.15)
                # else:
                #     sales_est = int(sales_est*1.25)
                # time.sleep(random.random())
                # print("sales:",sales_est)
            except:
                print(asin,'查询销量出错')
                pass

        each_detail_list = (goods_pic_url,goods_title, asin, brand, ad_plus, goods_price, choose_kind,
                            seller, seller_cls, seller_name, seller_months, seller_review_count,
                            rank_in_hk, date_on_shelf, stockOnHand, goods_review_count,product_dimensions,
                            package_dimensions, product_weight, ship_weight, goods_review_star, category_main,
                            rank_main, sales_est, high_fre_words, multi_asin, goods_each_ranks)
        if goods_title:
            self.detail_list.append(each_detail_list)

        #  如果获取到asin数据， 把asin相关的数据写入到数据库
        if asin:
            # try:
            cs = self.conn.cursor()
            cs.execute('select * from amazon_test.goods_detail where goods_detail.asin=(%s)', asin)
            result = cs.fetchone()
            if result:
                update_sql = 'update goods_detail set rank_in_HK=(%s), goods_review_count=(%s),goods_review_star=(%s), ' \
                             'category_main=(%s), rank_main=(%s), goods_price=(%s), seller_cls=(%s), sales_est=(%s), high_fre_words=(%s)' \
                             'where asin=(%s)'
                count = cs.execute(update_sql, (rank_in_hk, goods_review_count, goods_review_star, category_main, rank_main,
                                                goods_price, seller_cls, sales_est, str(high_fre_words), asin))
                self.conn.commit()
                print(count, "asin已存在，更新完毕")
                cs.close()

            else:
                insert_sql = 'insert into amazon_test.goods_detail(pic, goods_title, asin, brand, goods_price, seller_cls,' \
                             ' category_main, rank_main, sales_est, rank_in_HK, date_on_shelf, goods_review_count, goods_review_star, ' \
                             'product_dimensions, package_dimensions, product_weight, ship_weight, goods_each_ranks, high_fre_words)' \
                             ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                if goods_each_ranks:
                    sql_ranks = json.dumps(goods_each_ranks)
                else:
                    sql_ranks = ""

                count = cs.execute(insert_sql, (goods_pic_url,goods_title, asin, brand, goods_price, seller_cls,
                             category_main, rank_main, sales_est, rank_in_hk, date_on_shelf, goods_review_count, goods_review_star,
                            product_dimensions, package_dimensions, product_weight, ship_weight, sql_ranks, str(high_fre_words)))

                try:
                    self.conn.commit()
                except:
                    self.conn.rollback()

                print(count, "asin已添加")

                cs.execute('select count(*) from amazon_test.goods_detail')

                result = cs.fetchall()
                print(result)
                cs.close()


def pic_save(base_code, asin):
    import base64
    img_data = base64.b64decode(base_code)
    if not os.path.exists("../data/pic/"):
        os.makedirs('../data/pic/')
    with open(r"../data/pic/" + str(asin) + '.jpg', 'wb') as f:
        f.write(img_data)


def seller_check(url):
    print("卖家年评论数获取中...")
    s = requests.Session()

    s.headers.update({'User-Agent': random.choice(head_user_agent)})
    seller_res = s.get(url, timeout=20)
    if seller_res.status_code != 200:
        print('{}卖家信息查询出错'.format(url))
        return None
    seller_res_html = etree.HTML(seller_res.text)

    seller_name, seller_months, seller_review_count = None, None, None
    try:
        seller_name = seller_res_html.xpath("//h1[@id='sellerName']/text()")[0]
    except:
        pass

    try:
        seller_review_str = seller_res_html.xpath("//a[@class='a-link-normal feedback-detail-description']/text()")[0]
    except:
        return

    try:
        count_patt = re.compile('in the last (.*) months \((.*) ratings\)')
        a, b = re.search(count_patt, seller_review_str).groups()
        seller_months, seller_review_count = int(a), int(b)
    except:
        pass

    if not seller_review_count:
        try:
            another_patt = re.compile('(\d+) total ratings\)')
            seller_months = 0
            seller_review_count = int(re.search(another_patt, seller_review_str).group(1))
        except:
            pass

    return seller_name, seller_months, seller_review_count


def main(data_file, start=0, end=61):
    goods_detail = GoodDetail()

    if data_file.endswith('csv'):
        data = pd.read_csv(data_file)
        # 选择数据范围
        # for url in data['goods_url_full'][起始位置:结束位置]
        for url in data['goods_url_full'][start: end]:
            if url:
                # print(url)
                try:
                    goods_detail.get_detail(url)
                except Exception as e:
                    print(e)
                time.sleep(random.random())

    if data_file.endswith('xlsx'):
        data = pd.read_excel(data_file, encoding='utf-8')
        for asin in data['asin'][start: end]:
            if asin:
                url = "https://www.amazon.com/dp/" + str(asin)
                print(url)
                goods_detail.get_detail(url)
                time.sleep(random.random())

    last_info_list = goods_detail.detail_list

    # 判断是否有错误的页面，返回链接列表 再试一次
    another_list = None
    print("error_list:", goods_detail.error_list)
    if goods_detail.error_list:
        another_detail = GoodDetail()
        for each in goods_detail.error_list:
            another_detail.get_detail(each)
        another_list = another_detail.detail_list

    if another_list:
        last_info_list.extend(another_list)

    details_pd = pd.DataFrame(last_info_list,
                              columns=['goods_pic_url', 'goods_title', 'asin', 'brand', 'ad_plus', 'goods_price',
                                       'choose_kind', 'seller', 'seller_cls', 'seller_name', 'seller_months',
                                       'seller_review_count', 'rank_in_HK', 'date_on_shelf', 'stockOnHand',
                                       'goods_review_count', 'product_dimensions', 'package_dimensions',
                                       'product_weight', 'ship_weight', 'goods_review_star', 'category_main',
                                       'rank_main', 'sales_est', 'high_fre_words', 'multi_asin', 'goods_each_ranks'])
    # ranks_pd = pd.DataFrame(goods_detail.rank_list)
    aft = datetime.datetime.now().strftime('%m%d%H%M')

    for base_code_full, asin in zip(details_pd['goods_pic_url'], details_pd['asin']):
        if base_code_full and asin:
            if re.search('data:image', base_code_full):
                try:
                    base_code = base_code_full.split(',')[1]
                    pic_save(base_code, asin)
                except Exception as e:
                    print("图片存储错误：", base_code_full, e)
            if re.search('https', base_code_full):
                try:
                    pic_res = goods_detail.s.get(base_code_full, headers=goods_detail.pic_headers)
                    if pic_res.status_code == 200:
                        pic_content = pic_res.content
                        if not os.path.exists("../data/pic/"):
                            os.makedirs('../data/pic/')
                        with open(r"../data/pic/" + str(asin) + '.jpg', 'wb') as f:
                            f.write(pic_content)
                    else:
                        print("图片获取结果：{}", pic_res.status_code)
                except:
                    print("ASIN：{}图片保存错误".format(asin))

    time.sleep(3)

    # abs_path为项目的跟路径，相当于域
    abs_path = os.path.abspath('../')
    data_path = abs_path + "/data/goods_detail/"
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    file_name = data_path + aft + "_with_ad.xlsx"
    try:
        details_pd['pic_url'] = abs_path + r"\data\pic\\" + details_pd['asin'] + ".jpg"
        details_pd['pic_table_url'] = '<table> <img src=' + '\"' + details_pd['pic_url'] + '\"' + 'height="140" >'
    except:
        pass
    # 获取 子类目列表 返回类似稀疏矩阵 进行数据连接
    # last_pd = pd.concat([details_pd, ranks_pd], axis=1)
    # 是否删除排名相同的行
    # details_pd.drop_duplicates(subset=['category_main', 'rank_main'], inplace=True)
    details_pd.to_excel(file_name, encoding='utf-8', engine='xlsxwriter')


if __name__ == '__main__':

    data_file = r"E:\AmazonPycharm\keepa\data\asin_list_1_12101351_Home & Kitchen_0_5000.xlsx"

    """
    输入文件路径， 起始位置， 终止位置，csv文件需要包含字段‘goods_url_full’（通过goods_rank_list即关键词搜索得到的数据适用）
    其他excel文件需要包含字段‘asin’（自定义的目标产品适用），起始位置即从第几个开始 默认从头开始，终止位置即抓取到第几个链接，
    默认61 选取第一页数据60个，链接多时容易报错503 ，（亚马逊反爬机制）建议单次不超过100个链接，多次分段抓取后合并。
    """
    main(data_file, start=9000, end=9050)
