"""
进行图像下载请求的类

暴露接口
：->run()
    用于放到线程池里面执行
：->to_dict()
    用于转义成json格式
：->from_json()
    基于json生成代码
"""
import collections
import os
from src import download_info

from requests.models import Response
from requests.sessions import Session


class Image(object):
    def __init__(self, url: str, save_path: str, session: Session, chunk_size: int = 1024, err_collect=None) -> None:
        # 图像请求的URL
        self.url: str = url
        # 图像保存的位置
        self.save_path: str = save_path
        self.file_name: str = ...
        self.file_path: str = ...
        # io区
        self.file_handle = None

        # 迭代器
        self.iter: collections.Iterable = ...

        # 请求区
        self.session: Session = session
        self.respond: Response = ...
        self.target_size: int = 0
        self.chunk_size: int = chunk_size
        self.download_size: int = 0

        # 错误处理器
        self.err_handle = err_collect

        # 部分数据预处理
        self.file_name = os.path.basename(self.url)
        self.save_path = os.path.abspath(self.save_path)if os.path.isabs(
            self.save_path) else self.save_path
        self.file_path = os.path.join(self.save_path, self.file_name)

        if os.path.exists(self.save_path):
            os.makedirs(self.save_path, exist_ok=True)

        # 是否为断点续传
        self .is_recover = False

    def __await__(self) -> None:
        self.run()

    def __call__(self) -> None:
        self.run()

    @download_info
    def run(self) -> None:
        """
        添加到线程池的方法
        1-开始循环下载前，先进行流请求，打开文件，准备好迭代器
        2-在正式下载时，阻塞下载，写入文件
        3-在完成下载后，关闭文件和请求流
        """
        try:
            self.init_download()
            self.main_action()
        except Exception as info:
            if self.err_handle is not None:
                self.err_handle.add(info)
            print(info)
        finally:
            self.exit_download()

    def to_dict(self) -> dict:
        """
        将下载器转换为json
        """
        return{
            "url": self.url,
            "save_path": self.save_path,
            "chunk_size": self.chunk_size
        }

    @staticmethod
    def from_dict(value: dict, session: Session, err_collection=None) -> None:
        """
        基于给定的json格式文件生成下载器
        """
        return Image(value.get("url"),
                     value.get("save_path"),
                     session=session,
                     chunk_size=value.get("chunk_size"),
                     err_collect=err_collection)

    def init_download(self) -> None:
        """
        初始化下载过程，建立下载链接
        """
        # 发送请求
        self.respond = self.session.get(self.url, stream=True)
        # 检查状态码
        self.respond.raise_for_status()
        # 文件大小
        self.target_size = self.respond.headers.get("content-length")
        # 构建请求迭代器
        self.iter = iter(self.respond.iter_content(self.chunk_size))
        # 打开文件
        self.file_handle = open(self.file_path, "wb")

    def main_action(self) -> None:
        """
        下载的主要方法
        """
        while True:
            try:
                data = next(self.iter)
            except StopIteration:
                break
            else:
                # 将data写入文件
                self.file_handle.write(data)
                # 已下载位置递增
                self.download_size += len(data)

                print(f"[{self.download_size}|{self.target_size}]",end="\r")
        print()

    def exit_download(self) -> None:
        """
        下载结束
        """
        if isinstance(self.respond, Response):
            self.respond.close()
        if self.file_handle is not None:
            # 等待文件写入结束
            self.file_handle.flush()
            os.fsync(self.file_handle)
            self.file_handle.close()
