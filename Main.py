# coding=utf-8
"""
    Created by kang on 11/1/2015.
"""
import os
import time
import urllib
from DownCourse import DownCourse
import multiprocessing


def schedule(block, block_size, file_size):
    # name = threading.currentThread().name
    # print name + ":" + str(file_size) + " block:" + str(block)
    pass


def print_data(data=[], threads=[]):
    pass


def worker(down_url=("", "")):
    print down_url[0]
    print down_url[1]
    if os.path.exists(down_url[0]):
            return
    urllib.urlretrieve(down_url[1], down_url[0] + ".tmp")
    os.rename(down_url[0] + ".tmp", down_url[0])


if __name__ == '__main__':
    multiprocessing.freeze_support()
    down_class = DownCourse("D:\\Media\\ClassVedio\\".decode('utf-8'),
                            'http://www.maiziedu.com/course/python/572-8104/')
    down_class.get_content()
    down_class.get_course_name()
    down_class.get_class_list()
    class_list = down_class.mClassList
    down_url = down_class.get_download_list(class_list)
    pool = multiprocessing.Pool(processes=8)
    result = []
    for _list in down_url:
        result.append(pool.apply_async(worker, (_list,)))
    pool.close()
    pool.join()
    print "完成"
