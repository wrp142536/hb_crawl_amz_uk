from tools import Singleton, clear_other_list
from amz import asins_by_key, listing_uk, secrch_by_bsr
from mylog import logger
from tools_mysql import Conn_Mysql
import datetime
from QA import Q_and_A
from RV import Reveiews
import re


class GET_TASK(Singleton):
    db = Conn_Mysql().conn()
    cursor = db.cursor()

    @classmethod
    def get_black_flag_id(cls):
        # 此处只查英国站的黑名单
        sql = f'''SELECT id FROM black_flag where country='uk';'''
        cls.cursor.execute(sql)
        data = cls.cursor.fetchall()
        return data

    @classmethod
    def get_task_id(cls):
        # 返回任务id（未完成的任务）和黑名单标记id
        sql = f'''SELECT id,black_flag_id FROM task where is_finished=0 order by id desc limit 1;'''
        cls.cursor.execute(sql)
        data = cls.cursor.fetchall()
        return data

    @classmethod
    def get_task_info(cls, task_id):
        sql = f'''SELECT * FROM task_info where task_id={task_id} ;'''
        cls.cursor.execute(sql)
        data = cls.cursor.fetchall()
        return data

    @classmethod
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
    # black_asin_list=['','','',]
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

    def parse_task_dict(self, task_id, black_flag_id):
        # 获取所有的asin
        if self.kwargs.__contains__('key'):
            for k in self.kwargs['key']:
                asins0 = asins_by_key(k[0], k[1])
                logger.info(f'通过关键字得到asin：{asins0}')
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
                qa_data = qa.parse()
                for data in qa_data:
                    self.save_data(data, 'qa', task_id, black_flag_id, asin[0])

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
                rv = Reveiews(asin[0], Num[0], sort=sort[0], star=star[0], filter_by=filter_by[0])
                rv_data = rv.parse()
                for data in rv_data:
                    self.save_data(data, 'review', task_id, black_flag_id, asin[0])

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
                6]}","{
            pp[7]}",{task_id},"{asin}") '''
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

    def start(self):
        logger.info('【爬虫程序启动】')
        # 查询任务id和黑名单标记
        tsk_data = self.get_task_id()
        if not tsk_data:
            logger.info('未获取任务')
            return
        task_id = tsk_data[0][0]
        logger.info(f'开始执行任务，任务id为{task_id}')
        black_flag_id = tsk_data[0][1]
        if black_flag_id == 0:
            black_asins = []
        else:
            # 查询出黑名单列表
            blc = self.get_black_List(black_flag_id)
            black_asins = [k[0] for k in blc]

        # 获取任务详情
        task_info_datas = self.get_task_info(task_id)

        # 任务解析成字典格式
        self.parse_task_datas_to_dict(task_info_datas)
        # 解析字典
        self.parse_task_dict(task_id, black_flag_id)
        # 清洗asin,去掉黑名单里的asin
        asins = clear_other_list(self.all_asin, black_asins)
        for asin in asins:
            tmp_dict = listing_uk(asin)
            self.save_data(tmp_dict, 'product_info', task_id, black_flag_id, asin)
        self.change_task_status(task_id)

    def change_task_status(self, task_id):
        # 任务完成后把数据库任务状态设为已完成
        sql = f'''update task set is_finished=1 where id={task_id}'''
        self.cursor.execute(sql)
        self.db.commit()

    def __del__(self):
        self.cursor.close()
        self.db.close()


if __name__ == '__main__':
    s = Start_Task()
    s.start()
    print('over!')