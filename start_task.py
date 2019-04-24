import os
import re
import requests
from tools import Singleton, clear_other_list, my_proxy, retry, run_time
from amz import asins_by_key, listing_uk, secrch_by_bsr, get_request
from mylog import logger
from tools_mysql import Conn_Mysql
import datetime
from QA import Q_and_A
from RV import Reveiews
import threadpool


class GET_TASK(Singleton):
    db = Conn_Mysql().conn()
    cursor = db.cursor()

    @classmethod
    @run_time
    def get_task_id(cls):
        # 返回任务id（未完成的任务）和黑名单标记id
        sql = f'''SELECT task.id ,task.black_flag_id FROM task INNER JOIN black_flag ON ( task.black_flag_id = \
            black_flag.id and task.is_finished=0 and black_flag.country='uk') ORDER BY id desc limit 1;'''
        cls.cursor.execute(sql)
        data = cls.cursor.fetchall()
        return data

    @classmethod
    @run_time
    def get_task_info(cls, task_id):
        sql = f'''SELECT * FROM task_info where task_id={task_id} ;'''
        cls.cursor.execute(sql)
        data = cls.cursor.fetchall()
        return data

    @classmethod
    @run_time
    def get_black_List(cls, black_flag_id):
        if black_flag_id == 0:
            return [[]]
        sql = f'''SELECT asin FROM black_list where black_flag_id={black_flag_id};'''
        cls.cursor.execute(sql)
        data = cls.cursor.fetchall()
        return data


