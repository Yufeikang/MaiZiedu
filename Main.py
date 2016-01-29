# coding=utf-8
"""
    Created by kang on 11/1/2015.
"""

from DownSection import DownloadSection
import multiprocessing

if __name__ == '__main__':
    multiprocessing.freeze_support()
    down_class = DownloadSection("D:\\Media\\ClassVedio\\python\\".decode('utf-8'),
                            'http://www.maiziedu.com/course/python/425-5465/')
    down_class.start_download_all()
    print "完成"
