# coding:utf-8
"""
@version: 1.0
@author: kang
@contact: kyf0722@gmail.com
@site: www.kangyufei.net
@software: PyCharm
@file: ParserCourseAllSection.py
@time: 1/29/2016 16:54
@description: 获取某些课程章节列表
"""
from HTMLParser import HTMLParser
import urllib2

ROOT_URL = "http://www.maiziedu.com"


class CourserParser(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        HTMLParser.__init__(self)
        self.is_article = False
        self.is_state = False  # 进入获取状态
        self.is_class = False  # 进入章节url和标题获取
        self.section_list = []

    def handle_starttag(self, tag, attrs):
        HTMLParser.handle_starttag(self, tag, attrs)
        # print "handle starttag:", tag
        if tag == 'article':
            self.is_article = True
        elif tag == 'div':
            if self.is_article:
                __class = [v for k, v in attrs if k == 'class']
                if __class[0] == 'lead-img':
                    self.is_state = True
                elif __class[0] == 'artc-bt':
                    self.is_class = True
        elif tag == 'a':
            if self.is_state:
                pass  # 暂不实现
            elif self.is_class:
                self.section_list.append((ROOT_URL + attrs[0][1], attrs[1][1]))

    def handle_endtag(self, tag):
        HTMLParser.handle_endtag(self, tag)
        # print 'handle endtag:', tag
        if tag == 'article':
            self.is_article = False
        elif tag == 'div':
            self.is_class = False
            self.is_state = False


def get_section_list(course_url=""):
    request = urllib2.Request(course_url)
    response = urllib2.urlopen(request)
    context = response.read()
    tag_parser = CourserParser()
    tag_parser.feed(context)
    return tag_parser.section_list


if __name__ == '__main__':
    for _section in get_section_list('http://www.maiziedu.com/course/python/'):
        print _section[0], _section[1]
