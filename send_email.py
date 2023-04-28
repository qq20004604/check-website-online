# 发送邮件
import os
import time
import sys
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import yagmail

# 创建目录
if not os.path.isdir('log'):
    os.mkdir('log')


def error_log(msg):
    with open('./log/send-mail-err.log', 'a') as f:
        f.write('%s||%s：%s\n' % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            sys._getframe(1).f_code.co_name,  # 执行error_log这个函数的函数名字，即上一级函数
            msg
        ))


def log(msg):
    with open('./log/send-mail.log', 'a') as f:
        f.write('%s||%s：%s\n' % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            sys._getframe(1).f_code.co_name,  # 执行error_log这个函数的函数名字，即上一级函数
            msg
        ))


# 目前遗留问题
# 1、发件人是乱码，
class SendMailTool(object):
    def __init__(self, user, password, host, sender='test', receivers=None):
        if not user or not password or not host:
            raise ValueError("生成实例时，必须传送 user, password, host 三个字段，作为邮件服务器的配置，不然无法使用。")
        if receivers is None:
            receivers = []
        self.mail_sender = yagmail.SMTP(user=user,
                                        password=password,
                                        host=host)
        self.sender = sender
        self.receivers = receivers
        self.message = None
        self.content = ''

    # 设置接收者的邮箱
    def set_receivers(self, receivers):
        if isinstance(receivers, list):
            self.receivers = receivers
        else:
            raise ValueError("Receivers should be a list of email addresses")

    # 发送邮件，发生成功返回True
    def set_mail_content(self, header, content):
        self.message = {
            'header': header,
            'content': content,
        }

    def send_mail(self):
        if self.message is None:
            msg = '发送失败，缺少发送内容，发送者：%s，接受者：%s，内容:%s\n' % (
                self.sender, str(self.receivers), self.content)
            print(msg)
            error_log(msg)
            return False
        # 使用'localhost'上的SMTP服务器尝试发送邮件
        try:
            # 收件人设置为默认收件人，然后提供标题和内容
            self.mail_sender.send(to=self.receivers,
                                  subject=self.message['header'],
                                  contents=self.message['content'])

            # 如果邮件发送成功，则记录日志并返回True
            log('success，发送者：%s，接受者：%s，内容:%s\n' % (self.sender, str(self.receivers), self.content))
            # 发送成功后，将内容重置为空
            self.message = None
            return True

        # 如果发送邮件过程中出现smtplib.SMTPException异常
        except smtplib.SMTPException as e:
            # 记录错误日志，包括异常信息、发件人、收件人和邮件内容
            error_log('error，报错信息：%s，发送者：%s，接受者：%s，内容:%s\n' % (
                str(e), self.sender, str(self.receivers), self.content))

            # 打印错误提示信息
            print("Error: 无法发送邮件")
            # 发送成功后，将内容重置为空
            self.message = None
            # 返回False表示邮件发送失败
            return False
