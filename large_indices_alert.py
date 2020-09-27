#!/usr/bin/env python3
import datetime
import pprint
import logging
from elasticsearch import Elasticsearch
from wechatpy.enterprise import WeChatClient

project = "indices_alert"
logging.basicConfig(filename='/tmp/' + project + '.log',
                    format='%(asctime)s %(message)s', level=logging.INFO, filemode='a',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(project)

wechat_client = WeChatClient(
    corp_id='xxxxx_your_corp_id_xxxxxxx',
    secret='xxxxxx_your_corp_secret_xxxxxxxx'
)
es = Elasticsearch(['http://elastic:yourpassword@10.10.10.10:9200'])


def send_wechat_message(content):
    # 发送企业微信应用消息，参考文档 https://work.weixin.qq.com/api/doc/90000/90135/90236
    wechat_client.message.send(AgentID10000, 'UserID1|UserID2|UserID3', msg={
        "msgtype": "text",
        "text": {
            "content": content
        }
    })


def get_large_indices():
    # 获取大于50GB的索引列表
    stats = es.indices.stats()
    indices = stats.get('indices')
    large_list = []
    size_list = []
    for i in indices.items():
        index = i[0]  # 获取索引名
        size = i[1].get('total').get('store').get('size_in_bytes')  # 获取索引大小
        gb_size = int(size / 1024 / 1024 / 1024)  # 转换为GB
        if gb_size >= 50:
            large_list.append(index)
            size_list.append(gb_size)
    result = dict(zip(large_list, size_list))
    return result


def get_date():
    # 获取昨天的日期
    yesterday = datetime.date.today() + datetime.timedelta(-1)
    yesterday = str(yesterday.strftime("%Y.%m.%d"))
    return yesterday


if __name__ == '__main__':
    alert_list = {key: value for key, value in get_large_indices().items() if get_date() in key}  # 过滤出昨日的大索引
    # 格式化
    pp = pprint.PrettyPrinter()
    alert_list = pp.pformat(alert_list)
    alert_list = alert_list.replace('{', '').replace('}', '').replace('\'', "").replace(':', '   ').replace(',', 'GB')
    if alert_list:
        try:
            logger.info(send_wechat_message(alert_list + "\n以上索引超过50GB,请注意!"))
        except Exception as e:
            logger.info(e)
    else:
        logger.info(send_wechat_message('昨日没有超过50GB的索引.'))
