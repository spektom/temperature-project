#!/usr/bin/python

import Adafruit_DHT, requests, json, sys

if __name__ == "main":
    if len(sys.argv) != 2:
        sys.exit("Usage: %s <Webapp IP address>" % sys.argv[0])

    webapp = sys.argv[1]

    humidity, temperature = tuple(map(lambda x: round(x, 2), Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)))
    data = {"t": temperature, "h": humidity}
    headers = {"Content-type": "application/json"}
    requests.post("http://%s:4001/api/update" % webapp, data=json.dumps(data), headers=headers)

