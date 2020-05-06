import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import start_http_server, push_to_gateway, Gauge, Counter
import time
import json
import requests

NSID = 'b4e9cbec-08e5-4570-b04d-5d17d93221be'


def get_services():
    service_url = 'http://dev-nacos.aeonbuy.com/nacos/v1/ns/service/list?namespaceId=%s&pageNo=1&pageSize=200' % NSID
    r = requests.get(service_url).text
    data = json.loads(r)
    services = data.get('doms')
    services.sort()
    return services


def get_instance_status(svc):
    #    for name in get_services():
    instance_url = 'http://dev-nacos.aeonbuy.com/nacos/v1/ns/instance/list?serviceName=%s&namespaceId=%s' \
                   % (svc, NSID)
    r = requests.get(instance_url).text
    data = json.loads(r)
    instance = data.get('hosts')
    if instance:
        status = instance[0]["valid"]
        ip = instance[0]["ip"]
        return status, ip
    else:
        return [-1, -1]
#        print("service " + svc + " has no instance found.")


REGISTRY = CollectorRegistry(auto_describe=False)
INSTANCE_STATUS = Gauge("nacos_instance_status", "service", ['service_name', 'instance'], registry=REGISTRY)

for i in get_services():
    i_status = get_instance_status(i)
    INSTANCE_STATUS.labels(service_name=i, instance=i_status[1]).inc(i_status[0])

requests.post("http://10.10.36.211:9091/metrics/job/nacos_instance", data=prometheus_client.generate_latest(REGISTRY))
print("metrics data has been sent.")

