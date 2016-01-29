# coding:utf-8
"""
@version: 1.0
@author: kang
@contact: kyf0722@gmail.com
@site: www.kangyufei.net
@software: PyCharm
@file: ParserCourseAllSection.py
@time: 1/29/2016 16:54
@description: 获取麦子学院课程列表
"""
from HTMLParser import HTMLParser
import urllib2

MaiZi_URL = "http://www.maiziedu.com/course/"
ROOT_URL = "http://www.maiziedu.com"


class AllCourseParser(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        HTMLParser.__init__(self)
        self.is_class_list = False
        self.class_list = []

    def handle_starttag(self, tag, attrs):
        HTMLParser.handle_starttag(self, tag, attrs)
        # print "handle starttag:", tag
        if tag == "ul":
            # print attrs
            __class = [v for k, v in attrs if k == 'class']
            if __class:
                # print _class
                if __class[0] == 'zy_course_listNN':
                    self.is_class_list = True
        elif tag == 'a':
            if self.is_class_list:
                # print attrs
                self.class_list.append((ROOT_URL + attrs[0][1][0:-4]+'/', attrs[1][1]))

    def handle_endtag(self, tag):
        HTMLParser.handle_endtag(self, tag)
        # print 'handle endtag:', tag
        if tag == 'ul':
            self.is_class_list = False


# 获取麦子学院课程列表
# return [(url, title) ,(url, title) ...]
def get_all_course_list():
    request = urllib2.Request(MaiZi_URL)
    response = urllib2.urlopen(request)
    context = response.read()
    tag_parser = AllCourseParser()
    tag_parser.feed(context)
    return tag_parser.class_list


if __name__ == '__main__':
    for _class in get_all_course_list():
        print _class[0], _class[1].decode('utf-8')
