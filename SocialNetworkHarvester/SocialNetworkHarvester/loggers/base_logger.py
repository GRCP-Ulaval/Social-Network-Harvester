import logging
import pprint
import re
import threading
from datetime import datetime


class Logger():
    indent_level = 0

    def __init__(self, loggerName="defaultLogger", filePath="default.log", format='%(message)s',
                 wrap=False, append=True, indentation=4, showThread=False):
        self.defaultFilePath = filePath
        if not append:
            self.reset_log()
        self.format = format
        self.wrap = wrap
        self.indentation = indentation
        self.loggerName = loggerName
        self.fileHandler = None
        self.createLogger()
        self.showThread = showThread

    def reset_log(self):
        open(self.defaultFilePath, 'w').close()

    def setFileHandler(self, filepath):
        if self.fileHandler:
            self.logger.removeHandler(self.fileHandler)
        self.fileHandler = logging.FileHandler(filepath, mode="a+", encoding='utf-8')
        self.fileHandler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(self.format)
        self.fileHandler.setFormatter(formatter)
        self.logger.addHandler(self.fileHandler)

    def createLogger(self):
        self.logger = logging.getLogger(self.loggerName)
        self.logger.setLevel(logging.DEBUG)
        self.setFileHandler(self.defaultFilePath)

    def indent(self):
        self.indent_level += self.indentation

    def unindent(self):
        self.indent_level -= self.indentation

    def log(self, message, showTime=True, showDate=True, showThread=None):
        if showThread is None:
            showThread = self.showThread
        try:
            self.logger.info(
                "{date}{time}{thread}{indent}{message}".format(
                    date=showDate * datetime.utcnow().strftime("%Y/%m/%d "),
                    time=showTime * datetime.utcnow().strftime("%H:%M | "),
                    thread=showThread * "{threading.current_thread().name:^30} | ",
                    indent=" " * (self.indent_level),
                    message=message,
                )
            )
        except:
            self.logger.exception("AN ERROR OCCURED IN LOGGING ELEMENT!")

    def pretty(self, message):
        try:
            if isinstance(message, list):
                self.log('[')
                self.indent()
                for i in message:
                    self.log('%s,' % i)
                self.unindent()
                self.log(']')
            else:
                self.logger.info(self.pformat(message))
        except:
            self.logger.info(self.pformat(message.encode('unicode-escape')))

    def exception(self, message='EXCEPTION', showTime=True, showDate=True):
        self.logger.exception("%s%s%s%s" % (
            showDate * datetime.utcnow().strftime('%Y/%m/%d '),
            showTime * datetime.utcnow().strftime('%H:%M | '),
            self.showThread * '{:^30} | '.format(threading.current_thread().name),
            message))

    def debug(self, showArgs=False, showFile=False, showClass=True):
        '''Decorator used to intelligently debug functions, classes, etc.
        '''

        def outer(func):
            def inner(*args, **kwargs):
                filename = func.__code__.co_filename
                func_name = func.__name__
                argCount = func.__code__.co_argcount
                inClassInstance = 0
                varNames = func.__code__.co_varnames

                s = []
                if self.showThread:
                    s += ['{:<30}'.format(threading.current_thread().name)]
                s += [' ' * self.indent_level]
                if showFile:
                    s += [re.sub(r'(.*/)|(.*\\)', '', filename), ": "]

                if 'self' in varNames:
                    varNames = tuple(var for var in varNames if var != 'self')
                    inClassInstance = 1
                    instance = args[0]
                    if showClass:
                        s += ["%s." % re.search(r"(?<=\.)\w+(?=\'>)", str(type(instance))).group(0)]

                s += [func_name, '(']
                for varName in varNames[0:argCount - inClassInstance]:
                    s += [varName, ', ']
                if s[-1] == ', ':
                    s[-1] = "):"
                else:
                    s.append("):")
                self.logger.info("".join(s))

                self.indent_level += self.indentation

                if showArgs:
                    self.printArgs(varNames, argCount, inClassInstance, args)

                if self.wrap:
                    if self.indent_level > self.indentation * 40:
                        self.indent_level = 8
                    elif self.indent_level < 0:
                        self.indent_level = self.indentation * 40 - 4
                try:
                    ret = func(*args, **kwargs)
                    self.indent_level -= self.indentation
                except:
                    self.indent_level -= self.indentation
                    if not showArgs:
                        self.printArgs(varNames, argCount, inClassInstance, args)
                    raise
                return ret

            return inner

        return outer

    def printArgs(self, varNames, argCount, inClassInstance, args):
        for variable, i in zip(varNames[:argCount - inClassInstance], range(inClassInstance, argCount)):
            strVar = []
            if self.showThread:
                strVar += ['{:<30}'.format(threading.current_thread().name)]
            strVar.append(" " * self.indent_level + '<arg ' + variable + ' = ')
            if isinstance(args[i], dict):
                strVar.append(self.pformat(args[i]))
            else:
                strVar.append(str(args[i]))
            strVar.append('>')
            self.logger.info("".join(strVar))

    def pformat(self, message):
        return pprint.pformat(message, indent=self.indentation)
