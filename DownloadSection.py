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
import sys
import multiprocessing
import logging

ROOT_URL = "http://www.maiziedu.com"


def check_file_dir(file_dir=""):
    file_dir = "".join(file_dir.split())
    (dir, file) = os.path.split(file_dir)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return file_dir


class DownloadSection:
    def __init__(self, root_dir="", url=""):
        if root_dir[-1] == "\\" or root_dir[-1] == "/":
            self.mRootDir = root_dir
        else:
            self.mRootDir = root_dir + "\\"
        self.mCourseUrl = url
        self.mClassList = []
        self.mContent = ""
        self.mCourseName = ""
        self.mDownload_list = []  # 包含保存路径和下载URl的元组
        self.mResult = []
        self.mProgressNum = 0
        self.mLogger = logging.getLogger(self.mRootDir)
        self.mLogger.setLevel(logging.INFO)
        self.mFileHandle = logging.FileHandler(self.mRootDir + 'log.txt')
        self.mConsoleHandle = logging.StreamHandler()
        self.mLogger.addHandler(self.mFileHandle)
        self.mLogger.addHandler(self.mConsoleHandle)

    def obtain_content(self):
        try:
            req = urllib2.Request(self.mCourseUrl)
            self.mContent = urllib2.urlopen(req).read()
        except Exception, e:
            print e
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
            del html_parser

    @staticmethod
    def get_down_url(url=""):
        pattern_video = "<video[\s\S]+?</video>"
        pattern_url = "src=\S+?\""
        pattern_type = "type=.*?/>"
        try:
            req = urllib2.Request(url)
            content = urllib2.urlopen(req).read()
        except Exception, e:
            print e
        video_content = re.search(pattern_video, content).group()
        down_url = re.search(pattern_url, video_content).group()[5:-1]
        video_type = re.search(pattern_type, video_content).group()[6:-3]
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
            if video_type == "video/mp4":
                class_name = self.mRootDir + self.mCourseName + "\\" + class_name + ".mp4"
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
            class_name = self.mRootDir + self.mCourseName.decode('utf-8') + "\\" + class_name + ".mp4"
        class_name = check_file_dir(class_name)
        # print "Url:" + down_url
        # print "Name:" + class_name
        if os.path.exists(class_name):
            return
        urllib.urlretrieve(down_url, class_name + ".tmp", call_back)
        os.rename(class_name + ".tmp", class_name)

    def get_download_list(self, class_list):
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
                class_name = self.mRootDir + "\\" + class_name + ".mp4"
            class_name = check_file_dir(class_name)
            result.append((class_name, down_url))
        return result

    def set_progress_num(self, num=0):
        self.mProgressNum = num

    # 启动多个进程开始下载
    def start_download_all(self):
        self.obtain_content()
        self.obtain_class_list()
        self.mDownload_list = self.get_download_list(self.mClassList)
        if self.mProgressNum == 0:
            self.mProgressNum = multiprocessing.cpu_count()
            self.mLogger.info("cpu count is %d", self.mProgressNum)
        pool = multiprocessing.Pool(self.mProgressNum)
        for _list in self.mDownload_list:
            self.mResult.append(pool.apply_async(worker, (_list,)))
        pool.close()
        pool.join()


def worker(download_url=("", "")):
    print download_url[0]
    print download_url[1]
    if os.path.exists(download_url[0]):
        return
    urllib.urlretrieve(download_url[1], download_url[0] + ".tmp")
    os.rename(download_url[0] + ".tmp", download_url[0])


def schedule(block, block_size, file_size):
    if -1 != file_size:
        per = int(100.0 * block * block_size / file_size)
        if per > 100:
            per = 100
            os.write(1, '\r')
        os.write(1, 'Downloading ->' + str(per) + '%')
        os.write(1, '\b' * 18)
        sys.stdout.flush()
