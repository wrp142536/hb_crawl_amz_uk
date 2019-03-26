import requests
import re
from urllib import parse
import lxml.etree
from tools import *
import random
import time
import datetime
from mylog import My_log

logger = My_log('lyl').get_logger()


def before15_days(strs):
    """
    把某个时间字符串推前15天
    :param strs: 时间字符串，格式为 【20 March 2019】
    :return:
    """
    datetime.timedelta(days=-15)
    dd = datetime.datetime.strptime(strs, '%d %B %Y') + datetime.timedelta(days=-15)
    cc = datetime.datetime.strftime(dd, '%d %B %Y')
    return cc


def conn_mysql():
    """
    数据库链接
    :return: 数据库链接对象
    """
    import pymysql
    mysql_ip = '127.0.0.1'
    mysql_database = 'test'
    mysql_password = 'liuyalong'
    mysql_username = 'root'
    mysql_db = pymysql.connect(mysql_ip, mysql_username, mysql_password, mysql_database, use_unicode=True,
                               charset='utf8')
    return mysql_db


mysql_db = conn_mysql()


def update_into_mysql(url):
    """
    更新bsr_uk表，对访问过的url的visted字段设置为1
    :param url: url地址
    :return:
    """
    curs = mysql_db.cursor()
    sql = '''UPDATE bsr_uk set visted=1 WHERE url='{}';'''.format(url)
    try:
        curs.execute(sql)
        mysql_db.commit()
    except Exception as e:
        print('update_into_mysql', sql, e)


def write_into_mysql(table, data, deepth, visted):
    """
    把数据写入mysql
    :param table: 表名
    :param data: 要写入的数据，格式：（'',''）
    :param deepth: 当前数据的深度
    :param visted: 是否被访问过，理论上应该默认为0
    :return:
    """
    curs = mysql_db.cursor()
    sql = '''insert into {} values ("{}","{}",{},{})'''.format(table, data[0], data[1], deepth, visted)
    try:
        curs.execute(sql)
        mysql_db.commit()
    except Exception as e:
        print(data, '------', sql, e)
    # curs.close()
    # mysql_db.close()


def bool_url_in_mysql(url):
    """
    查询某个url是否在数据库表中存在
    :param url: url
    :return: bool值
    """
    curs = mysql_db.cursor()
    sql = '''SELECT * from bsr_uk where url='{}';'''.format(url)
    try:
        curs.execute(sql)
        data = curs.fetchall()
        if len(data) > 0:
            return True
        else:
            return False
    except Exception as e:
        print(sql, e)


def select_mysql(deepth):
    """
    查询数据库指定深度且没有访问过的url
    :param deepth: 深度
    :return:url元组，格式（（），（））
    """
    curs = mysql_db.cursor()
    sql = '''select url from bsr_uk where deepth={} and visted=0'''.format(deepth)
    try:
        curs.execute(sql)
        data = curs.fetchall()
        return data
    except Exception as e:
        print(sql, e)


def random_headers():
    """
    制造随机请求头，减少爬虫被封几率，此请求头针对amazon
    :return: 请求头字典
    """
    headers = {
        # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'accept-encoding': 'gzip, deflate, br',
        # 'accept-language': 'zh-CN,zh;q=0.8',
        # 'cache-control': 'max-age=0',
        # 'cookie': '%s' % random.choice(my_cookies),
        # 'upgrade-insecure-requests': '1',
        'user-agent': '%s' % random.choice(my_user_agent),
        # 'user-agent':,

    }
    return headers


def get_request(url):
    """
    对某个url进行get请求，
    :param url: url
    :return: html字符串
    """
    headers = random_headers()
    try:
        resp = requests.get(url=url, headers=headers)
        print(resp.text)
        return resp.text
    except Exception as e:
        print(e)
        print('请求失败：', url)
        return 'failed'


