from typing import Text
from src import authorIDAndTagsURL, authorURL
from requests import Session


class Author(object):
    def __init__(self, author_id: str, session: Session, art_range: slice) -> None:
        self.id = author_id
        self.art_range=art_range

        self.session = session

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Author) and o.id == self.id:
            return True
        return False

    def load_artical_list(self):
        self.session.headers.update({"referer":f"https://www.pixiv.net/users/{self.id}"})
        res = self.session.get(authorURL(self.id))
        res.raise_for_status()

        json_data = res.json()

        if not json_data["error"]:
            arts = json_data["body"]["illusts"].keys()
            return list(arts)[self.art_range]
