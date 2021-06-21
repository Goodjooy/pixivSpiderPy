import json
from os import read

import selenium
from src import DIVISION_BY_AOTHOR_NAME_WITHOUT_SUB_DIR, author
from src.spider import Spider


def login(driver, userid, pasword):
    driver.get("https://accounts.pixiv.net/login")

    user = driver.find_element_by_xpath(
        "/html/body/div[4]/div[3]/div/form/div[1]/div[1]/input")
    user.clear()
    user.send_keys(userid)
    password = driver.find_element_by_xpath(
        "/html/body/div[4]/div[3]/div/form/div[1]/div[2]/input")
    password.clear()
    password.send_keys(pasword)

    go = driver.find_element_by_xpath(
        "//*[@id=\"LoginComponent\"]/form/button")
    go.click()
    cookie = driver.get_cookies()
    with open("cookies.json", "w") as target:
        json.dump(cookie, target, indent=4)


if __name__ == "__main__":
    from selenium.webdriver import edge, Edge
    import time
    import os
    # option=edge.webdriver()
    prefs = {"profile.managed_default_content_settings.images":2}
    # option.add_argument("--headless")
    driver = Edge("./msedgedriver.exe")
    driver.get("https://www.pixiv.net/")

    if not os.path.exists("cookies.json"):
        login(driver, input("用户名"), input("密码"))

    with open("cookies.json", "r")as f:
        cookies = json.load(f)
        for cookie in cookies:
            #del cookie["domain"]
            driver.add_cookie(cookie)

        res=driver.get("https://accounts.pixiv.net/login")

        if driver.current_url!="https://www.pixiv.net/":
            login(driver,input("用户名"), input("密码"))
        # driver.refresh()

    s = Spider(driver.get_cookies(), "I:\\下载素材\\2021年6月15日")
    s.set_save_mode(DIVISION_BY_AOTHOR_NAME_WITHOUT_SUB_DIR)

    # s.add_author("15847203",slice(11))
    # s.add_artical("84932457","84503628","84758203")
    # s.add_author("4754550",slice(-1))
    # s.add_author("5121919",slice(30))
    # s.add_author("45255077",slice(-1))
    # s.add_author("14496985",slice(5))
    # s.add_artical("12126485",slice(45))
    # s.add_author("30837811",slice(20))
    # s.add_artical("86713169","86677572","86510934",)
    # s.add_author("24234",slice(50))
    # s.add_author("31317880",slice(40))
    # s.add_author("16274829",slice(5))

    # s.add_author("490219",slice(75))
    # s.add_author("27517",slice(128))
    # s.add_author("3036679",slice(75))

    # s.add_author("463194",slice(150))
    # s.add_author("18800957",slice(50))
    # s.add_author("3695323",slice(50))
    # s.add_author("20898295",slice(50))
    # s.add_author("2262943",slice(50))

    # s.add_author("10706782",slice(50))
    # s.add_author("26837253",slice(50))
    # s.add_author("44730209",slice(50))
    # s.add_author("4360832",slice(50))
    # s.add_author("163536​",slice(50))
    #s.add_artical("80249489","76478102","85532594","68454842","87073632")

    #s.add_artical("87033410",
                  #"87073644",
                  #"86963282",
                 # "87052262",
                 # "87033492",
                #  "87073632",
                #  "87033441",
                #  "86965699",
                 # "86965230")
    # s.add_artical("85566269","86847612")
    #s.add_author("35692440",slice(4))
   # s.add_author("16778114",slice(0,None))

    s.add_author("6657532",slice(12))
    cookie = driver.get_cookies()

    driver.close()

    s.start()

    with open("cookies.json", "w") as target:
        json.dump(cookie, target, indent=4)

{
    "GET": {
        "scheme": "https",
        "host": "117-27-114-202.mcdn.bilivideo.cn:480",
                "filename": "/upgcxcode/79/81/262668179/262668179-1-30080.m4s",
                "query": {
                    "expires": "1607517453",
                    "platform": "pc",
                    "ssig": "stFfmYCY-VzQJJhIhQJUaw",
                    "oi": "2102225137",
                    "trid": "a7bdc394062d4880b4b9a792a81f2ae5u",
                    "nfc": "1",
                    "nfb": "maPYqpoel5MI3qOUX6YpRA==",
                    "mcdnid": "1000996",
                    "mid": "14435736",
                    "orderid": "0,3",
                    "agrr": "1",
                    "logo": "A0000001"
                },
        "remote": {
                    "地址": "117.27.114.202:480"
                }
    }
}
