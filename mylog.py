import logging
import logging.handlers
from logging.handlers import TimedRotatingFileHandler
import gzip
import os
import time


class Singleton:
    """
    单例模式
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance


class GzTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when, interval, **kwargs):
        super(GzTimedRotatingFileHandler, self).__init__(filename, when, interval, **kwargs)

    def doGzip(self, old_log):
        with open(old_log, 'rb') as old:
            with gzip.open(old_log.replace('.log', '', 1) + '.gz', 'wb') as comp_log:
                comp_log.writelines(old)
        os.remove(old_log)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if os.path.exists(dfn):
            os.remove(dfn)
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
            self.doGzip(dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


class My_log(Singleton):
    """
    日志系统，error,info,warning分别记录,每周切割并压缩日志
    """

    def __init__(self, logger_name='lyl', info_name='amz_info.log', error_name='amz_error.log',
                 warning_name='amz_warning.log', debug_name='amz_debug.log'):
        self.info_name = info_name
        self.logger_name = logger_name
        self.error_name = error_name
        self.warning_name = warning_name
        self.debug_name = debug_name
        self.path = os.path.dirname(os.path.abspath(__file__)) + '/logs/'

    def get_logger(self):
        logger = logging.getLogger(self.logger_name)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        # 添加此行，防止日志重复记录
        if not logger.handlers:
            # 默认日志等级
            logger.setLevel(logging.INFO)

            # 格式化输出
            formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(message)s", "%Y%m%d %H:%M:%S")
            formatter01 = logging.Formatter("%(asctime)s - %(message)s", "%Y%m%d %H:%M:%S")

            # 创建两个handler
            # info_handler = logging.handlers.TimedRotatingFileHandler(self.info_name, when='midnight', interval=7,
            #                                                          backupCount=7, encoding='utf-8')
            # error_handler = logging.handlers.TimedRotatingFileHandler(self.error_name, when='midnight', interval=7,
            #                                                           backupCount=7, encoding='utf-8')
            # warning_handler = logging.handlers.TimedRotatingFileHandler(self.warning_name, when='midnight', interval=7,
            #                                                             backupCount=7, encoding='utf-8')
            # #

            info_handler = GzTimedRotatingFileHandler(self.path + self.info_name, when='D', interval=10,
                                                      backupCount=7, encoding='utf-8')
            error_handler = GzTimedRotatingFileHandler(self.path + self.error_name, when='D', interval=10,
                                                       backupCount=7, encoding='utf-8')
            warning_handler = GzTimedRotatingFileHandler(self.path + self.warning_name, when='D', interval=10,
                                                         backupCount=7, encoding='utf-8')
            if logger.level == logging.DEBUG:
                debug_handler = GzTimedRotatingFileHandler(self.path + self.debug_name, when='D', interval=10,
                                                           backupCount=7, encoding='utf-8')
                debug_handler.suffix = "%Y%m%d.log"
                debug_handler.setFormatter(formatter01)
                debug_handler.setLevel(logging.DEBUG)
                debug_filter = logging.Filter()
                debug_filter.filter = lambda record: record.levelno == logging.DEBUG
                debug_handler.addFilter(debug_filter)
                logger.addHandler(debug_handler)

            # # 去掉名字中的.log
            # info_handler.namer = lambda x: x.replace(".log", '')
            # error_handler.namer = lambda x: x.replace(".log", '')
            # warning_handler.namer = lambda x: x.replace(".log", '')

            # # # # 设置日志切割后的名字后缀
            info_handler.suffix = "%Y%m%d.log"
            error_handler.suffix = "%Y%m%d.log"
            warning_handler.suffix = "%Y%m%d.log"

            # 设置日志等级
            error_handler.setLevel(logging.ERROR)
            warning_handler.setLevel(logging.WARNING)
            info_handler.setLevel(logging.INFO)

            # 格式化输出应用给handlers
            info_handler.setFormatter(formatter)
            error_handler.setFormatter(formatter)
            warning_handler.setFormatter(formatter01)

            # 添加过滤器，过滤掉info中等级小于warning的
            info_filter = logging.Filter()
            info_filter.filter = lambda record: record.levelno == logging.INFO

            warning_filter = logging.Filter()
            warning_filter.filter = lambda record: record.levelno == logging.WARNING

            info_handler.addFilter(info_filter)
            warning_handler.addFilter(warning_filter)

            # handler添加给对象
            logger.addHandler(info_handler)
            logger.addHandler(error_handler)
            logger.addHandler(warning_handler)
        return logger


# 为了方便导入logger，在此处执行
logger = My_log().get_logger()
