from amz import get_request
import lxml.etree
import re
from tools import date_strft, return_list0_to_str, replace_emoji
from mylog import logger


class Reveiews:
    """
    获取评论相关信息
    :param asin: 商品id
    :param number: 需要获取评论的数量
    :param sort: 排序方式（top rated和）
    :param star: 星级选择
    :param filter_by: 过滤选项
    """

    def __init__(self, asin, number, sort='helpful', star='all_stars', filter_by='all_reviews'):
        self.asin = asin
        self.number = number
        self.sort = sort
        self.star = star
        self.filter_by = filter_by
        # if sort == 'top rated':
        #     self.sort = 'helpful'
        # elif sort == 'most recent':
        #     self.sort = 'recent'
        #
        # if filter_by == 'all reviewers':
        #     self.filter_by = 'all_reviews'
        # elif filter_by == 'verified purchase only':
        #     self.filter_by = 'avp_only_reviews'
        #
        # if str(star) == '1':
        #     self.star = 'one_star'
        # elif str(star) == '2':
        #     self.star = 'two_star'
        # elif str(star) == '3':
        #     self.star = 'three_star'
        # elif str(star) == '4':
        #     self.star = 'four_star'
        # elif str(star) == '5':
        #     self.star = 'five_star'
        # elif str(star) == 'all positive':
        #     self.star = 'positive'
        # elif str(star) == 'all critical':
        #     self.star = 'critical'
        # elif str(star) == 'all':
        #     self.star = 'all_stars'

    def make_url(self, page):
        # TODO 根据数量选择1~n页,此函数返回最大页，需要修改
        url = f'https://www.amazon.co.uk/product-reviews/{self.asin}?&reviewerType={self.filter_by}&pageNumber=' \
            f'{page}&filterByStar={self.star}&sortBy={self.sort}'
        return url

    def get_data(self, page):
        url = self.make_url(page)
        html = get_request(url)
        if not html:
            logger.error(f'''请求【{url}】被拒绝''')
        return html

    def parse(self):
        max_page = (int(self.number) - 1) // 10 + 1
        result = []
        regx = re.compile('product-reviews/(.*?)/ref')
        regx0 = re.compile('product-reviews/(.*?)\?')
        regx1 = re.compile('(.*?) out')
        regx2 = re.compile('(.*?) people')
        regx3 = re.compile('(.*?) person')
        for page in range(1, max_page + 1):
            html = self.get_data(page)
            if not html:
                continue
            mytree = lxml.etree.HTML(html)
            ids = mytree.xpath('//div[@id="cm_cr-review_list"]/div[@data-hook="review"]/@id')
            # print(ids)
            for id in ids:
                names = mytree.xpath(f'.//div[@id="{id}"]//span[@class="a-profile-name"]/text()')
                time = mytree.xpath(f'.//div[@id="{id}"]//span[@data-hook="review-date"]/text()')

                title = mytree.xpath(f'.//div[@id="{id}"]//a[@data-hook="review-title"]/span/text()')
                text = mytree.xpath(f'.//div[@id="{id}"]//span[@data-hook="review-body"]/span/text()')
                stars = mytree.xpath(f'.//div[@id="{id}"]//span[@class="a-icon-alt"]/text()')
                if len(stars) > 0:
                    star = regx1.findall(stars[0])
                else:
                    star = []
                urls = mytree.xpath(f'.//div[@id="{id}"]//a[@data-hook="format-strip"]/@href')
                if len(urls) > 0:
                    asin = regx.findall(urls[0])
                    if len(asin) == 0:
                        asin = regx0.findall(urls[0])
                else:
                    asin = []
                size1 = mytree.xpath(f'.//div[@id="{id}"]//a[@data-hook="format-strip"]/text()')
                if len(size1) > 0:
                    size1 = '||'.join(size1)
                else:
                    size1 = ''
                numbers = mytree.xpath(f'.//div[@id="{id}"]//span[@data-hook="helpful-vote-statement"]/text()')
                if len(numbers) > 0:
                    helpful = regx2.findall(numbers[0])
                    if len(helpful) == 0:
                        helpful = regx3.findall(numbers[0])
                        if len(helpful) > 0:
                            helpful = helpful[0].replace('One', '1')
                    else:
                        helpful = helpful[0]
                else:
                    helpful = 0

                if len(time) > 0:
                    time = date_strft(time[0])
                else:
                    time = '1970/01/01'

                if len(star) > 0:
                    star = float(star[0].replace(' ', ''))
                else:
                    star = 0
                names = return_list0_to_str(names)
                names = replace_emoji(names)
                title = return_list0_to_str(title)
                title = replace_emoji(title)
                title = title.replace('"', "'")

                text = return_list0_to_str(text)
                text = replace_emoji(text)
                text = text.replace('"', "'")
                asin = return_list0_to_str(asin)

                result.append((asin, time, title, text, star, helpful, size1, names))

        return result[:int(self.number)]


if __name__ == '__main__':
    rv = Reveiews('B07CS1XKST', 10)
    aa = rv.parse()
    print(len(aa))
    for i in aa:
        print(i)
