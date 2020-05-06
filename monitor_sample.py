import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import start_http_server, push_to_gateway, Gauge
import time
import json
import requests
import sys

NS1_ID = '95ea397e-cafd-4da8-a384-7ba1bb507e6f'
NS2_ID = '9fcacb54-cb66-4751-be4c-b1cf12078415'
NACOS = 'nacos.aeonbuy.com'


def get_services():
    service1_url = 'http://%s/nacos/v1/ns/service/list?namespaceId=%s&pageNo=1&pageSize=200' % (NACOS, NS1_ID)
    service2_url = 'http://%s/nacos/v1/ns/service/list?namespaceId=%s&pageNo=1&pageSize=200' % (NACOS, NS2_ID)
    r1 = requests.get(service1_url).text
    r2 = requests.get(service2_url).text
    data1 = json.loads(r1)
    data2 = json.loads(r2)
    s1 = data1.get('doms')
    s2 = data2.get('doms')
    services = s1 + s2
    if services:
        services.sort()
        return services
    else:
        print('please check namespace id or nacos domain.')
        sys.exit(1)


def get_instance_status(svc):
    instance_url1 = 'http://%s/nacos/v1/ns/instance/list?serviceName=%s&namespaceId=%s' \
                   % (NACOS, svc, NS1_ID)
    instance_url2 = 'http://%s/nacos/v1/ns/instance/list?serviceName=%s&namespaceId=%s' \
                   % (NACOS, svc, NS2_ID)
    r1 = requests.get(instance_url1).text
    r2 = requests.get(instance_url2).text
    data1 = json.loads(r1)
    data2 = json.loads(r2)
    instance1 = data1.get('hosts')
    instance2 = data2.get('hosts')
    instance = instance1 + instance2
    if instance:
        status = instance[0]["valid"]
        ip = instance[0]["ip"]
        return status, ip
    else:
        return [-1, -1]
#        print("service " + svc + " has no instance found.")


REGISTRY = CollectorRegistry(auto_describe=False)
INSTANCE_STATUS = Gauge("nacos_instance_status", "service", ['service_name', 'instance', 'namespace'], registry=REGISTRY)

for i in get_services():
    i_status = get_instance_status(i)
    INSTANCE_STATUS.labels(service_name=i, namespace='prod', instance=i_status[1]).inc(i_status[0])


def main():
    requests.post("http://10.10.36.211:9091/metrics/job/nacos_instance", data=prometheus_client.generate_latest(REGISTRY))
    print("metrics data has been sent.")


if __name__ == '__main__':
    while True:
        main()
        time.sleep(15)

