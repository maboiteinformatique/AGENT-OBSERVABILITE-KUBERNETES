"""la fonction search_logs(pod_name, namespace="default") 
autour de ça (url + requests.post(url, json=body) + return 
  ...text), puis teste sur flask-demo-864cc9b79c-ggc6q.

def query_prometheus(promql):
    url = "http://10.43.115.93:9090/api/v1/query"
    a = requests.get(url, params={"query": promql})
    return a.text"""

import requests
def search_logs(pod_name, namespace = "default"):
    url = "http://10.43.31.138:9200/logstash-*/_search"
    body = {
        "size": 20,
        "sort": [{"@timestamp": "desc"}],
        "query": {
            "bool": {
                "filter": [
                    {"term": {"kubernetes.pod_name.keyword": pod_name}},
                    {"term": {"kubernetes.namespace_name.keyword": namespace}}
                ]
            }
        }
    }
    a = requests.post(url, json=body)
    return a.text

print(search_logs("flask-demo-864cc9b79c-ggc6q"))

