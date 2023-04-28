import requests
import time
from bs4 import BeautifulSoup


class CheckWebsiteOnline(object):
    def __init__(self, web_site, interval=60, min_dom_count=100, tag_name="div"):
        # 60秒检查一次
        self.interval = interval
        # 最少dom节点
        self.min_dom_count = min_dom_count
        # dom元素，默认是div
        self.tag_name = tag_name
        # 网页
        self.web_site = web_site
        msg = f"被检查的网站为：%s，检查间隔为：%d秒，检查的DOM类型为：%s，最少DOM数量为：%s" % (
            self.web_site, self.interval, self.tag_name, self.min_dom_count)

        print(msg)
        self.check_count = 1
        self.last_send_time = False
        self.error_count = 0
        self.send_count = 0
        self.url = None

    # 轮询查询
    def run(self):
        while True:
            print(f"%s 开始第 %d 轮检查……" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.check_count))
            is_online = self.check_website_status()
            if is_online:
                print(f"{self.web_site} is online.")
            else:
                print(f"{self.web_site} is offline.")
            print("结束本轮检查")
            time.sleep(self.interval)
            self.check_count += 1

    def check_website_status(self):
        try:
            print("开始获取网站资源")
            response = requests.get(self.web_site, timeout=10)
            if response.status_code == 200:
                print("网站资源获取成功，开始检查dom节点数量")
                soup = BeautifulSoup(response.text, 'lxml')
                elements = soup.find_all(self.tag_name)
                if len(elements) >= self.min_dom_count:
                    print(f"dom节点数量符合要求，当前DOM节点数量为：%d" % len(elements))
                    return True
                else:
                    print(f"dom节点数量【不】符合要求，当前DOM节点数量为：%d" % len(elements))
            else:
                print("网站资源获取失败")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return False


if __name__ == "__main__":
    target_url = "https://www.baidu.com/"  # 更改为您想要检测的网站URL
    check = CheckWebsiteOnline(web_site=target_url)
    check.run()
