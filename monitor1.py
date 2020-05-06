import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import start_http_server, push_to_gateway, Gauge
import time
import json
import requests
import sys

NS1_ID = 'b4e9cbec-08e5-4570-b04d-5d17d93221be'
#NS2_ID = '9fcacb54-cb66-4751-be4c-b1cf12078415'
NACOS = 'dev-nacos.aeonbuy.com'


def get_services():
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
    instance_url = 'http://%s/nacos/v1/ns/instance/list?serviceName=%s&namespaceId=%s' \
                   % (NACOS, svc, NS1_ID)
    r = requests.get(instance_url).text
    data = json.loads(r)
    instance = data.get('hosts')
    if instance:
        status = instance[0]["valid"]
        ip = instance[0]["ip"]
        return status, ip
    else:
        return [0, 0]
#        print("service " + svc + " has no instance found.")


REGISTRY = CollectorRegistry(auto_describe=False)
INSTANCE_STATUS = Gauge("nacos_instance_status", "service", ['service_name', 'instance', 'namespace'], registry=REGISTRY)

for i in get_services():
    i_status = get_instance_status(i)
    INSTANCE_STATUS.labels(service_name=i, namespace='sit', instance=i_status[1]).inc(i_status[0])


def main():
    requests.post("http://10.10.36.211:9091/metrics/job/nacos_instance", data=prometheus_client.generate_latest(REGISTRY))
    print("metrics data has been sent.")


if __name__ == '__main__':
    while True:
        main()
        time.sleep(15)

