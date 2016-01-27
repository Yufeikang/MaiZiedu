# coding=utf-8
"""
    Created by kang on 11 / 1 / 2015.
"""
import urllib
import urllib2
import re
import HTMLParser
import os
import sys

ROOT_URL = "http://www.maiziedu.com"


def check_file_dir(file_dir=""):
    file_dir = "".join(file_dir.split())
    (dir, file) = os.path.split(file_dir)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return file_dir


class DownCourse:
    def __init__(self, root_dir="", url=""):
        if root_dir[-1] == "\\" or root_dir[-1] == "/":
            self.mRootDir = root_dir
        else:
            self.mRootDir = root_dir + "\\"
        self.mCourseUrl = url
        self.mClassList = []
        self.mContent = ""
        self.mCourseName = ""
        print "DownCourse Created\n"

    def get_content(self):
        try:
            req = urllib2.Request(self.mCourseUrl)
            self.mContent = urllib2.urlopen(req).read()
        except Exception, e:
            print e
        return

    def get_course_name(self):
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
            print "get_course_name ERROR:" + str(e)
        return

    def get_class_list(self):
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
                class_name = self.mRootDir + self.mCourseName.decode('utf-8') + "\\" + class_name + ".mp4"
            class_name = check_file_dir(class_name)
            result.append((class_name, down_url))
        return result

    def fast_start(self, call_back=None):
        self.get_content()
        self.get_course_name()
        self.get_class_list()
        self.down_class(call_back)


def schedule(block, block_size, file_size):
    if -1 != file_size:
        per = int(100.0 * block * block_size / file_size)
        if per > 100:
            per = 100
            os.write(1, '\r')
        os.write(1, 'Downloading ->' + str(per) + '%')
        os.write(1, '\b' * 18)
        sys.stdout.flush()


if __name__ == '__main__':
    class_down = DownCourse("D:\\tmp\\", 'http://www.maiziedu.com/course/android/504-7107/')
    class_down.fast_start(schedule)