class Start_Task(GET_TASK):
    # 参数格式：
    # key=[('water bottle',page),('water bottle',page)....]
    # bsr=[('bsr_url',number),('bsr_url',number).....]
    # asin=[asin，asin1]

    db = Conn_Mysql().conn()
    cursor = db.cursor()

    def __init__(self, **kwargs):
        super(Start_Task, self).__init__(**kwargs)
        self.db = Start_Task.db
        self.cursor = self.db.cursor()
        if kwargs:
            self.kwargs = kwargs
            if not (kwargs.__contains__('key') or kwargs.__contains__('asin') or kwargs.__contains__(
                    'bsr') or kwargs.__contains__('qa') or kwargs.__contains__('rv')):
                print('参数输入错误')
                raise ValueError
        else:
            self.kwargs = {}
        self.all_asin = []
        self.path = 'pic_uk_0'

    @run_time
    def parse_task_dict(self, task_id, black_flag_id):
        # 获取所有的asin
        if self.kwargs.__contains__('key'):
            for k in self.kwargs['key']:
                for page in range(1, k[1] + 1):
                    asins0 = asins_by_key(k[0], page)
                    logger.info(f'通过关键字第{page}页得到asin：{asins0}')
                    self.all_asin = self.all_asin + asins0
        if self.kwargs.__contains__('bsr'):
            for j in self.kwargs['bsr']:
                asins1 = secrch_by_bsr(j[0], j[1])
                logger.info(f'通过bsr得到asin：{asins1}')
                self.all_asin = self.all_asin + asins1
        if self.kwargs.__contains__('asin'):
            logger.info(f"手动添加asin：{self.kwargs['asin']}")
            self.all_asin = self.all_asin + self.kwargs['asin']

        if self.kwargs.__contains__('qa'):
            reg_asin = re.compile('asin=(.*?)&')
            reg_QANum = re.compile('QANum=(.*?)&')
            reg_sort = re.compile('sort=(.*)')
            for jj in self.kwargs['qa']:
                logger.info(f'qa请求:{jj}')
                asin = reg_asin.findall(jj)
                QANum = reg_QANum.findall(jj)
                sort = reg_sort.findall(jj)
                qa = Q_and_A(asin[0], QANum[0], method=sort[0])
                logger.debug('运行到%d行' % 99)
                qa_data = qa.parse()
                logger.debug('运行到%d行' % 101)
                for data in qa_data:
                    self.save_data(data, 'qa', task_id, black_flag_id, asin[0])
                    logger.debug('运行到%d行' % 104)

        if self.kwargs.__contains__('review'):
            reg_asin = re.compile('asin=(.*?)&')
            reviewsNum = re.compile('reviewsNum=(.*?)&')
            reg_sortBy = re.compile('sortBy=(.*?)&')
            reg_filterByStar = re.compile('filterByStar=(.*?)&')
            reg_reviewerType = re.compile('reviewerType=(.*)')
            for jj in self.kwargs['review']:
                logger.info(f'review请求:{jj}')
                asin = reg_asin.findall(jj)
                Num = reviewsNum.findall(jj)
                sort = reg_sortBy.findall(jj)
                star = reg_filterByStar.findall(jj)
                filter_by = reg_reviewerType.findall(jj)
                logger.debug('运行到%d行' % 119)
                rv = Reveiews(asin[0], Num[0], sort=sort[0], star=star[0], filter_by=filter_by[0])
                rv_data = rv.parse()
                logger.debug('运行到%d行' % 122)
                for data in rv_data:
                    self.save_data(data, 'review', task_id, black_flag_id, asin[0])
                    logger.debug('运行到%d行' % 125)

    @run_time
    def parse_task_datas_to_dict(self, datas):
        key = []
        bsr = []
        asin = []
        qa = []
        review = []
        for data in datas:
            if data[1] == 1:
                key.append([data[7], data[4]])
            elif data[2] == 1:
                bsr.append([data[7], data[4]])
            elif data[3] == 1:
                asin.append(data[7])
            elif data[5] == 1:
                qa.append(data[7])
            elif data[6] == 1:
                review.append(data[7])
        self.kwargs['key'] = key
        self.kwargs['bsr'] = bsr
        self.kwargs['asin'] = asin
        self.kwargs['qa'] = qa
        self.kwargs['review'] = review

    @run_time
    def save_data(self, data, table, task_id, black_flag_id, asin):
        run_time = datetime.datetime.strftime(datetime.datetime.today(), '%Y/%m/%d')
        if table == 'product_info':
            sql = f'''insert into {table} (run_time ,asin ,brand ,title ,price ,pic_url ,
            rev_num ,star ,is_amazon ,first_category,first_category_rank,date_first_available,
            sellers_rank,task_id,black_flag_id ) values ("{run_time}","{data['asin']}","{data['品牌']}",
            "{data['标题']}","{data['价格']}","{data['图片链接']}","{data['评论数']}","{data['星级']}",
            "{data['是否自营']}","{data['大类名字']}","{data['大类中排名']}","{data['上架时间']}","{data['子类排名']}",
            {task_id},{black_flag_id});'''
            try:
                self.cursor.execute(sql)
            except Exception:
                logger.error(sql)
            self.db.commit()
        elif table == 'review':
            pp = data

            sql = f'''insert into {table} (product_asin,review_date,title,content,star,helpful_num,color_size,
            reviewer_name,task_id,asin) values ("{pp[0]}","{pp[1]}","{pp[2]}","{pp[3]}","{pp[4]}","{pp[5]}","{pp[
                6]}","{pp[7]}",{task_id},"{asin}") '''
            try:
                self.cursor.execute(sql)
            except Exception:
                logger.error(sql)
            self.db.commit()
        else:
            pp = data
            sql = f'''insert into {table} (ask_date,question,answer,answer_name,vote_num,task_id,asin) values ("{pp[
                0]}","{pp[1]}","{pp[2]}","{pp[3]}","{pp[4]}",{task_id},"{asin}") '''
            try:
                self.cursor.execute(sql)
            except Exception:
                logger.error(sql)
            self.db.commit()

    @run_time
    def callback_for_save_listing(self, *result):
        # args[0].args[0] 是asin，来源于listing函数的输入参数，result[1]是listing函数的执行结果
        if result[1]:
            self.save_data(result[1], 'product_info', self.task_id, self.black_flag_id, result[0].args[0])
        else:
            logger.error(f'商品详情页未抓到数据，asin：{result[0].args[0]}')

    @retry(5)
    def down_load_pic(self, url):
        if not url:
            return
        proxies = my_proxy()
        resp = requests.get(url=url, proxies=proxies, verify=False, timeout=120)
        # 此处抛出异常，让装饰器处理，进行再次发起请求
        if resp.status_code != 200:
            raise ValueError

        path_name = re.split('/', url)[-1]
        with open(self.path + '/' + str(path_name), 'wb+') as fb:
            fb.write(resp.content)
        logger.warning(f'''图片【{url}】，大小为【%.2fKB】,状态码【{resp.status_code}】''' % (len(resp.content) / 1024))

    def start(self):
        logger.info('【----------爬虫任务启动------------】')
        # uk_tasks = self.get_black_flag_id()
        # if not uk_tasks:
        #     logger.info('没有获取任务')
        #     logger.info('【------------爬虫任务结束------------】\n\n')

        # 查询任务id和黑名单标记
        tsk_data = self.get_task_id()
        if not tsk_data:
            logger.info('未获取任务')
            return
        self.task_id = tsk_data[0][0]
        logger.info(f'开始执行任务，任务id为{self.task_id}')
        self.black_flag_id = tsk_data[0][1]
        if self.black_flag_id == 0:
            black_asins = []
        else:
            # 查询出黑名单列表
            blc = self.get_black_List(self.black_flag_id)
            black_asins = [k[0] for k in blc]
        logger.info(f'''黑名单asin{black_asins}''')
        # 获取任务详情
        task_info_datas = self.get_task_info(self.task_id)
        logger.debug('运行到%d行' % 234)

        # 任务解析成字典格式
        self.parse_task_datas_to_dict(task_info_datas)
        logger.debug('运行到%d行' % 238)
        # 解析字典
        self.parse_task_dict(self.task_id, self.black_flag_id)
        logger.debug('运行到%d行' % 241)
        # 清洗asin,去掉黑名单里的asin
        asins = clear_other_list(self.all_asin, black_asins)
        logger.info(f'共需要解析【{len(asins)}】个asin')
        if len(asins) == 0:
            logger.info('【------------爬虫任务结束------------】\n\n')
            self.change_task_status(self.task_id)
            logger.debug('运行到%d行' % 248)

            return

            # 开一个10数量的线程池
        pool = threadpool.ThreadPool(10)
        # 创建任务
        reques = threadpool.makeRequests(listing_uk, asins, callback=self.callback_for_save_listing)
        # 添加所有任务
        [pool.putRequest(req) for req in reques]
        pool.wait()

        self.change_task_status(self.task_id)

        # # 查询本次任务所有的pic url
        # sql_pics = f'''SELECT pic_url FROM product_info where task_id={self.task_id} and pic_url!='';'''
        # self.cursor.execute(sql_pics)
        # pics = self.cursor.fetchall()
        # my_pics = [k[0] for k in pics]
        #
        # self.path = 'pic_uk_' + str(self.task_id)
        # if not os.path.exists(self.path):
        #     os.makedirs(self.path)
        #
        # # 创建任务2
        # reques2 = threadpool.makeRequests(self.down_load_pic, my_pics)
        # [pool.putRequest(req) for req in reques2]
        # pool.wait()

        logger.info('【------------爬虫任务结束------------】\n\n')
        # 向队列发送退出命令
        # qq.put('exit')
        return

    @run_time
    def change_task_status(self, task_id):
        # 任务完成后把数据库任务状态设为已完成
        sql = f'''update task set is_finished=1 where id={task_id}'''
        self.cursor.execute(sql)
        self.db.commit()

    def __del__(self):
        self.cursor.close()
        self.db.close()


if __name__ == '__main__':
    # print(f"{datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d %H:%M:%S')} 爬虫程序启动")
    s = Start_Task()
    s.start()
    # print(f"{datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d %H:%M:%S')} 爬虫程序关闭")
