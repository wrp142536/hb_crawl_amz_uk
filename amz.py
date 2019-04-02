import re
import requests
from urllib import parse
import lxml.etree
from tools_mysql import *
from tools import *
from mylog import logger
from spider_rules import *
import urllib3

urllib3.disable_warnings()

lst = Listing_Rules()
sp_key = SP_by_key()
rule_by_key = Search_by_key()


def parse_robot(html):
    """
    如果被发现是机器，人工输入验证码进行验证
    :param html: 验证码页面html
    :return: 返回正常请求的页面html str
    """
    mytree = lxml.etree.HTML(html)
    amzn = mytree.xpath('//form[@action="/errors/validateCaptcha"]/input[@name="amzn"]/@value')
    amzn_r = mytree.xpath('//form[@action="/errors/validateCaptcha"]/input[@name="amzn-r"]/@value')
    img = mytree.xpath('//form[@action="/errors/validateCaptcha"]//div[@class="a-row a-text-center"]/img/@src')
    headers = random_headers()
    a = requests.get(img[0], headers=headers)
    amzn = parse.quote(amzn[0])
    amzn_r = parse.quote(amzn_r[0])
    with open('a.jpg', 'wb') as f:
        f.write(a.content)
    code = input("请输入验证码：")

    url = '''https://www.amazon.co.uk/errors/validateCaptcha?amzn={}&amzn-r={}&field-keywords={}'''.format(amzn, amzn_r,
                                                                                                           code)
    aa = requests.get(url, headers=headers)
    return aa.text


@retry(3)
def get_request(url):
    """
    对某个url进行get请求，
    :param url: url
    :return: html字符串
    """
    print('即将请求：', url)
    # headers = random_headers()
    proxies = my_proxy()
    resp = requests.get(url=url, proxies=proxies, verify=False, timeout=120)
    # resp = requests.get(url=url, headers=headers,verify=False)
    # if is_robot(resp.text):
    #     result = parse_robot(resp.text)
    # else:
    #     result = resp.text
    return resp.text
    #
    # logger.error('请求失败：{},错误原因：{})'.format(url, e))
    # return get_request(url)


def get_sell_time(asin, page):
    """
     # 根据asin取最早的评论时间-15天
    :param asin: asin
    :param page: 最早评论应该出现的页码（总页码整除10,此处不需要处理）
    :return: 如果有时间，返回时间字符串，如果没有，返回null
    """

    url = 'https://www.amazon.co.uk/product-reviews/{}?sortBy=recent&pageNumber={}'.format(asin, page)
    resp = get_request(url)
    if not resp:
        logger.error(f'请求{url}被拒绝')
        return
    mytree = lxml.etree.HTML(resp)
    time = mytree.xpath(
        '//div[@id="cm_cr-review_list"]//span[@class="a-size-base a-color-secondary review-date"]/text()')
    if len(time) > 0:
        try:
            cc = before15_days(str(time[-1]))
            return cc
        except ValueError:
            logger.error('asin:{}de 评论时间{}转换失败'.format(asin, time[-1]))
    else:
        return 'null'


