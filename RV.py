from amz import get_request
import lxml.etree
import re


class Reveiews:
    """
    获取评论相关信息
    :param asin: 商品id
    :param number: 需要获取评论的数量
    :param sort: 排序方式（top rated和）
    :param star: 星级选择
    :param filter_by: 过滤选项
    """

    def __init__(self, asin, number, sort='top rated', star='all', filter_by='all reviewers'):
        self.asin = asin
        self.number = number
        if sort == 'top rated':
            self.sort = 'helpful'
        elif sort == 'most recent':
            self.sort = 'recent'

        if filter_by == 'all reviewers':
            self.filter_by = 'all_reviews'
        elif filter_by == 'verified purchase only':
            self.filter_by = 'avp_only_reviews'

        if str(star) == '1':
            self.star = 'one_star'
        elif str(star) == '2':
            self.star = 'two_star'
        elif str(star) == '3':
            self.star = 'three_star'
        elif str(star) == '4':
            self.star = 'four_star'
        elif str(star) == '5':
            self.star = 'five_star'
        elif str(star) == 'all positive':
            self.star = 'positive'
        elif str(star) == 'all critical':
            self.star = 'critical'
        elif str(star) == 'all':
            self.star = 'all_stars'

    def make_url(self):
        # TODO 根据数量选择1~n页,此函数返回最大页，需要修改
        url = f'https://www.amazon.co.uk/product-reviews/{self.asin}?&reviewerType={self.filter_by}&pageNumber=' \
            f'{(int(self.number) - 1) // 10 + 1}&filterByStar={self.star}&sortBy={self.sort}'
        return url

    def get_data(self):
        html = get_request(self.make_url())
        return html

    def parse(self):
        html = self.get_data()
        mytree = lxml.etree.HTML(html)
        regx = re.compile('product-reviews/(.*?)ref')
        regx1 = re.compile('(.*?) out')
        regx2 = re.compile('(.*?) people')
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
            else:
                asin = []
            size1 = mytree.xpath(f'.//div[@id="{id}"]//a[@data-hook="format-strip"]/text()')
            numbers = mytree.xpath(f'.//div[@id="{id}"]//span[@data-hook="helpful-vote-statement"]/text()')
            if len(numbers) > 0:
                helpful = regx2.findall(numbers[0])
            else:
                helpful = []
            print(time, asin, title, text, star, helpful, size1, names)

        # for a,b,c,d,e,f,g in zip(time,urls,title,text,star,size,names)


if __name__ == '__main__':
    rv = Reveiews('B01KORI78A', 10)
    rv.parse()
