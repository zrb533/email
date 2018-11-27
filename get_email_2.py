# -*-coding:utf-8-*- #
# -*-coding:gbk-*- #
from imapclient import IMAPClient
import email
import time
import chardet
from collections import Counter
import os

try:
    # 建立连接
    conn = IMAPClient(host='imap.mxhichina.com', ssl=False)
    print('已连接服务器')
    # 登陆
    u_email = input('please input your email:')  # colin.zhang@orderplus.com
    u_pwd = input('please input your password:')
    conn.login(u_email, u_pwd)
    print('已登陆')
except Exception as e:
    print("ERROR:>>> " + str(e))

# # 1. 查看所有文件夹
# print(conn.list_folders())  # 目录列表
# print(type(conn.list_folders()))  # list
# print(len(conn.list_folders()))  # 12

# # 2. 查看folder的结构
# for folder in conn.list_folders():
#     print(folder)  # ((), b'/', 'INBOX') or ((b'\\Trash',), b'/', '已删除邮件')
#     print(type(folder))  # tuple
#     print(len(folder))  # 3

# 3. 获取INBOX中的邮件数量
# 先设置文件夹为INBOX
conn.select_folder('INBOX', readonly=True)
# 获取INBOX中的所有邮件ID
# result_all = conn.search()
# print("邮件ID列表：", result_all)
# 获取INBOX中的所有未读邮件ID
result_unseen = conn.search('UNSEEN')
print("未读邮件ID列表", result_unseen)
# # 获取INBOX中的所有发件人为"bug@ops.orderplus.com"的未读邮件ID列表
# result_unseen = conn.search()
# print("bug未读邮件ID列表", result_unseen)

# 4. 根据Email ID获取邮件内容
if len(result_unseen):
    for email_id in result_unseen:
        # print(email_id)
        # print(type(email_id))  # int
        # 根据ID获取邮件内容
        msgdict = conn.fetch(email_id, b'BODY[]')
        # print(type(msgdict))  # collections.defaultdict
        mailbody = msgdict[email_id][b'BODY[]']
        # print(mailbody)
        # print(type(mailbody))  # bytes
        # print(chardet.detect(mailbody))  # {'encoding': 'ascii', 'confidence': 1.0, 'language': ''}

        # 从mailbody中使用email获取message对象
        message = email.message_from_bytes(mailbody)
        # print(type(message))  # email.message.Message
        # 从message对象中解析出subject，from等
        # subject = message.get('subject')
        # print(subject)
        # print(type(subject))  # str
        # print('*' * 180)
        send_from = message.get('from')
        # dh = email.header.decode_header(subject)
        # print(dh[0][0])
        # print(type(dh[0][0]))  # bytes
        # print("Subject:", dh[0][0].decode("utf-8", "ignore"))  # Subject: 【监控系统报告】Orderplus-Client【beta】预警

    # 5. 获取邮件内容并转为utf-8,保存到文件中
        # 当前时间的时间戳
        now_time = int(time.time())

        if send_from == 'bug@ops.orderplus.com':
            for part in message.walk():
                # print(part)
                # print(type(part))  # email.message.Message
                # print(part.get_payload(decode=True))
                # print(type(part.get_payload(decode=True)))  # bytes
                is_read = part.get_payload(decode=True).decode("utf-8", "ignore")
                # print(is_read)
                # print('*' * 180)

                # 将结果全部记录到一个文件中
                file_handle = open('/Users/zhanglinquan/Desktop/bugs.txt', mode='a')
                file_handle.write(is_read)

                file_handle.close()


# 6. 从bugs.txt中分析数据
# 6.1. 读取bugs.txt文件内容
if os.path.exists('/Users/zhanglinquan/Desktop/bugs.txt'):
    file_handle = open('/Users/zhanglinquan/Desktop/bugs.txt', mode='r')
    contents = file_handle.readlines()
    bug_list = []
    # print(contents)
    # print(type(contents))  # list
    # print(len(contents))
    # 2. com.orderplus.core.exception.ServiceException的个数
    for content in contents:
        # print(content)
        # print(type(content))  # str
        if "com.orderplus.core.exception.ServiceException" in content:
            # print(content[47:])
            bug_list.append(content[47:])
            # print('*' * 180)

    # print(bug_list)
    count = Counter(bug_list)
    print(dict(count))

    os.remove('/Users/zhanglinquan/Desktop/bugs.txt')




