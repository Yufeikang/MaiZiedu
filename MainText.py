# coding:utf-8
"""
@version: ??
@author: kang
@contact: kyf0722@gmail.com
@site: www.kangyufei.net
@software: PyCharm
@file: MainText.py
@time: 1/29/2016 18:07
@description:??
"""
from ParserAllCourse import get_all_course_list
from ParserCourseAllSection import get_section_list
from DownloadSection import DownloadSection, check_file_dir, DIR_SPLIT_C
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def main(root_dir=''):
    course_list = get_all_course_list()
    print u'''
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                麦子学院当前免费课程列表：
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
             '''
    num = 0
    for course in course_list:
        num += 1
        print "     %2d" % num + u".课程：" + course[1].decode('utf-8')
        print "        " + u"课程首页:" + course[0]

    course_num = int(raw_input(u"输入要下载的课程编号：")) - 1
    section_list = get_section_list(course_list[course_num][0])
    course_dir = root_dir + course_list[course_num][1] + DIR_SPLIT_C
    course_dir = check_file_dir(course_dir)
    print u'''
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                当前课程的所以章节列表：
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
             '''
    num = 0
    for section in section_list:
        num += 1
        print "     %2d" % num + u".章节：" + section[1].decode('utf-8')
        print "        " + u"章节首页:" + section[0]
    section_num_list = raw_input(u"输入要下载的章节编号(下载多个用，分开，输入0下载所有)：")
    section_num_list = section_num_list.split(',')
    if '0' in section_num_list:
        for _section in section_list:
            section_dir = course_dir + _section[1] + DIR_SPLIT_C
            section_dir = check_file_dir(section_dir)
            downloader = DownloadSection(section_dir, _section[0])
            downloader.start_download_all()
    for section_num in section_num_list:
        _section_num = int(section_num)-1
        section_dir = course_dir + section_list[_section_num][1] + DIR_SPLIT_C
        section_dir = check_file_dir(section_dir)
        downloader = DownloadSection(section_dir, section_list[_section_num][0])
        downloader.start_download_all()


if __name__ == "__main__":
    main(u"D:\\Media\\ClassVedio\\")
