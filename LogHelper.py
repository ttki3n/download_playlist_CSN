import logging

#default 
l_name = "LogHelper"
#l_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#l_format = "%(asctime)s - %(pathname)s-  %(levelname)s - %(message)s"
l_format = "[%(asctime)s] [%(levelname)8s] --- %(message)s"
l_log_file_level = logging.DEBUG
l_log_file_name = "log.txt"
l_log_console_level = logging.DEBUG


class LogHelper:
    """
        A simple log helper
        Init with keyword params:
            name                    : name of logger
            format                  : format
            file_level              : log level of file handler, default is DEBUG
            file_name               : log file name
            console_level           : log level of console level, defaul is ERROR
    """
    def __init__(self, **kw):       
        name = kw.get("name", l_name)
        format = kw.get("format", l_format)
        log_file_level = kw.get("file_level", l_log_file_level)
        log_file_name = kw.get("file_name", l_log_file_name)
        log_cs_level = kw.get("console_level", l_log_console_level)
        
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(format)

        fh = logging.FileHandler(log_file_name)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        ch = logging.StreamHandler()
        ch.setLevel(log_cs_level)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        self.logger.info("")
        self.logger.info(" ---------- ---------- ---------- ---------- ---------- ")
        self.logger.info(" START NEW SESSION ")
        self.logger.info("\n")
log_helper = LogHelper()

