import random
import datetime
import re
import time

my_user_agent = [
    'Mozilla/5.0 (Android 2.2; Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; fr-FR) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it-IT) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4'
]
my_cookies = [
    "i18n-prefs=GBP; csm-hit=tb:s-DZMMM35FERRSYRZ1R3X3|1552984518345&t:1552984520459&adb:adblk_no; x-wl-uid=1MES0+GPxfZPv1GTfhYF1YmszEGNW8sm6bxtcCfzOhaa1HKK2iVXn3TDicgK3rmdKqyOClYoxr+4=; session-token=nGyoPozQeylZUiAEvztSiKcJmR/oZjz3R7h1b8STqK0BRhpMWhAqE5y6CDBM0naOpBkqNXMdz2z27v5GnYoA/a02heS9Hf8mPG9Os87TiiNpxLAjJmiakLHwnTtdonbmy4aY50KAzVSCPGTOY5lgBqzJAn6epnoopKpDKDCfuOCW1s7TrFgrPGLBLax1gRA8DLWkb+cPhQ5WLrydT8OCCcCobM097QL6HG8paOzcUc69+5nPJf9YFr6G3KY18r2GixF3FcpqDic=; ubid-acbuk=260-7690648-0227832; session-id-time=2082758401l; session-id=259-4383301-1388542",

    # "i18n-prefs=GBP; x-wl-uid=17Ix84B+2UkOgorAJhTKJO0oSAvPTCMT8ZHkUYvqAagUHZ+hg7mUsnVYGEsxBjpe9QzLNEJnxI4s=; csm-hit=tb:s-X4MR54GFD9KZHDRSFRER|1552984638059&t:1552984639891&adb:adblk_no; session-token=QDSNzohhP1fyBKKNcXK/yZoCI6wg9yOjdP1Rssm0ycXxKDyCGlzgk7u8Iiqdgs28cqHFMOK8vIimr8WzSqxbQQeFmH5+WvwpQdJmp1PJ+QrmUHECB1E/X3wPOpMmRFjT261I6OVMikZfuNGFWAMsbaRzEsaFt+km7D9ET3m4ORY2Hib6SLEMetSgfyqDDOOExBdManp6dsbnNDxyhYN0NyQ3zPNt1A1YEvhC+PIYZTpnBV4L0OVf++wWWLqU9MDmkokvn9ZVFYk=; ubid-acbuk=258-5213684-5618621; session-id-time=2082758401l; session-id=261-1644157-2686632",

    # "i18n-prefs=GBP; x-wl-uid=1GHKdZPQrwzy2iMh52zdY2/41yh3bjOqd8EZd7L4cMneOULvN+NfONqTSEWoDj7UR3UExvTPA1f0=; session-token=u1KzWQDv6VRIxHuNayl5wJ7gZ4AOilf4kCVAeFaXDfAXVj4MFfTp9pawv01O3G+GVUS28SdFGtEs+vHWPFp4/yOO3ercfOQkQGcf7TlkwFJ+5RJI8I8L0P9idDt7mdqgxpljES32wPEHsvEYTJI/HRl3NFyZOmnpZMprxrSuRHG1H4W3RwYFE4J1x2z2lMk4G7EaBbW3XGJfqgBmZxZP8ROTS6EsJMaKQcZVQpwncWiAiV+/TUfyAidp0/NUMhagymxHP8doIFo=; csm-hit=tb:s-36JYJTVG6P0SG803BV2A|1552984790512&t:1552984793118&adb:adblk_no; ubid-acbuk=260-7679557-6766441; session-id-time=2082758401l; session-id=261-7817554-8498830",

    # 'session-token="i2If0Kq9hyjxuNpCaf/XEfhb2+f66rI2QJK3AVU6bxLsf4+Yc63nvwjpdMs6YY2mFyslAYtc8jgiQXtqcq1sODwXB4J7Un5fpPdA1Unzni43bd5UeTTvGgD8Ox91aG6QMrwFB0thIZw8ux6O0kDH0Q3KBwtB+VQ95mAmlxdmbsGq3UCNza9Pznsk8wpd0SMyMsTkaqaMbsNFKFA/kC5vEA=="; amznacsleftnav-82426066-a164-33c3-8db7-5511782ee90f=1; csm-hit=tb:MZTSM3SKG7DJMTJA0TV4+s-MC5D1QRSXZ3Z866AFBTP|1552963666967&t:1552963666967&adb:adblk_no;',
    'amznacsleftnav-82426066-a164-33c3-8db7-5511782ee90f=1; session-token=yXrorBlVGcePuPSYjFRTSvaITZPAApd165NAC5U/TlH64tVKN8U6IxQ2vtW0dxzzqTCq5upD37nbEsdR7e/mbFw2Pb4tdHh1E2Bv3wUv5jkNo+X0GSNzezRg25ZK6x7RJZOhN5DhzGlxd5B2iC/r4X+sBB2VD3FYjcE/0YIXyZnxUcwmWfU1jwONrq7PLqB4;session-id-time=2082754801l; csm-hit=tb:s-6A2C32G7PH7ESM6TKC5E|1553223356860&t:1553223357476&adb:adblk_no',
]


