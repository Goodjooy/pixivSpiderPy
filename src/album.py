"""
相册信息请求器

暴露的接口
：->load_album_data(inthread:bool=False,tp:ThreadPool=None)
    加载相册信息（进行多次请求（阻塞）（可否异步？））
    可定义异步魔法方法处理
：->download_images(in_thread:bool=False,tp:ThreadPool=None)
    将下载任务添加到线程池
：->adownload_image()->list[Awaitable]
    异步请求器（不知道有没有用）
    生成图片的异步列表
:->is_fit_tags(*tags:str)
    是否符合提供标签
    可以更多，不能更少
"""


from concurrent.futures import ThreadPoolExecutor, Future
import os
import time
from src import albumURL, authorIDAndTagsURL, build_save_path

from requests.sessions import Session, SessionRedirectMixin


from .image import Image


class Album(object):
    def __init__(self, album_id: str, session: Session, init_save_path: str, save_path_struct: int, err_collect=None) -> None:
        self.init_save_path: str = init_save_path
        self.save_path: str = ...

        # 相册信息
        self.aother: str = ...
        self.aother_id: str = ...
        self.album_name: str = ...
        self.album_id: str = album_id
        self.tags: list = []
        #self.images_url: list = []
        self.images: list = []
        self.images_futures = []

        self.session: Session = session
        # 需要保留请求器信息？

        self.err_collect = err_collect

        self.division_type = save_path_struct

        self.load_fetures: list = []

        self.images_download_tp: ThreadPoolExecutor = None

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Album) and o.album_id == self.album_id:
            return True
        return False

    def load_data(self,
                  finished_start_download: bool = False, download_tp: ThreadPoolExecutor = None,
                  in_thread: bool = False, tp: ThreadPoolExecutor = None) -> None:
        """
        加载相册信息，将进行多次请求
        """
        try:
            time.sleep(2)
            if finished_start_download:
                self.images_download_tp = download_tp

            if in_thread:
                t = tp.submit(self.load_author_info)
                self.load_fetures.append(t)
                t = tp.submit(self.load_image_info)
                if finished_start_download:
                    t.add_done_callback(self.start_images_download)
                self.load_fetures.append(t)
            else:
                self.load_author_info()
                self.load_image_info()

        except Exception as info:
            if self.err_collect is not None:
                self.err_collect.add(info)

    def is_done(self):
        """
        检查信息加载是否已经完成
        """
        if len(self.load_fetures) == 0 or len(list(filter(lambda x: not x.done(), self.load_fetures))):
            return True
        return False

    def load_author_info(self):
        try:
            a_and_tags = self.session.get(authorIDAndTagsURL(self.album_id))
            a_and_tags.raise_for_status()

            json_data: dict = a_and_tags.json()

            # 正常
            if not json_data.get("error"):
                self.album_name = json_data.get("body")["illustTitle"]
                self.aother = json_data["body"]["userName"]

                tags_group: dict = json_data.get("body").get("tags")

                self.aother_id = tags_group.get("authorId")

                for tag in tags_group["tags"]:
                    self.tags.append(tag["tag"])

                self.save_path = build_save_path(self, self.division_type)
                if not os.path.exists(self.save_path):
                    os.makedirs(self.save_path, exist_ok=True)

        except Exception as err:
            if self.err_collect is not None:
                self.err_collect.add(err)
            raise

    def load_image_info(self):
        try:
            imag_res = self.session.get(albumURL(self.album_id))
            imag_res.raise_for_status()

            json_data: dict = imag_res.json()

            if not json_data.get("error"):
                body: list = json_data.get("body")

                while not self.load_fetures[0].done():
                    time.sleep(0.5)
                for img in body:
                    t: Image = Image(img["urls"]["original"], self.save_path,
                                     self.session, err_collect=self.err_collect)
                    self.images.append(t)
        except Exception as err:
            if self.err_collect is not None:
                self.err_collect.add(err)
            raise

    def start_images_download(self, ft: Future = None, tp=None):
        """
        开始图像下载
        """
        while not self.load_fetures[0].done() or not self.load_fetures[1].done():
            time.sleep(0.5)
        if tp is not None:
            self.images_download_tp = tp

        for img in self.images:
            img: Image
            # img.save_path=self.save_path
            t = self.images_download_tp.submit(img.run)
            self.images_futures.append(t)
