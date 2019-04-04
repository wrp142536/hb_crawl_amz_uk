from amz import get_request
import lxml.etree
from tools import list_to_str
import re
from tools import date_strft, replace_emoji
from mylog import logger


class Q_and_A:
    def __init__(self, asin, number, method='HELPFUL'):
        """
        QA部分数据采集
        :param asin: asin
        :param number: 采集的数量
        :param method: 排序方式，此处两种
        """
        self.asin = asin
        self.number = number
        self.method = method

        # if method == 'most helpful first':
        #     self.method = 'HELPFUL'
        # elif method == 'newest first':
        #     self.method = 'SUBMIT_DATE'

    def make_url(self, page):
        url = f'https://www.amazon.co.uk/ask/questions/asin' \
            f'/{self.asin}/{page}?sort={self.method}&isAnswered=true'
        return url

    def get_data(self, page):
        url = self.make_url(page)
        html = get_request(url)
        if not html:
            logger.error(f'请求{url}被拒绝')
            return
        return html

    def parse(self):
        max_page = (int(self.number) - 1) // 10 + 1
        result = []
        regx = re.compile('asked on (.*)')
        for page in range(1, max_page + 1):
            html = self.get_data(page)
            if not html:
                continue
            mytree = lxml.etree.HTML(html)
            divs = mytree.xpath(
                '//div[@class="a-section askTeaserQuestions"]/div[@class="a-fixed-left-grid a-spacing-base"]')
            for div in divs:
                q = div.xpath('.//div[@class="a-fixed-left-grid-col a-col-right"]/a/span/text()')
                a = div.xpath('.//div[@class="a-fixed-left-grid-col a-col-right"]/span/text()')
                name = div.xpath('.//div[@class="a-profile-content"]/span/text()')
                helpful = div.xpath('.//div[@class="a-fixed-left-grid-col a-col-left"]//span[@class="count"]/text()')
                # 回答者的发表日期
                # time = div.xpath('.//div[@class="a-section a-spacing-none a-spacing-top-micro"]/span/text()')
                href = div.xpath('.//div[@class="a-fixed-left-grid-col a-col-right"]/a/@href')
                if len(href) > 0:
                    html_0 = get_request('https://www.amazon.co.uk' + href[0])
                    if not html_0:
                        logger.error(f'请求https://www.amazon.co.uk{href[0]}被拒绝')
                        continue
                    # 提问者的发布日期
                    time = regx.findall(html_0)
                else:
                    time = ''
                q = list_to_str(q)
                q = replace_emoji(q)
                q = q.replace('"', "'")
                a = list_to_str(a)
                a = replace_emoji(a)

                if len(a) == 0:
                    # 此处存在【more】格式的回复，（回复字数过多时出现）
                    a = div.xpath(
                        './/div[@class="a-fixed-left-grid-col a-col-right"]//span[@class="askLongText"]/text()')
                    a = list_to_str(a)
                    a = a.replace('"', "'")
                name = list_to_str(name)
                name = replace_emoji(name)
                time = list_to_str(time).replace('· ', '')
                helpful = list_to_str(helpful)
                time = date_strft(time)
                if not time:
                    time = '1970/01/01'
                result.append((time, q, a, name, helpful))
        return result[:int(self.number)]


if __name__ == '__main__':
    q = Q_and_A('B07CGWHV2C', 10)
    a = q.parse()
    print(a)
