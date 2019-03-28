from amz import get_request
import lxml.etree
from tools import list_to_str


class Q_and_A:
    def __init__(self, asin, number, method='most helpful first'):
        """
        QA部分数据采集
        :param asin: asin
        :param number: 采集的数量
        :param method: 排序方式，此处两种
        """
        self.asin = asin
        self.number = number
        if method == 'most helpful first':
            self.method = 'HELPFUL'
        elif method == 'newest first':
            self.method = 'SUBMIT_DATE'

    def make_url(self, page):
        url = f'https://www.amazon.co.uk/ask/questions/asin' \
            f'/{self.asin}/{page}?sort={self.method}&isAnswered=true'
        return url

    def get_data(self, page):
        html = get_request(self.make_url(page))
        return html

    def parse(self):
        max_page = (int(self.number) - 1) // 10 + 1
        result = []
        for page in range(1, max_page + 1):
            html = self.get_data(page)
            mytree = lxml.etree.HTML(html)
            divs = mytree.xpath(
                '//div[@class="a-section askTeaserQuestions"]/div[@class="a-fixed-left-grid a-spacing-base"]')
            for div in divs:
                q = div.xpath('.//div[@class="a-fixed-left-grid-col a-col-right"]/a/span/text()')
                a = div.xpath('.//div[@class="a-fixed-left-grid-col a-col-right"]/span/text()')
                name = div.xpath('.//div[@class="a-profile-content"]/span/text()')
                time = div.xpath('.//div[@class="a-section a-spacing-none a-spacing-top-micro"]/span/text()')
                helpful = div.xpath('.//div[@class="a-fixed-left-grid-col a-col-left"]//span[@class="count"]/text()')
                q = list_to_str(q)
                a = list_to_str(a)
                if len(a) == 0:
                    # 此处存在【more】格式的回复，（回复字数过多时出现）
                    a = div.xpath(
                        './/div[@class="a-fixed-left-grid-col a-col-right"]//span[@class="askLongText"]/text()')
                    a = list_to_str(a)
                name = list_to_str(name)
                time = list_to_str(time).replace('· ', '')
                helpful = list_to_str(helpful)
                result.append((q, a, name, helpful, time))
        return result[:int(self.number)]


if __name__ == '__main__':
    q = Q_and_A('B0045XA94K', '10')
    a = q.parse()
    print(a)
