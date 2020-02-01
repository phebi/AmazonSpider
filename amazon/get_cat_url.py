import pandas as pd
import requests
from lxml import etree
import datetime, time, random
from queue import Queue
import threading
import re
import numpy as np
import pymysql


class BSE:
    headers = {

        'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0);'
    }

    # 添加代理 应添加https生效 实际操作中会用到全局VPN
    proxies = {
        "http": "http://49.86.181.43:9999",
    }

    s = requests.Session()
    s.headers.update(headers)
    url_base = "https://www.amazon.com"
    s.get(url=url_base, headers=headers, verify=False)

    raw_queue = Queue()
    fir_queue = Queue()
    sec_queue = Queue()
    thr_queue = Queue()
    thr_list = []
    last_list = []

    def del_ref(self, url):
        try:
            url = url.split('/ref')[0]
        except:
            pass
        return url

    # def get_raw(self):
    #
    #     raw_base_url = r'https://www.amazon.com/Best-Sellers/zgbs/'
    #     raw_res = self.s.get(url=raw_base_url, headers=self.headers, proxies=self.proxies)
    #     raw_html = etree.HTML(raw_res.text)
    #
    #     for each in raw_html.xpath('//*[@id="zg_browseRoot"]/ul/li')[-5:-4]:
    #         title = each.xpath("./a/text()")[0]
    #         url = each.xpath("./a/@href")[0]
    #         url = self.del_ref(url)
    #         print(title, '一级类目')
    #         print(url)
    #         self.raw_queue.put((title, url))
    #         print('raw_list:', self.raw_queue.qsize())

    def get_raw(self, root_url):

        raw_res = self.s.get(url=root_url, headers=self.headers, proxies=self.proxies)
        raw_html = etree.HTML(raw_res.text)

        try:
            title = raw_html.xpath("//span[@class='category']/text()")[0]
        except:
            title = None
        self.raw_queue.put((title, root_url))
        print('raw_list:', self.raw_queue.qsize())

    def get_fir(self, abs_title, abs_url):

        abs_res = self.s.get(url=abs_url, headers=self.headers, proxies=self.proxies)
        abs_html = etree.HTML(abs_res.text)

        for each in abs_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/li'):
            fir_url = each.xpath("./a/@href")[0]
            fir_url = self.del_ref(fir_url)
            fir_title = each.xpath("./a/text()")[0]
            print(fir_title, '二级类目')
            print(fir_url, "")
            self.fir_queue.put((abs_title, abs_url, fir_title, fir_url))
            print('二级类目数据', self.fir_queue.qsize())

    def get_sec(self, abs_title, abs_url, fir_title, fir_url):

        inner_res = self.s.get(url=fir_url, headers=self.headers, proxies=self.proxies)
        inner_html = etree.HTML(inner_res.text)

        if inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/li/a'):
            for each in inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/li/a'):
                sec_url = each.xpath("./@href")[0]
                sec_url = self.del_ref(sec_url)
                sec_title = each.xpath("./text()")[0]
                print("get_sec")
                print(sec_title, "三级类目")
                print(sec_url)
                self.sec_queue.put((abs_title, abs_url, fir_title, fir_url, sec_title, sec_url))
        else:
            print("三级类目分支")
            self.last_list.append((abs_title, abs_url, fir_title, fir_url))
            print(len(self.last_list), self.last_list[-1][-2:])

    def get_thr(self, abs_title, abs_url, fir_title, fir_url, sec_title, sec_url):

        time.sleep(random.random())
        inner_res = self.s.get(url=sec_url, headers=self.headers, proxies=self.proxies)
        inner_html = etree.HTML(inner_res.text)

        if inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/ul/li/a'):

            for each in inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/ul/li/a'):
                thr_url = each.xpath("./@href")[0]
                thr_url = self.del_ref(thr_url)
                thr_title = each.xpath("./text()")[0]
                print("get_thr")
                print(thr_title, "四级类目")
                print(thr_url)
                self.thr_queue.put((abs_title, abs_url, fir_title, fir_url, sec_title, sec_url, thr_title, thr_url))
                self.last_list.append((abs_title, abs_url, fir_title, fir_url, sec_title, sec_url, thr_title, thr_url))
                print(len(self.last_list), self.last_list[-1][-2:])

        else:
            print("四级类目分支")
            self.last_list.append((abs_title, abs_url, fir_title, fir_url, sec_title, sec_url))
            print(len(self.last_list), self.last_list[-1][-2:])

    def get_last(self, abs_title, abs_url, fir_title, fir_url, sec_title, sec_url, thr_title, thr_url):
        inner_res = self.s.get(url=thr_url, headers=self.headers, proxies=self.proxies)
        inner_html = etree.HTML(inner_res.text)

        if inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/ul/ul/li/a'):

            for each in inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/ul//ul/li/a'):
                last_url = each.xpath("./@href")[0]
                last_url = self.del_ref(last_url)
                last_title = each.xpath("./text()")[0]
                print("get_last")
                print(last_title, "子类目")
                print(last_url)
                self.last_list.append((abs_title, abs_url, fir_title, fir_url, sec_title, sec_url, thr_title, thr_url,
                                       last_title, last_url))
                print(len(self.last_list), self.last_list[-1][-2:])

    def run(self, root_url):
        self.get_raw(root_url=root_url)
        print(self.raw_queue.qsize())

        while True:

            fir_thread_list = [threading.Thread(target=self.get_fir, args=(self.raw_queue.get())) for i in range(3)
                        if not self.raw_queue.empty()]

            for each in fir_thread_list:
                each.start()
            for each in fir_thread_list:
                each.join()
            time.sleep(0.5)

            sec_thread_list = [threading.Thread(target=self.get_sec, args=(self.fir_queue.get())) for i in range(8)
                        if not self.fir_queue.empty()]

            for each in sec_thread_list:
                each.start()
            for each in sec_thread_list:
                each.join()
            time.sleep(random.random())

            thr_thread_list = [threading.Thread(target=self.get_thr, args=(self.sec_queue.get())) for i in range(20)
                        if not self.sec_queue.empty()]

            for each in thr_thread_list:
                each.start()
            for each in thr_thread_list:
                each.join()
            time.sleep(random.random())

            final_thread_list = [threading.Thread(target=self.get_last, args=(self.thr_queue.get())) for i in range(20)
                          if not self.thr_queue.empty()]

            for each in final_thread_list:
                each.start()
            for each in final_thread_list:
                each.join()
            time.sleep(random.random())

            if self.fir_queue.empty() and self.sec_queue.empty() and self.raw_queue.empty() and self.thr_queue.empty():
                break

        try:
            last_data = pd.DataFrame(self.last_list, columns=['类目名称', '类目链接', '二级类目', '二级类目链接', '三级类目',
                                                              '三级类目链接', '四级类目', '四级类目链接', '子类目', '子类目链接'])
            last_data.sort_values(by=['类目名称', '二级类目', '三级类目', '四级类目', '子类目'], ascending=True, inplace=True)
        except:
            last_data = pd.DataFrame(self.last_list)
        return last_data