def re_clear_str(args):
    """
    清洗字符串，去掉换行符，开头和结尾的空格
    :param args: 需要清洗的字符串
    :return: 清洗后的字符串
    """
    if isinstance(args, list):
        strs = ''.join(args)
    elif isinstance(args, str):
        strs = args
    else:
        print('re_clear_str函数传入参数格式不对')

    # 换行符剔除
    tmp = re.sub('\n|\r|\t|\f', '', strs)
    tmp = re.sub('\xa0', ' ', tmp)
    # 剔除首尾空格
    tmp = tmp.strip()
    return tmp


def clear_other_list(list0, list1):
    """
    删除第一个列表中在第二个列表里的数据
    :param list0: 总数据列表
    :param list1: 需要剔除的元素列表
    :return: 清洗后的列表
    """
    for i in list0:
        if i in list1:
            list0.remove(i)
    return list0


def list_to_str(list_a):
    """
    把列表转化为字符串，并去除换行符和首位空格
    :param list_a:
    :return:
    """
    a = ''.join(list_a)
    a = re_clear_str(a)
    return a


def get_sell_time(asin, page):
    """
     # 根据asin取最早的评论时间-15天
    :param asin: asin
    :param page: 最早评论应该出现的页码（总页码整除10,此处不需要处理）
    :return: 如果有时间，返回时间字符串，如果没有，返回null
    """

    url = 'https://www.amazon.co.uk/product-reviews/{}?sortBy=recent&pageNumber={}'.format(asin, page)
    resp = get_request(url)
    mytree = lxml.etree.HTML(resp)
    time = mytree.xpath(
        '//div[@id="cm_cr-review_list"]//span[@class="a-size-base a-color-secondary review-date"]/text()')
    if len(time) > 0:
        cc = before15_days(str(time[-1]))
        return cc
    else:
        return 'null'


