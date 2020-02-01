from keepa_request import get_varies
import pandas as pd
import datetime
import pymysql


def stock_handle(file):
    stock_list = []
    # data = pd.read_excel(file)
    # asin_list = data['asin'].tolist()
    # asin_list = ['B07X5HPNXV']
    # 目标产品  B07VLYBRHT
    # asin_list = ['B07VZD6TK7', 'B07X92TMYR', 'B07RX8HVCK', 'B07K6R2Q5G']
    # bedsure圣诞
    asin_list = ['B07X38BBZH', 'B01KLPXZX2', 'B07X97HQ6W', 'B07X3FMNK9']
    # 一次性
    # asin_list = ['B081DZXJ2S', 'B07BGVP5XB', 'B07YBLF5J9']
    # asin_list =
    for asin in asin_list:
        stock_list.extend(get_varies(asin.strip()))
        print(stock_list)

    aft = "./data/stock_" + datetime.datetime.now().strftime("%m%d%H%M")
    data_pd = pd.DataFrame(stock_list, columns=['parent_asin', 'asin', 'style', 'stock', 'model'])
    data_pd.drop_duplicates(subset=['asin'], inplace=True)
    data_pd.to_excel(aft + '.xlsx')

    conn = pymysql.connect(host='localhost', port=3306, db='amazon_test', user='root', passwd='1118')
    cs = conn.cursor()
    for each in data_pd.values.tolist():
        parent_asin, asin, style, stock, model = each
        stock_date = datetime.datetime.now()
        insert_sql = "INSERT INTO amazon_test.amazon_stock(parent_asin, asin, style, stock, model, stock_date) VALUES" \
                     "(%s,%s,%s,%s,%s,%s)"

        count = cs.execute(insert_sql, (parent_asin, asin, style, stock, model, stock_date))
        print(count)
        try:
            conn.commit()
        except:
            conn.rollback()

    cs.close()


if __name__ == '__main__':
    file = r'E:\爬虫pycharm\data\goods_detail\目标产品.xlsx'
    stock_handle(file)