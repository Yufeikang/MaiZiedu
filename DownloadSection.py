# coding=utf-8
"""
@version: 1.0
@author: kang
@contact: kyf0722@gmail.com
@site: www.kangyufei.net
@software: PyCharm
@file: DownloadSection.py
@time: 1/29/2016 16:54
@description: 下载整个章节
"""
import urllib
import urllib2
import re
import HTMLParser
import os
import multiprocessing
import logging

ROOT_URL = "http://www.maiziedu.com"


def check_file_name(filename=''):
    filename = "".join(filename.split())
    return re.sub('[\ /:*?"<>|]', '_', filename)


def check_file_dir(file_path=""):
    (filedir, filename) = os.path.split(file_path)
    filename = check_file_name(filename)
    file_path = os.path.join(filedir, filename)
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    return file_path


class DownloadSection:
    def __init__(self, root_dir="", url=""):
        self.mRootDir = root_dir
        self.mCourseUrl = url
        self.mClassList = []
        self.mContent = ""
        self.mDownCnt = 0
        self.mCourseName = ""
        self.mDownload_list = []  # 包含保存路径和下载URl的元组
        self.mResult = []
        self.mProgressNum = 0
        self.pool = None
        self.queue = None
        self.mLogger = logging.getLogger(self.mRootDir)
        self.mLogger.setLevel(logging.DEBUG)
        logfilepath = os.path.join(self.mRootDir, 'log.txt')
        logfilepath = check_file_dir(logfilepath)
        self.mFileHandle = logging.FileHandler(logfilepath)
        formatter = logging.Formatter("%(asctime)s:[line:%(lineno)d] %(levelname)s %(message)s")
        self.mFileHandle.setFormatter(formatter)
        self.mConsoleHandle = logging.StreamHandler()
        self.mConsoleHandle.setFormatter(formatter)
        self.mLogger.addHandler(self.mFileHandle)
        self.mLogger.addHandler(self.mConsoleHandle)
        self.mManager = multiprocessing.Manager()
        self.mQueue = self.mManager.Queue()

    def obtain_content(self):
        self.mLogger.debug("obtain_content enter")
        try:
            req = urllib2.Request(self.mCourseUrl)
            self.mContent = urllib2.urlopen(req).read()
        except Exception, e:
            print e
        self.mLogger.debug("obtain_content end")
        return

    def obtain_course_name(self):
        try:
            pattern_ol = "<ol class=\"breadcrumb\">[\s\S]+?</ol>"
            pattern_li = "<li class=\"active\">[\S\s]+?</li>"
            ol_content = re.search(pattern_ol, self.mContent)
            ol_content = ol_content.group()
            li_content = re.search(pattern_li, ol_content)
            self.mCourseName = li_content.group()[19:-5]
            filter_char = "\/:*?<>|"
            for c in filter_char:
                self.mCourseName = self.mCourseName.replace(c, '_')
        except Exception, e:
            print "obtain_course_name ERROR:" + str(e)
        return

    def obtain_class_list(self):
        self.mLogger.debug("obtain_class_list enter")
        pattern_div = "<div id=\"playlist\"[\S\s]+?</div>"
        pattern_li = "<li[\s\S]+?</li>"
        pattern_url = "\"\S+?\""
        pattern_name = "lesson_id=\d+?>[\S\s]+?</a>"
        div_content = re.search(pattern_div, self.mContent).group()
        li_content = re.finditer(pattern_li, div_content)
        for _li in li_content:
            _li = _li.group()
            url_content = re.search(pattern_url, _li).group()[1:-1]
            name_content = re.search(pattern_name, _li).group()
            name_content = re.search(">[\s\S]+?<", name_content).group()[1:-1]
            html_parser = HTMLParser.HTMLParser()
            self.mClassList.append((url_content, html_parser.unescape(name_content.decode('utf-8'))))
            self.mLogger.debug('class_lis:url_content:%s', url_content)
            del html_parser
        self.mLogger.debug("obtain_class_list end")

    def get_down_url(self, url=""):
        pattern_video = "<video[\s\S]+?</video>"
        pattern_url = "src=[\S\s]+?\""
        pattern_type = "type=.*?/>"
        try:
            req = urllib2.Request(url)
            content = urllib2.urlopen(req).read()
        except Exception, e:
            self.mLogger.error("get_down_url:%s ", str(e))
            print e
        try:
            video_content = re.search(pattern_video, content).group()
            down_url = re.search(pattern_url, video_content).group()[5:-1]
            video_type = re.search(pattern_type, video_content).group()[6:-3]
        except Exception, e:
            self.mLogger.error("get_down_url:url=%s \n ERROR: %s \n CONTENT: %s", url, str(e), video_content)
            down_url = ''
            video_type = ''
        return down_url, video_type

    def down_all_class(self, call_back=None):
        for _class in self.mClassList:
            class_url = _class[0]
            class_name = _class[1]
            if class_url == "active_null":
                class_url = self.mCourseUrl
            else:
                class_url = ROOT_URL + class_url
            (down_url, video_type) = self.get_down_url(class_url)
            if down_url == '':
                continue
            if video_type == "video/mp4":
                class_name = check_file_name(class_name)
                class_name = os.path.join(self.mRootDir, class_name + ".mp4")
            class_name = check_file_dir(class_name)
            print "Url:" + down_url
            print "Name:" + class_name
            if os.path.exists(class_name):
                continue
            urllib.urlretrieve(down_url, class_name + ".tmp", call_back)
            os.rename(class_name + ".tmp", class_name)

    def down_class(self, _class, call_back=None):
        class_url = _class[0]
        class_name = _class[1]
        if class_url == "active_null":
            class_url = self.mCourseUrl
        else:
            class_url = ROOT_URL + class_url
        (down_url, video_type) = self.get_down_url(class_url)
        if video_type == "video/mp4":
            class_name = check_file_name(class_name)
            class_name = os.path.join(self.mRootDir, class_name + ".mp4")
        class_name = check_file_dir(class_name)
        # print "Url:" + down_url
        # print "Name:" + class_name
        if os.path.exists(class_name):
            return
        urllib.urlretrieve(down_url, class_name + ".tmp", call_back)
        os.rename(class_name + ".tmp", class_name)

    def get_download_list(self, class_list):
        self.mLogger.debug("get_download_list enter")
        result = []
        for _class in class_list:
            class_url = _class[0]
            class_name = _class[1]
            if class_url == "active_null":
                class_url = self.mCourseUrl
            else:
                class_url = ROOT_URL + class_url
            (down_url, video_type) = self.get_down_url(class_url)
            if video_type == "video/mp4":
                class_name = check_file_name(class_name)
                class_name = os.path.join(self.mRootDir, class_name + ".mp4")
            else:
                continue
            class_name = check_file_dir(class_name)
            self.mLogger.debug("get_download_list:%s", down_url)
            result.append((class_name, down_url))
        self.mLogger.debug("get_download_list end")
        return result

    def set_progress_num(self, num=0):
        self.mProgressNum = num

    # 启动多个进程开始下载
    def start_download_all(self):
        self.mLogger.debug("start_download_all enter")
        self.obtain_content()
        self.obtain_class_list()
        self.mDownload_list = self.get_download_list(self.mClassList)
        if self.mProgressNum == 0:
            self.mProgressNum = multiprocessing.cpu_count()
            self.mLogger.info("cpu count is %d", self.mProgressNum)
        self.pool = multiprocessing.Pool(self.mProgressNum)
        for _list in self.mDownload_list:
            self.mLogger.info('new progress:%s', _list[0])
            self.mResult.append(self.pool.apply_async(worker, (_list, self.mQueue,)))
        self.pool.close()
        self.mLogger.debug("start_download_all end")
        # self.pool.join()

    def recv_queue(self):
        self.mLogger.debug('recv_queue enter')
        while True:
            if self.mQueue.qsize() != 0:
                url, sta = self.mQueue.get_nowait()
                print url + " : " + sta
                if sta == 'end':
                    self.mDownCnt += 1
                elif sta == 'error':
                    self.mDownCnt += 1
                    self.mLogger.error(url + ':ERROR')
                if self.mDownCnt == len(self.mDownload_list):
                    return


def worker(download_url=("", ""), queue=None):
    try:
        queue.put((download_url[0], 'start'))
        if os.path.exists(download_url[0]):
            queue.put((download_url[0], 'end'))
            return
        urllib.urlretrieve(download_url[1], download_url[0] + ".tmp", schedule)
        os.rename(download_url[0] + ".tmp", download_url[0])
        queue.put((download_url[0], 'end'))
    except:
        queue.put((download_url[0], 'error'))


def schedule(block, block_size, file_size):
    if -1 != file_size:
        per = int(100.0 * block * block_size / file_size)
        if per > 100:
            per = 100