def listing_uk(asin):
    """
    通过asin获取商品的详细信息
    :param asin: asin
    :return:
    """
    print('开始解析asin：', asin)
    print()
    listing = {
        '标题': 'null',
        'asin': asin,
        '品牌': 'null',
        '大类中排名': 'null',
        '大类名字': 'null',
        '评论数': 'null',
        '星级': 'null',
        '价格': 'null',
        '是否自营': 'null',
        '上架时间': 'null',
        '图片链接': 'null',
        '国家': '英国',
        '子类排名': 'null',
    }
    # 根据asin解析出商品详情
    a = get_request("https://www.amazon.co.uk/dp/{}/?psc=1".format(asin))
    # print(a)
    # from strs import a
    mytree = lxml.etree.HTML(a)
    # 排名情况
    rank_list1 = mytree.xpath('//li[@id="SalesRank"]/text()')
    rank_list2 = mytree.xpath('//tr[@id="SalesRank"]/td[@class="value"]/text()')
    rank1 = list_to_str(rank_list1)
    rank2 = list_to_str(rank_list2)
    if len(rank1) > 0:
        ranks = re.findall('(.*) in (.*)\(', rank1)
        # 大类中排名
        listing['大类中排名'] = ranks[0][0].replace(' ', '')
        # 大类名称
        listing['大类名字'] = ranks[0][1]
    elif len(rank2) > 0:
        ranks = re.findall('(.*) in (.*)\(', rank2)
        # 大类中排名
        listing['大类中排名'] = ranks[0][0].replace(' ', '')
        # 大类名称
        listing['大类名字'] = ranks[0][1]

    # 子类排名情况
    child_rank_list1 = mytree.xpath('//*[@id="SalesRank"]//ul')
    if len(child_rank_list1) > 0:
        child_rank_list1 = child_rank_list1[0].xpath('string(.)')
        child_rank1 = list_to_str(child_rank_list1)
        listing['子类排名'] = child_rank1

    # 评论个数
    rev1 = mytree.xpath('//span[@id="acrCustomerReviewText"]//text()')
    rev2 = re.findall('">([\d, ]+)customer reviews', a)
    if len(rev1) > 0:
        rev1_tmp = rev1[0].replace('customer reviews', '').replace('customer review', '')
        listing['评论数'] = rev1_tmp
        # print('评论1')
    elif len(rev2) > 0:
        # print('评论2')
        listing['评论数'] = rev2[0]

    # 评分，星级
    score = re.findall('class="reviewCountTextLinkedHistogram noUnderline" title="(.*) out of 5 stars', a)
    score2 = re.findall('>([\d. ]+)out of 5 stars', a)
    if len(score) > 0:
        listing['星级'] = score[0]
    elif len(score2) > 0:
        listing['星级'] = score2[0]

    # 价格
    price1 = re.findall('class="a-size-medium a-color-price">(.*)</span>', a)
    price2 = re.findall('class="a-color-price a-text-bold">(.*)</span>', a)
    price3 = mytree.xpath('//td[@class="a-color-price a-size-medium a-align-bottom"]/text()')
    price4 = mytree.xpath('//button[@class="av-button av-button--default js-purchase-button dv-record-reftag"]/text()')

    if len(price1) > 0:
        listing['价格'] = price1[0]
    elif len(price2) > 0:
        listing['价格'] = price2[0]
    elif len(price3) > 0:
        listing['价格'] = price3[0]
    elif len(price4) > 0:
        listing['价格'] = price4[3]

    # 品牌01
    pinpai1 = re.findall('id="bylineInfo".*>+(.*)</a>', a)
    pinpai2 = re.findall('id="gc-brand-name-link".*>+(.*)</a>', a)

    if len(pinpai1) > 0:
        listing['品牌'] = pinpai1[0]
    elif len(pinpai2) > 0:
        listing['品牌'] = pinpai2[0]

    # 标题
    titles1 = re.findall('<span id="productTitle" class="a-size-large">(.*?)</span>?', a, re.S)
    titles1 = re_clear_str(titles1)
    titles2 = mytree.xpath('//span[@id="btAsinTitle"]/text()')
    titles3 = mytree.xpath('//h1[@data-automation-id="title"]/text()')

    if len(titles1) > 0:
        listing['标题'] = titles1
    elif len(titles2) > 0:
        listing['标题'] = titles2[0]
    elif len(titles3) > 0:
        listing['标题'] = titles3[0]

    # 上架时间（如果能找到发布的上架时间信息，如果没有，取评论时间-15天）
    # sell_time1 = re.findall('<td class="label">Date First Available</td>', a)
    sell_time2 = mytree.xpath('//tr[@class="date-first-available"]/td[@class="value"]/text()')
    sell_time3 = re.findall('<li><b> Date first available at Amazon.co.uk:</b> (.*)</li>', a)

    # if len(sell_time1) > 0:
    #     listing['上架时间'] = sell_time1[0]
    if len(sell_time2) > 0:
        listing['上架时间'] = sell_time2[0]
    elif len(sell_time3) > 0:
        listing['上架时间'] = sell_time3[0]

    # 如果商品页没有上架时间，取评论时间
    if listing['上架时间'] == 'null':
        if listing['评论数'] != 'null':
            try:
                nums = int(listing['评论数'].replace(',', '').replace(' ', ''))
                if nums > 5000:
                    page = 500
                else:
                    page = nums // 10 + 1
                listing['上架时间'] = get_sell_time(asin, page)
            except Exception as e:
                print('评论数转为页码失败', e)

    # 图片url
    pic_list = mytree.xpath('//div[@class="imgTagWrapper"]/img/@src')
    pic_list2 = mytree.xpath('//div[@class="av-fallback-packshot"]/img/@src')
    pic_list00 = mytree.xpath('//div[@class="imgTagWrapper"]/img/@data-old-hires')
    pic_list01 = mytree.xpath('//div[@class="imgTagWrapper"]/img/@data-a-dynamic-image')

    if len(pic_list) > 0 and len(pic_list[0]) < 100:
        listing['图片链接'] = pic_list[0]
    elif len(pic_list2) > 0 and len(pic_list2[0]) < 100:
        listing['图片链接'] = pic_list2[0]
    else:
        if len(pic_list00) > 0 and len(pic_list00[0]) > 0:
            listing['图片链接'] = pic_list00[0]
        elif len(pic_list01) > 0 and len(pic_list01[0]) > 0:
            l = re.findall('https://.*?.jpg', pic_list01[0])
            if len(l) > 0:
                listing['图片链接'] = l[0]

    # 自营(如果为空，表示非自营，如果有，有可能是自营)
    is_ziying = re.findall('sold by Amazon.', a)
    if len(is_ziying) > 0:
        listing['是否自营'] = 'yes'
    print(listing.items())