def main(root_url):
    bse = BSE()
    aft = "_" + datetime.datetime.now().strftime('%m%d%H%M')

    # root_url = 'https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/'
    data = bse.run(root_url)

    # 化简 去掉各列中重复的值 只保留出现的第一个 耗时操作
    # for each_column in data.columns:
    #     for each in pd.DataFrame(data[each_column]).index:
    #         if each not in pd.DataFrame(data[each_column]).drop_duplicates().index:
    #             data[each_column][each] = None

    # 保留每一行的最后一个链接，即最小类目\最大分类数的链接

    last_list = []
    for each in data.index:
        each_list = data.iloc[each].to_list()
        while True:
            if None in each_list:
                each_list.remove(None)
            if None not in each_list:
                last_list.append(each_list[-2:])
                break
    print(last_list)

    # 文件名称修改
    patt = 'Best-Sellers([^/]*)/'
    try:
        cate = re.search(patt, root_url).groups()[0]
        cate = cate.replace('-', '_')
    except:
        cate = ''
    print("类目{}下的 best_seller榜链接数量: {}".format(cate, len(last_list)))
    file_name = r'../data/category/amazon_category_' + cate + aft + '.xlsx'
    data.to_excel(file_name, encoding='utf-8', engine='xlsxwriter')
    pd_last = pd.DataFrame(last_list)
    try:
        pd_last.columns = ['类目名称', '类目链接']
        pd_last.drop_duplicates(subset=['类目链接'], inplace=True)
        pd_last.reset_index(drop=True)
    except:
        pass
    pd_last.to_excel('../data/category/' + cate + aft + '_类目简化.xlsx',
                                     encoding='utf-8', engine='xlsxwriter')


if __name__ == '__main__':

    # 输入： 根类目的链接
    # 输出： 该类目的best_seller链接，各个层级的链接存放在 data/category/amazon_category_+类目名称的Excel表格中，
    # 输出： 简化版，仅保留最后一个层级的链接文件保存在相同目录下，类目名称+类目简化的Excel表格中。

    root_url = 'https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/'
    main(root_url)