def listing_uk(asin):
    """
    通过asin获取商品的详细信息
    :param asin: asin
    :return:
    """
    listing = {
        '标题': '',
        'asin': asin,
        '品牌': '',
        '大类中排名': 0,
        '大类名字': '',
        '评论数': 0,
        '星级': 0,
        '价格': '',
        '是否自营': 0,
        '上架时间': '1970/01/01',
        '图片链接': '',
        '子类排名': '[]',
    }
    # logger.info(f'开始解析{asin}')
    # 根据asin解析出商品详情
    url = "https://www.amazon.co.uk/dp/{}/?psc=1".format(asin)
    a = get_request(url)
    if not a:
        logger.error(f'请求{url}被拒绝')
        return

    # if is_robot(a):
    #     a = parse_robot(a)

    mytree = lxml.etree.HTML(a)

    # 排名情况
    for rank_rule in lst.rules_rank():
        if rank_rule[0] == 're_S':
            ranks = re.findall(rank_rule[1], a, re.S)
        elif rank_rule[0] == 'xpath':
            ranks = mytree.xpath(rank_rule[1])
        else:
            ranks = re.findall(rank_rule[1], a)
        ranks0 = re_clear_str(ranks)
        if len(ranks0) > 0:
            ranks = re.findall('(.*) in (.*)\(', ranks0)
            # 大类中排名
            listing['大类中排名'] = ranks[0][0].replace(' ', '')
            # 大类名称
            listing['大类名字'] = ranks[0][1]
            break
    if listing['大类中排名'] != 0:
        try:
            listing['大类中排名'] = int(listing['大类中排名'].replace(',', ''))
        except Exception:
            logger.error(f"大类排名格式化错误{listing['大类中排名']}")

    # 子类排名情况
    for child_rank in lst.rules_child_rank():
        if child_rank[0] == 'xpath':
            ranks1 = mytree.xpath(child_rank[1])
            if len(ranks1) > 0:
                child_rank_list1 = ranks1[0].xpath('string(.)')
                child_rank1 = list_to_str(child_rank_list1)
                child_rank2 = '[[' + str(listing['大类中排名']) + ',' + listing['大类名字'] + child_rank1 + ']]'
                tmp_999 = re.sub('#', '],[', child_rank2)
                listing['子类排名'] = re.sub(' in ', ',', tmp_999)
                # listing['子类排名'] = child_rank1
                break

    # 评论个数
    for rev in lst.rules_rev():
        if rev[0] == 'xpath':
            revs = mytree.xpath(rev[1])
            if len(revs) > 0:
                rev1_tmp = revs[0].replace('customer reviews', '').replace('customer review', '')
                listing['评论数'] = rev1_tmp
                break
        elif rev[0] == 're':
            revs = re.findall(rev[1], a)
            if len(revs) > 0:
                listing['评论数'] = revs[0]
                break
    if listing['评论数'] != 0:
        try:
            listing['评论数'] = int(listing['评论数'].replace(',', '').replace(' ', ''))
        except Exception:
            logger.error(f'评论数格式化失败：{listing["评论数"]}')

    # 评分，星级
    for score in lst.rules_scores():
        if score[0] == 're':
            tmp = re.findall(score[1], a)
            if len(tmp) > 0:
                try:
                    listing['星级'] = float(tmp[0])
                    break
                except Exception:
                    logger.error(f'星级格式化失败{tmp[0]}')

    # 价格
    for price in lst.rules_price():
        if price[0] == 're':
            price1 = re.findall(price[1], a)
            if len(price1) > 0:
                price_str = re_clear_str(price1[0])
                listing['价格'] = price_str
                break

        # elif price[0] == 'xpath':
        else:
            price1 = mytree.xpath(price[1])
            if len(price1) > 0:
                price_str = re_clear_str(price1[0])
                listing['价格'] = price_str
                break

    # 品牌
    for pp in lst.rules_pinpai():
        if pp[0] == 're':
            pinpai = re.findall(pp[1], a)
            if len(pinpai) > 0:
                pinpai = re_clear_str(pinpai[0])
                listing['品牌'] = pinpai
                break

    # 标题
    for title_rule in lst.rules_title():
        if title_rule[0] == 're_S':
            titles = re.findall(title_rule[1], a, re.S)
            titles = re_clear_str(titles)
        elif title_rule[0] == 'xpath':
            titles = mytree.xpath(title_rule[1])
        else:
            titles = re.findall(title_rule[1], a)
            titles = re_clear_str(titles)

        if len(titles) > 0:
            listing['标题'] = titles
            break

    # 上架时间（如果能找到发布的上架时间信息，如果没有，取评论时间-15天）
    for sell in lst.rules_sell_time():
        if sell[0] == 'xpath':
            sell_time = mytree.xpath(sell[1])
        # elif sell[0] == 're':
        else:
            sell_time = re.findall(sell[1], a)
        if len(sell_time) > 0:
            listing['上架时间'] = sell_time[0]
            break

    # 如果商品页没有上架时间，取评论时间
    if listing['上架时间'] == '1970/01/01':
        if listing['评论数'] != 0:
            try:
                nums = listing['评论数']
                if nums > 5000:
                    page = 500
                else:
                    page = (nums - 1) // 10 + 1
                listing['上架时间'] = get_sell_time(asin, page)
            except Exception as e:
                logger.error('asin:{}评论数转为页码失败,{}'.format(asin, e))
    else:
        try:
            # 格式化时间戳
            listing['上架时间'] = date_strft(listing['上架时间'])
        except Exception:
            logger.error(f'上架时间格式化失败：{listing["上架时间"]}')

    # 图片url
    for pic in lst.rules_pic():
        if pic[0] == 'xpath':
            pic_list = mytree.xpath(pic[1])
            if len(pic_list) > 0 and len(pic_list[0]) < 100 and len(pic_list[0]) > 0:
                listing['图片链接'] = pic_list[0]
                break
            elif len(pic_list) > 0 and len(pic_list) > 0:
                pics = re.findall('https://.*?.jpg', pic_list[0])
                if len(pics) > 0:
                    listing['图片链接'] = pics[0]

    # 自营
    for ziying in lst.rules_ziying():
        if ziying[0] == 're':
            is_ziying = re.findall(ziying[1], a)
            if len(is_ziying) > 0:
                listing['是否自营'] = 1

    return listing
    # print(listing.items())