def get_first_types():
    # 获取首次请求bsr的数据
    url = 'https://www.amazon.co.uk/gp/bestsellers'
    html_str = get_request(url)
    a = get_bsr_list(html_str)
    for i in a:
        write_into_mysql('bsr_uk', i, 1, 0)
    return a


def get_bsr_list(html_str):
    """
    提取类目的链接
    :param html_str: html_str
    :return: 返回集合，格式：{（name,url），（）}
    """

    # resp = requests.get(url=url, headers=headers)
    # regx = re.compile(' <ul id="zg_browseRoot"><li><a href=(.*?)>(.*?)</a></li>')
    # aa = regx.findall(bst)
    result = set()
    mytree = lxml.etree.HTML(html_str)
    aa = mytree.xpath("//ul[@id='zg_browseRoot']//li")
    for i in aa:
        try:
            name = i.xpath('./a/text()')[0]
            href = i.xpath('./a/@href')[0]
            href = re.findall('(.*)/ref=', href)[0]
            result.add((name, href))
        except IndexError:
            continue
    return result


def all_types(deep):
    """
    获取某个深度的bsr列表地址，数据存入mysql
    :param deep:
    :return:
    """
    # 获取深度为deep的未请求url,返回值元组（（type,url））
    datas_select = select_mysql(deep)
    datas_select = [x[0] for x in datas_select]

    for url in datas_select:
        html_str = get_request(url)
        found_data = get_bsr_list(html_str)

        for data in found_data:
            if bool_url_in_mysql(data[1]):
                continue
            else:
                write_into_mysql('bsr_uk', data, deep + 1, 0)

        update_into_mysql(url)


def secrch_by_bsr(url, number):
    """
    根据bsr排名爬取数据，返回指定书目的asin
    :param url: 类目的url
    :param number: 获取多少个asin
    :return: 列表格式，【asin,asin】
    """
    # 按照bsr采集asin
    html_str = get_request(url)
    number = int(number)
    mytree = lxml.etree.HTML(html_str)
    aa = mytree.xpath('//ol[@id="zg-ordered-list"]//li//a[@class="a-link-normal"]//@href')
    # bb=
    regx = re.compile('dp/(.*?)/ref')
    asins = []
    for i in aa:
        tmp = regx.findall(i)
        if len(tmp) == 0:
            continue
        asins.append(tmp[0])

    if number > 50:
        url2 = url + '?pg=2'
        html_str2 = get_request(url2)
        mytree2 = lxml.etree.HTML(html_str2)
        aa2 = mytree2.xpath('//ol[@id="zg-ordered-list"]//li//a//@href')
        for i in aa2:
            tmp = regx.findall(i)
            if len(tmp) == 0:
                continue
            asins.append(tmp[0])
    asins = list(set(asins))
    return asins[:number + 1]


def search_by_key(key, page):
    """
    查询第page页的商品信息
    :param key: 关键字，以空格区别多个关键字
    :param page: 页码
    :return: 返回第page页的html字符串
    """

    tmp_list = str(key).split(' ')
    url_key = ''
    for t in tmp_list:
        if t == '':
            continue
        else:
            # 中文编码为ASCII码
            k = parse.quote(t)
            url_key += k
            url_key += '+'
    # 去掉最后的+
    url_key = url_key[:-1]
    # 请求，构造url
    url = 'https://www.amazon.co.uk/s?k={}&page={}'.format(url_key, page)
    result = get_request(url)
    print('即将请求：', url)

    return result


