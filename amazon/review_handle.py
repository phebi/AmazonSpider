# 对评论详情进行词频分布统计
import pandas as pd
from pyecharts import options as opts
import datetime, time, re

word_filter = ['in', 'a', 'and', 'i', 'm', 'the', 'very',
               'it', 'for', 'is', 'on', 'is', 'was', 'so',
               'to', 'at', 'am', 'five', 'stars', 'this',
               'my', 'but', 'of', 'as', 'with', 'they',
               'are', 'you', 'these', 'have', 'good', 'great',
               'not', 'that', 'be']


def words_handle(text, *args):
    return text


def get_counts(text, *args):
    # 输入文字段 先进行替换 然后 分词
    words_filter = word_filter + ['dog', 'bed', 'would']
    import re
    txt = text.lower()
    step = re.compile(r'[\"~!@#$%^&*()_+{}|\[\]:;<>?.,，]')  # 替换特殊字符
    txt = re.sub(step, ' ', txt)
    words_row = txt.split()  # 分词
    row_counts = {}
    result_counts = {}
    for word in words_row:
        if word not in words_filter:
            row_counts[word] = row_counts.get(word, 0)+1
    for (key, value) in row_counts.items():
        if value > 2:
            result_counts[key] = value
    dict_items = list(result_counts.items())  # 输出words value 的字典
    dict_items.sort(key=lambda x: x[1], reverse=True)  # 把字典按照数值排序
    return dict_items


def get_word_pic(items):
    from pyecharts.globals import SymbolType
    from pyecharts.charts import WordCloud

    my_wd = WordCloud()
    my_wd.add('title', items, word_size_range=[10, 100], shape=SymbolType.DIAMOND)
    my_wd.set_global_opts(
        title_opts=opts.TitleOpts(title="词频分布示意图"),
        toolbox_opts=opts.ToolboxOpts(),
        tooltip_opts=opts.TooltipOpts()
    )

    return my_wd


def main(file_path):
    data = pd.read_excel(file_path)
    data_filter = data['review_body'][data['review_body'].notnull()][data['review_star'] <= 3]
    text = " ".join(data_filter)
    items = get_counts(text)

    aft = datetime.datetime.now().strftime('%m%d%H%M')
    get_word_pic(items).render(r"../data/goods_review/词频分布_" + aft + '.html')
    pd.DataFrame(items).to_csv(r"../data/goods_review/词频分布_" + aft + '.csv')
    print(items)
    time.sleep(3)


def check(file_path):
    data = pd.read_excel(file_path)
    data_filter = data['review_body'][data['review_body'].notnull()][data['review_star'] <= 3]
    while True:
        #  列出包含最高频的几个词语的评论
        word_list = (input("请输入要查询的词语，以逗号隔开，退出请输入quit:", ))
        if word_list == ('quit'):
            break
        res_list = list(i.strip() for i in word_list.split(',') if i)
        for word in res_list:
            print(word)
            num = 1
            for each in data_filter.tolist():
                patt = re.compile(r'\b' + word + r'\b', re.S)
                if re.search(patt, each):
                    print("{:*^20}".format(word + ":" + str(num)))
                    print(each.replace(word, '\033[1;31;40m' + word + '\033[0m'))
                    num += 1


if __name__ == '__main__':

    # 评价词频分析 输入为 评价详情文件
    file_path = '../data/goods_review/reviews-12091259.xlsx'
    # main 用来绘制词频分布图
    main(file_path)
    # check 检查关键词所在的句段
    check(file_path)