def get_first_types():
    # 获取首次请求bsr的数据
    url = 'https://www.amazon.co.uk/gp/bestsellers'
    html_str = get_request(url)
    if not html_str:
        logger.error(f'请求{url}被拒绝')
        return
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
        # TODO 请求失败需要处理，暂时处理为跳过本次请求
        if not html_str:
            logger.error(f'请求{url}被拒绝')
            continue
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
    if not html_str:
        logger.error(f'请求{url}被拒绝')
        return
    # if is_robot(html_str):
    #     logger.error(f'访问{url}需要验证码')
    #     # TODO BUG here
    #     html_str = parse_robot(html_str)
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
        if not html_str2:
            logger.error(f'请求{url}被拒绝')
            return
        mytree2 = lxml.etree.HTML(html_str2)
        aa2 = mytree2.xpath('//ol[@id="zg-ordered-list"]//li//a//@href')
        for i in aa2:
            tmp = regx.findall(i)
            if len(tmp) == 0:
                continue
            asins.append(tmp[0])
    asins = list_quchong(asins)
    return asins[:number]


def html_search_by_key(key, page):
    """
    通过关键字查询第page页
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
    if not result:
        logger.error(f'请求{url}被拒绝')
    return result


# @run_time
def asins_by_key(key, page):
    """
    查询第page页的商品asin
    :param key: 关键字，以空格区别多个关键字
    :param page: 页码
    :return: 返回asin列表(去掉广告后)
    """
    html = html_search_by_key(key, page)
    if not html:
        return
        # if is_robot(html):
    #     html = parse_robot(html)

    mytree = lxml.etree.HTML(html)
    # 通过xpath格式化，转为字符串
    html_reg = lxml.etree.tostring(mytree, encoding=str, pretty_print=True)
    # 正则去掉注释部分
    html_reg = re.sub('<!--[\s\S]*?-->', '', html_reg)
    sp_asin = []
    asin_result = []
    # 找出广告的asin列表
    for sps in sp_key.sp():
        if sps[0] == 're_S':
            sp_asin = re.findall(sps[1], html_reg, re.S)

        elif sps[0] == 're':
            sp_asin = re.findall(sps[1], html_reg)

        elif sps[0] == 'xpath_replace':
            sps = mytree.xpath(sps[1])
            sp_asin = [k.replace('a-popover-sp-info-popover-', '') for k in sps]
        else:
            sp_asin = []
        if len(sp_asin) > 0:
            break

    # 各种规则
    for rules in rule_by_key.asin_by_key():
        if rules[0] == 'xpath':
            asin = mytree.xpath(rules[1])
            if len(asin) > 0:
                asin_result = asin
    result_asin = clear_other_list(asin_result, sp_asin)
    logger.info(f'关键字搜索{key}：总{len(asin_result)}个,广告共{len(sp_asin)}个,清洗后{len(result_asin)}个', )
    # print(f'总asin{len(asin_result)}个：', asin_result)
    # print(f'广告asin共{len(sp_asin)}个：：', sp_asin)
    # print(f'清洗后asin{len(result_asin)}个：:', result_asin)

    return result_asin


if __name__ == '__main__':
    pass
    # a=html_search_by_key('shoes nike',1)

    # tups = get_first_types()
    # all_types(tups)
    # bsr_url = 'https://www.amazon.co.uk/Best-Sellers-Health-Personal-Care-Ponytail-Holders/zgbs/drugstore/2867998031/ref=zg_bs_nav_d_4_2867997031'
    # asins = secrch_by_bsr(bsr_url, 100)
    # print(len(asins))

    # print(asins)
    a = listing_uk('0345520106')
    print(a)
    # get_sell_time('B01E8ZKD3G', 2)

    # asins_by_key('water bottle', 1)
