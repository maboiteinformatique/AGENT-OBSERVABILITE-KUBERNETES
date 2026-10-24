"""
curl -s "http://10.43.115.93:9090/api/v1/query?query=up" | head -c 500

"""
import requests
def query_prometheus(promql: str):
    url = "http://10.43.115.93:9090/api/v1/query"
    a = requests.get(url, params={"query": promql})
    return a.text

print(query_prometheus('up'))