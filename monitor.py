import prometheus_client
from prometheus_client import Gauge
from prometheus_client.core import CollectorRegistry
from flask import Response, Flask

app = Flask(__name__)
requests_total = Gauge("request_count", "Total request cout of the host")


@app.route("/metrics")
def requests_count():
    requests_total.inc()
    # requests_total.inc(2)
    return Response(prometheus_client.generate_latest(requests_total),
                    mimetype="text/plain")


@app.route('/')
def index():
    requests_total.inc()
    return "Hello World"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
