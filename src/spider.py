"""
爬虫主要控制类
接受cookies以含有cookies的请求

含有值
2个线程池
    一个请求信息，一个下载
1个session
    负责统一的环境

公开接口
add_artical(*artical_ids:str)
    添加作品
start()
    开始下载
recommand_wandon(level:1)
    推荐列表漫游
"""

from os import SEEK_CUR
from time import sleep

from requests.sessions import session
from src.author import Author
from src import DIVISION_BY_ALBUM_NAME_AND_ID, referer, userAgent
from src.album import Album
from requests import Session
from concurrent.futures import Future, ThreadPoolExecutor


class Spider(object):
    def __init__(self, cookies: dict, save_path="./out") -> None:
        # 请求相关
        self.session: Session = Session()
        self.cookies: dict = cookies

        # 线程池
        self.info_load_tp: ThreadPoolExecutor = ThreadPoolExecutor(8)
        self.image_tp: ThreadPoolExecutor = ThreadPoolExecutor(16)

        # 信息组
        self.albums: list = []
        self.albums_futhures = []

        self.authors: list = []
        self.authors_future = []

        self.save_path = save_path
        self.save_mode: int = DIVISION_BY_ALBUM_NAME_AND_ID

        for cookie in self.cookies:
            self.session.cookies.set(cookie["name"], cookie["value"])
    
        
        self.session.headers["referer"] = referer
        self.session.headers["host"]="www.pixiv.net"
        self.session.headers["user-Agent"] = userAgent

    def add_artical(self, *artical_ids: str) -> list:
        temps = []
        for a_id in artical_ids:
            t = Album(a_id, self.session, self.save_path,
                      self.save_mode)
            if t not in self.albums:
                self.albums.append(t)
                temps.append(t)
        return temps

    def add_author(self, author_id: str, art_range: slice):
        t = Author(author_id, self.session, art_range)
        if t not in self.authors:
            self.authors.append(t)

    def recommand_wandon(level: int = 1):
        pass

    def start(self):
        self.append_author_artical_load(self.authors)
        while len(list(filter(lambda x: not x.done(), self.authors_future))):
            sleep(0.5)

        self.append_album_download(self.albums)

        self.info_load_tp.shutdown()
        self.image_tp.shutdown()

    def set_save_mode(self, save_mode: int = DIVISION_BY_ALBUM_NAME_AND_ID):
        """
        设置文件夹格式
        """
        self.save_mode = save_mode


    def append_author_arts(self, ft: Future):
        """
        完成作者信息请求后的回调函数
        """
        try:
            targets = ft.result()
            self.add_artical(*targets)
        except Exception as err:
            print("[ERR]" ,err.with_traceback(None))

    def append_album_download(self, album_list):
        """
        将提供的列表中的img添加到下载线程池里面
        """
        for album in album_list:
            album: Album
            album.load_data(True, self.image_tp, True, self.info_load_tp)

    def append_author_artical_load(self, author_list):
        for author in author_list:
            author: Author
            t = self.info_load_tp.submit(author.load_artical_list)
            t.add_done_callback(self.append_author_arts)
            self.authors_future.append(t)

            