def my_proxy():
    proxy_host = "proxy.crawlera.com"
    proxy_port = "8010"
    proxy_auth = "ddabf60de2564ab6a29bcc76a89eaafc:"  # Make sure to include ':' at the end
    proxies = {"https": "https://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
               "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)}
    return proxies


def run_time(func):
    # 此装饰器，用来统计
    def warps(*args, **kwargs):
        start_time = time.time()
        aa = func(*args, **kwargs)

        print(time.time() - start_time)
        return aa

    return warps


def base_64_pic():
    import base64
    a = '''data:image/jpeg;base64,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
    '''
    b = a.replace('data:image/jpeg;base64,', '')
    c = base64.b64decode(b)
    with open('a.jpg', 'wb') as f:
        f.write(c)


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


def before15_days(strs):
    """
    把某个时间字符串推前15天
    :param strs: 时间字符串，格式为 【20 March 2019】
    :return:
    """
    datetime.timedelta(days=-15)
    dd = datetime.datetime.strptime(strs, '%d %B %Y') + datetime.timedelta(days=-15)
    cc = datetime.datetime.strftime(dd, '%Y/%m/%d')
    return cc


def return_list0_to_str(list0):
    if len(list0) > 0:
        return list0[0]
    else:
        return ''


def date_strft(date_str):
    date_str = date_str.replace(".", '')
    try:
        dd = datetime.datetime.strptime(date_str, '%d %b %Y')
    except Exception:
        pass
    try:
        dd = datetime.datetime.strptime(date_str, '%d %B %Y')
    except Exception:
        pass
    # 这里对dd不做处理，在外部调用时方便捕获异常
    cc = datetime.datetime.strftime(dd, '%Y/%m/%d')
    return cc


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

    # for i in list0:
    #     if i in list1:
    #         list0.remove(i)
    #         print('删除',i)
    # return list0
    li = [k for k in list0 if k not in list1]
    return li


def list_to_str(list_a):
    """
    把列表转化为字符串，并去除换行符和首位空格
    :param list_a:
    :return:
    """
    a = ''.join(list_a)
    a = re_clear_str(a)
    return a


# @run_time
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


def list_quchong(list0):
    """
    列表去重，保持元素原先顺序
    :param list0: 原数据，列表格式
    :return: 去重后的列表，保留先出现的元素
    """
    new_li = list(set(list0))
    new_li.sort(key=list0.index)
    return new_li


class Singleton:
    """
    单例模式
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance


def replace_emoji(strs):
    EMOJI0 = re.compile('\n|\r|\t')
    EMOJI1 = re.compile(u'[\U00010000-\U0010ffff]')
    EMOJI2 = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    strs = EMOJI0.sub('', strs)
    strs = EMOJI1.sub('', strs)
    strs = EMOJI2.sub('', strs)
    return strs


def retry(n):
    """
    此装饰器用来重试nci
    :param n: int，重试次数
    :return:
    """

    def times(func):
        def wraps(*args, **kwargs):
            for _ in range(n):
                try:
                    a = func(*args, **kwargs)
                    return a
                except Exception:
                    pass

        return wraps

    return times
