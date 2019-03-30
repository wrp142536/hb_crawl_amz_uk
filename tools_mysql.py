from tools import Singleton
import pymysql


class Conn_Mysql(Singleton):
    def __init__(self, mysql_ip='127.0.0.1', mysql_database='test', mysql_password='liuyalong', mysql_username='root'):
        self.mysql_ip = mysql_ip
        self.mysql_database = mysql_database
        self.mysql_password = mysql_password
        self.mysql_username = mysql_username

    def conn(self):
        db = pymysql.connect(self.mysql_ip, self.mysql_username, self.mysql_password, self.mysql_database,
                             use_unicode=True, charset='utf8')
        return db


def update_into_mysql(url):
    """
    更新bsr_uk表，对访问过的url的visted字段设置为1
    :param url: url地址
    :return:
    """
    curs = mysql_db.cursor()
    sql = '''UPDATE bsr_uk set visted=1 WHERE url='{}';'''.format(url)
    try:
        curs.execute(sql)
        mysql_db.commit()
    except Exception as e:
        print('update_into_mysql', sql, e)


def write_into_mysql(table, data, deepth, visted):
    """
    把数据写入mysql
    :param table: 表名
    :param data: 要写入的数据，格式：（'',''）
    :param deepth: 当前数据的深度
    :param visted: 是否被访问过，理论上应该默认为0
    :return:
    """
    curs = mysql_db.cursor()
    sql = '''insert into {} values ("{}","{}",{},{})'''.format(table, data[0], data[1], deepth, visted)
    try:
        curs.execute(sql)
        mysql_db.commit()
    except Exception as e:
        print(data, '------', sql, e)
    # curs.close()
    # mysql_db.close()


def bool_url_in_mysql(url):
    """
    查询某个url是否在数据库表中存在
    :param url: url
    :return: bool值
    """
    curs = mysql_db.cursor()
    sql = '''SELECT * from bsr_uk where url='{}';'''.format(url)
    try:
        curs.execute(sql)
        data = curs.fetchall()
        if len(data) > 0:
            return True
        else:
            return False
    except Exception as e:
        print(sql, e)


def select_mysql(deepth):
    """
    查询数据库指定深度且没有访问过的url
    :param deepth: 深度
    :return:url元组，格式（（），（））
    """
    curs = mysql_db.cursor()
    sql = '''select url from bsr_uk where deepth={} and visted=0'''.format(deepth)
    try:
        curs.execute(sql)
        data = curs.fetchall()
        return data
    except Exception as e:
        print(sql, e)


if __name__ == '__main__':
    mysql_db = Conn_Mysql().conn()
