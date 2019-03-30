from tools import Singleton
from amz import asins_by_key, listing_uk, secrch_by_bsr
from tools_mysql import Conn_Mysql


class GET_TASK(Singleton):
    db = Conn_Mysql().conn()
    cursor = db.cursor()

    @classmethod
    def get_task(cls):
        sql = f'''SELECT id,country FROM task ORDER BY id desc limit 1'''
        cls.cursor.execute(sql)
        data = cls.cursor.fetchall()
        return data

    @classmethod
    def get_task_info(cls, data, flag):
        sql = f'''SELECT info,number FROM task_info where task_id={data[0][0]} and {flag}=1'''
        cls.cursor.execute(sql)
        data = cls.cursor.fetchall()
        return data


class Start_Task(GET_TASK):
    # 参数格式：
    # key=[('water bottle',page),('water bottle',page)....]
    # bsr=[('bsr_url',number),('bsr_url',number).....]
    # asin=[asin，asin1]
    # black_asin_list=['','','',]
    db = Conn_Mysql().conn()
    cursor = db.cursor()

    def __init__(self, **kwargs):
        super(Start_Task, self).__init__(**kwargs)
        self.db = Start_Task.db
        self.cursor = self.db.cursor()
        if not (kwargs.__contains__('key') or kwargs.__contains__('asin') or kwargs.__contains__('bsr')):
            print('参数输入错误')
            raise ValueError
        self.kwargs = kwargs
        self.all_asin = []

    def parse(self):
        # 获取所有的asin
        if self.kwargs.__contains__('key'):
            for k in self.kwargs['key']:
                asins0 = asins_by_key(k[0], k[1])
                self.all_asin.append(asins0)
        if self.kwargs.__contains__('bsr'):
            for j in self.kwargs['bsr']:
                asins1 = secrch_by_bsr(j[0], j[1])
                self.all_asin.append(asins1)
        if self.kwargs.__contains__('asin'):
            self.all_asin.append(self.kwargs['asin'])

    def listing(self):
        if self.kwargs.__contains__('black_asin_list'):
            asins = (i for item in self.all_asin for i in item if i not in self.kwargs['black_asin_list'])
        else:
            asins = (i for item in self.all_asin for i in item)
        result = []
        for asin in asins:
            my_items = listing_uk(asin)
            result.append(my_items)
        return result

    def start(self):

        self.parse()

    def save_data(self):
        sql = f'''insert into  '''
        pass

    def __del__(self):
        self.cursor.close()
        self.db.close()


if __name__ == '__main__':
    s = Start_Task(key=('water bottle', 1), bsr=('bsr_url', 10))
    c = s.start()

    print(c)
    # asins_by_key('water bottle', 1)
    # asins = secrch_by_bsr(bsr_url, 100)
    # listing_uk('604079156X')
