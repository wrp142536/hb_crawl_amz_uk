class Listing_Rules:
    """亚马逊商品详情页爬虫规则"""

    # 标题
    @staticmethod
    def rules_title():
        rules = [('re_S', '<span id="productTitle" class="a-size-large">(.*?)</span>?'),
                 ('xpath', '//span[@id="btAsinTitle"]/text()'),
                 ('xpath', '//h1[@data-automation-id="title"]/text()'),
                 ]
        return rules

    # 大类排名
    @staticmethod
    def rules_rank():
        rules = [
            ('xpath', '//li[@id="SalesRank"]/text()'),
            ('xpath', '//tr[@id="SalesRank"]/td[@class="value"]/text()'),
        ]
        return rules

    # 子类排名
    @staticmethod
    def rules_child_rank():
        rules = [
            ('xpath', '//*[@id="SalesRank"]//ul'),
        ]
        return rules

    # 评论数量
    @staticmethod
    def rules_rev():
        rules = [('re', '">([\d, ]+)customer reviews'),
                 ('xpath', '//span[@id="acrCustomerReviewText"]//text()'),
                 ]
        return rules

    # 评分，星级
    @staticmethod
    def rules_scores():
        rules = [('re', 'class="reviewCountTextLinkedHistogram noUnderline" title="(.*) out of 5 stars'),
                 ('re', '>([\d. ]+)out of 5 stars'),
                 ]
        return rules

    # 价格
    @staticmethod
    def rules_price():
        rules = [('re', 'class="a-size-medium a-color-price">(.*)</span>'),
                 ('re', 'class="a-color-price a-text-bold">(.*)</span>'),
                 ('xpath', '//td[@class="a-color-price a-size-medium a-align-bottom"]/text()'),
                 ('xpath', '//span[@class="a-size-medium a-color-price offer-price a-text-normal"]/text()'),
                 ('xpath', '//span[@id="color_name_1_price"]/span[@class="a-size-mini twisterSwatchPrice"]/text()'),
                 ('xpath', '//div[@id="unqualifiedBuyBox"]//span[@class="a-color-price"]/text()'),
                 ('xpath', '//span[@id="priceblock_ourprice"]/text()'),
                 ('xpath', '//span[@id="price_inside_buybox"]/text()'),
                 ('xpath',
                  '//button[@class="av-button av-button--default js-purchase-button dv-record-reftag"]/text()'),

                 ]
        return rules

    # 品牌
    @staticmethod
    def rules_pinpai():
        rules = [('re', 'id="bylineInfo".*>+(.*)</a>'),
                 ('re', 'id="gc-brand-name-link".*>+(.*)</a>'),
                 ]
        return rules

    # 上架时间
    @staticmethod
    def rules_sell_time():
        rules = [('re', '<li><b> Date first available at Amazon.co.uk:</b> (.*)</li>'),
                 ('xpath', '//tr[@class="date-first-available"]/td[@class="value"]/text()'),
                 ('re', '<td class="label">Date First Available</td>'),
                 ]
        return rules

    # 图片url
    @staticmethod
    def rules_pic():
        rules = [('xpath', '//div[@class="imgTagWrapper"]/img/@src'),
                 ('xpath', '//div[@class="av-fallback-packshot"]/img/@src'),
                 ('xpath', '//div[@class="imgTagWrapper"]/img/@data-old-hires'),
                 ('xpath', '//div[@class="imgTagWrapper"]/img/@data-a-dynamic-image'),
                 ('xpath', '//div[@id="img-canvas"]/img/@data-a-dynamic-image'),
                 ]
        return rules

    # 自营
    @staticmethod
    def rules_ziying():
        rules = [('re', 'sold by Amazon.'),
                 ]
        return rules


class SP_by_key:

    @staticmethod
    def sp():
        rules = [('re_S', 'a-popover-sp-info-popover-(.*?)"><span>These are ads'),
                 ('re', 'a-popover-sponsored-header-(.*?)"><span>These are ads'),
                 ('xpath_replace', "//div[contains(@id,'a-popover-sp-info-popover-')]/@id"),
                 ]
        return rules


class Search_by_key:

    @staticmethod
    def asin_by_key():
        rules = [('xpath', '//div[contains(@data-cel-widget,"search_result_")]/@data-asin'),
                 ('xpath', '//div[@class="s-result-list sg-row"]//div/@data-asin'),
                 ('xpath', '//li[contains(@id,"result_")]//@data-asin'),
                 ]
        return rules
