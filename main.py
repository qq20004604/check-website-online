import requests
import time
from bs4 import BeautifulSoup
from send_email import SendMailTool
import yaml


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

        with open('config.yml') as file:
            config = yaml.safe_load(file)
        # 发送邮件
        self.SendMailTool = SendMailTool(user=config['smtp']['user'],
                                         password=config['smtp']['password'],
                                         host=config['smtp']['host'],
                                         sender="网站在线检查",
                                         receivers=['20004604@qq.com'])

        print(msg)
        self.check_count = 1
        self.ok_after_error = True
        self.error_count = 0
        self.send_count = 0
        self.url = None

    # 轮询查询
    def run(self):
        while True:
            print(f"%s 开始第 %d 轮检查……" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.check_count))
            is_online = self.check_website_status()
            if is_online:
                # 如果正常后，则重新设置该值为 True
                self.ok_after_error = True
                print(f"{self.web_site} is online.")
            else:
                print(f"{self.web_site} is offline.")

                # 如果这是若干次正常之后的第一次报错。（避免因为同一个错误，重复推送报错邮件）
                if self.ok_after_error is True:
                    # 那么报错次数 +1
                    self.error_count += 1
                    # 则设置该值为 False
                    self.ok_after_error = False
                    print("首次报错，需要推送邮件")
                else:
                    print("依然报错中，无需重复推送邮件")
                # 推送邮件
                self.send_alert()
            print("结束本轮检查")
            time.sleep(self.interval)
            # 检查次数 +1
            self.check_count += 1

    def check_website_status(self):
        try:
            print(f"开始获取%s网站资源" % self.web_site)
            response = requests.get(self.web_site, timeout=10)
            if response.status_code == 200:
                print("网站资源获取成功，开始检查dom节点数量")
                soup = BeautifulSoup(response.text, 'lxml')
                elements = soup.find_all(self.tag_name)
                if len(elements) >= self.min_dom_count:
                    msg = f"dom节点数量符合要求，当前DOM节点数量为：%d，最低节点要求是：%d" % (
                        len(elements), self.min_dom_count)
                    print(msg)
                    return True
                else:
                    msg = f"网站：%s，dom节点数量【不】符合要求，当前DOM节点数量为：%d，最低节点要求是：%d" % (
                        self.web_site, len(elements), self.min_dom_count)
                    print(msg)
                    self.SendMailTool.set_mail_content(header="网站在线检查失败", content=msg)
            else:
                msg = f"网站：%s，网站资源获取失败，状态码：%d" % (self.web_site, response.status_code)
                print(msg)
                self.SendMailTool.set_mail_content(header="网站在线检查失败", content=msg)
            return False
        except requests.exceptions.RequestException as e:
            msg = f"网站：%s，Request error: {e}" % self.web_site
            print(msg)
            self.SendMailTool.set_mail_content(header="网站在线检查失败", content=msg)
            return False

    # 发送提醒信息
    def send_alert(self):
        # 如果推送次数大于等于报错次数，说明推送过了，则无需推送
        if self.send_count >= self.error_count:
            return
        # 发送成功后，加1
        if self.SendMailTool.send_mail() is True:
            print("报错邮件发送成功")
            self.send_count += 1
        else:
            print("报错邮件发送失败")


if __name__ == "__main__":
    target_url = "https://www.baidu.com/"  # 更改为您想要检测的网站URL
    check = CheckWebsiteOnline(web_site=target_url, min_dom_count=100)
    check.run()
