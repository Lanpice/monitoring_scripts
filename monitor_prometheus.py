#!/usr/bin/env python3
import requests
import json
import time

ROUTING_KEY = "27dcb2c327ed42168d3304f4d48ec76b"  # ENTER EVENTS V2 API INTEGRATION KEY HERE


def trigger_incident():
    # Uses Events V2 API - documentation: https://v2.developer.pagerduty.com/docs/send-an-event-events-api-v2
    header = {
        "Content-Type": "application/json"
    }

    payload = {
        "routing_key": ROUTING_KEY,
        "event_action": "trigger",
        "payload": {
            "summary": "Prometheus down",
            "source": "test:midp-ops-vm-e2-proms002",
            "severity": "critical"
        }
    }

    response = requests.post('https://events.pagerduty.com/v2/enqueue',
                             data=json.dumps(payload),
                             headers=header)

    if response.json()["status"] == "success":
        print('Incident created with dedup key (also known as incident / alert key) of ' + '"' + response.json()[
            'dedup_key'] + '"')
    else:
        print(response.text)  # print error message if not successful


def prometheus_health():
    url = "http://10.10.76.27:9090/-/healthy"  # prometheus health check api
    status = requests.get(url).status_code
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if status != 200:
        print("%s unhealthy!" % now)
    else:
        print("%s It works." % now)
    return status


# 检测到prometheus5分钟内都没有收到200返回，则发送告警
def main():
    code = int(prometheus_health())
    code_list = [200] * 10
    code_list.append(code)
    code_list.pop(0)
    if code_list.count(200) < 1:
        trigger_incident()


if __name__ == '__main__':
    while True:
        main()
        time.sleep(30)