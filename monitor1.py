import time
import json
import sys
import requests
import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import Gauge


NS1_ID = '95ea397e-cafd-4da8-a384-7ba1bb507e6f'
# NS2_ID = '9fcacb54-cb66-4751-be4c-b1cf12078415'
NACOS = 'nacos.aeonbuy.com'


def get_services():
    """获取nacos服务列表"""
    service_url = 'http://%s/nacos/v1/ns/service/list?namespaceId=%s&pageNo=1&pageSize=200' % (NACOS, NS1_ID)
    r = requests.get(service_url).text
    data = json.loads(r)
    services = data.get('doms')
    if services:
        services.sort()
        return services
    else:
        print('please check namespace id or nacos domain.')
        sys.exit(1)


def get_instance_status(svc):
    """获取nacos实例信息"""
    instance_url = 'http://%s/nacos/v1/ns/instance/list?serviceName=%s&namespaceId=%s' % (NACOS, svc, NS1_ID)
    r = requests.get(instance_url).text
    data = json.loads(r)
    instances = data.get('hosts')  # 获取实例列表
    if instances:
        # 多实例处理
        health = {}
        for instance in instances:
            status = instance.get("healthy")
            ip = instance.get("ip")
            health[ip] = status
        return health
    else:
        return {'Null': 0}


REGISTRY = CollectorRegistry(auto_describe=False)
INSTANCE_STATUS = Gauge("nacos_instance_status", "service", ['service_name', 'instance', 'namespace'],
                        registry=REGISTRY)

# 获取监控数据并代入labels
for i in get_services():
    i_status = get_instance_status(i)
    for k, v in i_status.items():
        INSTANCE_STATUS.labels(service_name=i, namespace='prod', instance=k).inc(v)


def main():
    """将监控数据发送给Pushgateway"""
    requests.post("http://10.10.76.28:9091/metrics/job/nacos_instance_backend",
                  data=prometheus_client.generate_latest(REGISTRY))
    print("metrics data has been sent.")


if __name__ == '__main__':
    while True:
        main()
        time.sleep(15)