def is_robot(strs):
    """
    验证码认证是否是机器人
    :param strs:
    :return:
    """
    a = re.findall("Sorry, we just need to make sure you're not a robot", strs)
    if len(a) > 0:
        print('卧槽！爬虫被发现了！')
        return True
    else:
        return False


def asins_by_key(key, page):
    """
    查询第page页的商品asin
    :param key: 关键字，以空格区别多个关键字
    :param page: 页码
    :return: 返回asin(去掉广告)
    """
    # TODO 根据page请求数量，调用search_by_key函数
    html = search_by_key(key, page)
    if is_robot(html):
        return []

    mytree = lxml.etree.HTML(html)
    # 通过xpath格式化，转为字符串，以供正则使用
    html_reg = lxml.etree.tostring(mytree, encoding=str, pretty_print=True)
    print(html_reg)
    sp_asin = find_sp_asins(html_reg)
    if len(sp_asin) > 0:
        print('广告1', sp_asin)
    else:
        sp_asin = find_sp_asins2(mytree)
        print('广告2', sp_asin)
    # 各种规则
    asin1 = mytree.xpath('//div[contains(@data-cel-widget,"search_result_")]/@data-asin')

    if len(asin1) > 19:
        asin = asin1
        print('解析规则：1')
    else:
        asin2 = mytree.xpath('//div[@class="s-result-list sg-row"]//div/@data-asin')
        if len(asin2) > 19:
            asin = asin2
            print('解析规则：2')
        else:
            asin3 = mytree.xpath('//li[contains(@id,"result_")]//@data-asin')
            asin = asin3
            print('解析规则：3')
    result_asin = clear_other_list(asin, sp_asin)
    return result_asin


def max_len_lists(*args):
    """
    返回几个列表元素最多的列表
    :param args:
    :return:
    """
    mydict = {}
    for i in range(len(args)):
        mydict[i] = len(args[i])
    a = sorted(mydict.items(), key=lambda x: x[1], reverse=True)
    return args[a[0][0]]


def find_sp_asins(html):
    # TODO  <!--[\s\S]*?--> 注释内容会被找到,应需要剔除，但不影响结果
    html = re.sub('<!--[\s\S]*?-->', '', html)

    # 找出广告的asin
    # # ads = re.findall('These are ads', html)
    # if len(ads) < 1:
    #     return []
    # else:
    #     print('预计广告数量：', len(ads))
    regex_asin_list = re.compile('<div.*?="a-popover-sponsored-header-(.*?)"><span>These are ads')
    aa = regex_asin_list.findall(html)

    if len(aa) > 0:
        return aa
    else:
        bb = re.findall('<div.*?="a-popover-sp-info-popover-(.*?)"><span>These are ads', html, re.S)
        return bb


def find_sp_asins2(mytree):
    sps = mytree.xpath("//div[contains(@id,'a-popover-sp-info-popover-')]/@id")
    sp = [k.replace('a-popover-sp-info-popover-', '') for k in sps]

    if len(sp) > 0:
        return sp
    else:
        print('find_sp_asins2未匹配到广告')
        return []


if __name__ == '__main__':
    pass
    # a=search_by_key('shoes nike',1)
    # 总数据存储在bsr_types_list中
    # tups = get_first_types()
    # all_types(tups)
    # bsr_url = 'https://www.amazon.co.uk/Best-Sellers-Computers-Accessories-Flatbed-Scanners/zgbs/computers/430592031'
    # asins = secrch_by_bsr(bsr_url, 100)
    # print(len(asins))
    # print(asins)
    listing_uk('B01DZ5HR66')
    # get_sell_time('B01E8ZKD3G', 2)

    # all_types()
    # asins = asins_by_key('球', 1)
    # print(asins)
    # print('原', len(asins), '去重', len(set(asins)))

    # mysql_db.close()
