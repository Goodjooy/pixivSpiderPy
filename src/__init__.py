from concurrent.futures import thread
import threading
import os
__ALL__ = ["album", "image", "spider"]
# 这些是常量，任何时候不可改变

#from .album import Album


DIVISION_BY_ALBUM_ID = 0
DIVISION_BY_ALBUM_NAME_AND_ID = 1

DIVISION_BY_AOTHOR_NAME_WITHOUT_SUB_DIR = 2
DIVISION_BY_AOTHOR_NAME_WITH_ALBUM_NAME_AND_ID = 3

DIVISION_NO = 4


referer = "https://www.pixiv.net"
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"

albumInfo = "https://www.pixiv.net/ajax/illust/%s/pages?lang=zh"
authorInfo = "https://www.pixiv.net/ajax/user/%s/profile/all"
authorIDAndTags = "https://www.pixiv.net/ajax/illust/%s?lang=zh"
recommandInfo = "https://www.pixiv.net/ajax/illust/%s/recommend/init?limit=18&lang=zh"


def build_save_path(a, division_type: int = DIVISION_BY_ALBUM_NAME_AND_ID) -> str:
    """
    文件保存目录路径生成器
    """
    dirs = None
    if division_type == DIVISION_BY_ALBUM_ID:
        dirs = "%s" % (a.album_id)
    elif division_type == DIVISION_BY_ALBUM_NAME_AND_ID:
        dirs = "%s-[%s]" % (a.album_name, a.album_id)
    elif division_type == DIVISION_BY_AOTHOR_NAME_WITHOUT_SUB_DIR:
        dirs = "%s-[%s]" % (a.aother, a.aother_id)
    elif division_type == DIVISION_BY_AOTHOR_NAME_WITH_ALBUM_NAME_AND_ID:
        dirs = "%s-[%s]/%s-[%s]" % (a.aother,
                                    a.aother_id, a.album_name, a.album_id)
    elif division_type == DIVISION_NO:
        dirs = ""

    return os.path.join(a.init_save_path, dirs)


def authorURL(author_id) -> str:
    return (authorInfo % author_id)


def albumURL(album_id) -> str:
    return albumInfo % album_id


def authorIDAndTagsURL(album_id) -> str:
    return authorIDAndTags % album_id


def download_info(func):
    def infoed_func(*args, **kwargs):
        nowThread=threading.currentThread()

        print(f"now enter <{func.__name__}>{type(func)}-IN Thread: {nowThread.getName()}")
        func(*args, **kwargs)
        print(f"now EXIT <{func.__name__}>{type(func)}-IN Thread: {nowThread.getName()}")

    return infoed_func
