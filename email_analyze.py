# -*-coding:utf-8-*- #
# -*-coding:gbk-*- #
from imapclient import IMAPClient
import email
from collections import Counter
import os


class BugEmailAnalyze(object):

    def _connection(self, host):
        try:
            # 建立连接
            self.host = host
            # 'imap.mxhichina.com'
            self.conn = IMAPClient(host=self.host, ssl=False)
            print('已连接服务器')
            return self.conn
        except Exception as e:
            print("ERROR:>>> " + str(e))

    def _login(self):
        try:
            # 登陆
            u_email = input('please input your email:')  # colin.zhang@orderplus.com
            u_pwd = input('please input your password:')
            self.conn.login(u_email, u_pwd)
            print('已登陆')
        except Exception as e:
            print("ERROR:>>> " + str(e))

        # # 1. 查看所有文件夹
        # print(self.conn.list_folders())  # 目录列表
        # print(type(self.conn.list_folders()))  # list
        # print(len(self.conn.list_folders()))  # 12

        # # 2. 查看folder的结构
        # for folder in self.conn.list_folders():
        #     print(folder)  # ((), b'/', 'INBOX') or ((b'\\Trash',), b'/', '已删除邮件')
        #     print(type(folder))  # tuple
        #     print(len(folder))  # 3

        # # 3. 获取INBOX中的邮件数量
        # 先设置文件夹为INBOX
    def get_bugs_folder(self, folder_name):
        # folder_name = '云站线上报错'
        self.conn.select_folder(folder_name, readonly=True)
        # 获取INBOX中的所有邮件ID
        # result_all = self.conn.search()
        # print("邮件ID列表：", result_all)
        # 获取INBOX中的所有未读邮件ID
        self.result_all = self.conn.search()
        # result_unseen = self.conn.search('UNSEEN')
        # print("未读邮件ID列表", result_unseen)
        # # 获取INBOX中的所有发件人为"bug@ops.orderplus.com"的未读邮件ID列表
        # result_unseen = self.conn.search()
        # print("bug未读邮件ID列表", result_unseen)
        return self.result_all

    # 4. 根据Email ID获取邮件内容
    def get_email_body(self, file_path, b_content, get_from, get_value):
        """
        根据Email ID获取邮件内容
        :param file_path:'/Users/zhanglinquan/Desktop/bugs.txt'
        :param b_content: b'BODY[]'
        :param get_from: 'from'
        :param get_value: 'bug@ops.orderplus.com'
        :param get_time: 'from'
        """
        if len(self.result_all):
            for email_id in self.result_all:
                # print(email_id)
                # print(type(email_id))  # int
                # 根据ID获取邮件内容

                msgdict = self.conn.fetch(email_id, b_content)
                # print(type(msgdict))  # collections.defaultdict
                mailbody = msgdict[email_id][b_content]
                # print(mailbody)
                # print(type(mailbody))  # bytes
                # print(chardet.detect(mailbody))  # {'encoding': 'ascii', 'confidence': 1.0, 'language': ''}

                # 从mailbody中使用email获取Message对象
                message = email.message_from_bytes(mailbody)
                # print(type(message))  # email.message.Message
                # 从message对象中解析出subject，from等
                # subject = message.get('subject')
                # print(subject)
                # print(type(subject))  # str
                # print('*' * 180)
                send_from = message.get(get_from)
                # send_time = message.get(get_time)
                # dh = email.header.decode_header(subject)
                # print(dh[0][0])
                # print(type(dh[0][0]))  # bytes
                # print("Subject:", dh[0][0].decode("utf-8", "ignore"))  # Subject: 【监控系统报告】Orderplus-Client【beta】预警

                # 5. 获取邮件内容并转为utf-8,保存到文件中
                if send_from == get_value:
                    for part in message.walk():
                        # print(part)
                        # print(type(part))  # email.message.Message
                        # print(part.get_payload(decode=True))
                        # print(type(part.get_payload(decode=True)))  # bytes
                        is_read = part.get_payload(decode=True).decode("utf-8", "ignore")
                        # print(is_read)
                        # print('*' * 180)

                        # 将结果全部记录到一个文件中
                        file_handle = open(file_path, mode='a')
                        file_handle.write(is_read)

                        file_handle.close()

    # 6. 从bugs.txt中分析数据
    # 6.1. 读取bugs.txt文件内容
    @staticmethod
    def read_bugs(file_path, sub_content):
        """
        :param file_path: '/Users/zhanglinquan/Desktop/bugs.txt'
        :param sub_content: "Exception"
        """
        if os.path.exists(file_path):
            file_handle = open(file_path, mode='r')
            contents = file_handle.readlines()
            bug_list = []
            # print(contents)
            # print(type(contents))  # list
            # print(len(contents))
            # 2. com.orderplus.core.exception.ServiceException的个数
            for content in contents:
                # print(content)
                # print(type(content))  # str
                if sub_content in content:
                    # print(content[47:])
                    # bug_list.append(content[47:])
                    # print('*' * 180)
                    bug_list.append(content)

            # print(bug_list)
            # 统计List中每个元素出现的次数
            counts = Counter(bug_list)
            for kv in dict(counts).items():
                print(kv)

            # 统计完成后，删除文件
            os.remove(file_path)


if __name__ == "__main__":
    b = BugEmailAnalyze()
    b._connection('imap.mxhichina.com')
    b._login()
    b.get_bugs_folder('云站线上报错')
    b.get_email_body('/Users/zhanglinquan/Desktop/bugs.txt', b'BODY[]', 'from', 'bug@ops.orderplus.com')
    b.read_bugs('/Users/zhanglinquan/Desktop/bugs.txt', "Exception")
