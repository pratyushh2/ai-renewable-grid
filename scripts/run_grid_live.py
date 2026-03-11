import time
import requests

URL = "http://127.0.0.1:8000/smart-grid-status"

while True:
    try:
        r = requests.get(URL)
        print(r.json())
    except:
        print("API not responding")

    time.sleep(10)