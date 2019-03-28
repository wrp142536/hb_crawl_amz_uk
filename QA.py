from amz import get_request
import lxml.etree
from tools import list_to_str


class Q_and_A:
    def __init__(self, asin, number, method='most helpful first'):
        self.asin = asin
        self.number = number
        if method == 'most helpful first':
            self.method = 'HELPFUL'
        elif method == 'newest first':
            self.method = 'SUBMIT_DATE'

    def make_url(self):
        # TODO 根据数量选择1~n页,此函数返回最大页，需要修改
        url = f'https://www.amazon.co.uk/ask/questions/asin' \
            f'/{self.asin}/{(int(self.number) - 1) // 10 + 1}?sort={self.method}&isAnswered=true'
        return url

    def get_data(self):
        html = get_request(self.make_url())
        return html

    def parse(self):
        html = self.get_data()
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
                a = div.xpath('.//div[@class="a-fixed-left-grid-col a-col-right"]//span[@class="askLongText"]/text()')
                a = list_to_str(a)
            name = list_to_str(name)
            time = list_to_str(time).replace('· ', '')
            helpful = list_to_str(helpful)
            print(q, a, name, helpful, time)


if __name__ == '__main__':
    q = Q_and_A('B0045XA94K', '10')
    q.parse()
