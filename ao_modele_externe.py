
TOOL_GET_POD_EVENTS = {
    "type": "function",
    "function": {
    "name": "get_pod_events",              # le nom EXACT de ta fonction Python
    "description": (
             "Renvoie les events Kubernetes d'un pod "
            "(OOMKilled, FailedScheduling, BackOff, Failed to pull image…). "
            "À appeler en premier dès qu'un pod a un souci : crash, Pending, redémarrages." 
    ), # une phrase : quand Mistral doit-il l'utiliser ?
    
    "parameters": {
        "type": "object",
        "properties": {
          "pod_name":  {"type": "string", "description": "nom exact du pod, ex: flask-demo-864cc9b79c-ggc6q"},
          "namespace": {"type": "string", "description": "namespace du pod "}
    },
    "required": ["pod_name"]   # namespace a un défaut → pas requis
    }
}
}

TOOL_QUERY_PROMETHEUS = {
    "type": "function",
    "function": {
        "name": "query_prometheus",              # le nom EXACT de ta fonction Python
        "description": (
            "Renvoie la valeur d'une métrique Prometheus. À utiliser pour chiffrer un symptôme sur "
            "une fenêtre : nombre de redémarrages, mémoire, CPU. Fournir une expression PromQL valide."
        ), # une phrase : quand Mistral doit-il l'utiliser ?
    
    "parameters": {
        "type": "object",
        "properties": {
          "promql":  {"type": "string", "description": "Expression PromQL valide, ex: rate(...) ou kube_pod_container_status_restarts_total{pod='...'}"},
    },
    "required": ["promql"]   # namespace a un défaut → pas requis
    }
    }
}

TOOL_SEARCH_LOGS = {
    "type": "function",
    "function": {
    "name": "search_logs", # le nom EXACT de ta fonction Python
    "description": (
            "Renvoie les logs applicatifs récents d'un pod (message d'erreur exact, stack trace). "
            "À appeler quand les events et les métriques ne donnent pas la cause : "
            "il faut voir ce que l'application elle-même a écrit."
    ), # une phrase : quand Mistral doit-il l'utiliser ?

    "parameters": {
        "type": "object",
        "properties": {
          "pod_name":  {"type": "string", "description": "nom exact du pod, ex: flask-demo-864cc9b79c-ggc6q"},
          "namespace": {"type": "string", "description": "namespace du pod "}
    },
    "required": ["pod_name"]   # namespace a un défaut → pas requis
    }
}
}

import requests
import subprocess
import os
os.environ["KUBECONFIG"] = "/home/david/.kube/config"
def get_pod_events(pod_name, namespace="default"):
    r = subprocess.run(
        ["kubectl", "describe","pod", pod_name , "-n", namespace],
        capture_output=True,
        text=True
    )
    return r.stdout



"query prometheus"

def query_prometheus(promql: str):
    url = "http://10.43.115.93:9090/api/v1/query"
    a = requests.get(url, params={"query": promql})
    return a.text



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
    data = a.json()
    logs = [hit["_source"]["log"] for hit in data["hits"]["hits"]]
    return "\n".join(logs)

# annuaire nom (ce que Mistral renvoie) -> fonction Python

TOOLS = {
    "get_pod_events": get_pod_events,
    "query_prometheus": query_prometheus,
    "search_logs": search_logs,
}

# Agent LLM

#import ollama # type: ignore
import json
from groq import Groq
client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": (
          "Tu es un agent de diagnostic Kubernetes. Réponds TOUJOURS en français, "
          "en 5 lignes maximum. Base ta conclusion sur TOUTES les informations "
          "obtenues jusqu'ici (events, métriques, logs), pas seulement le dernier "
          "résultat reçu. Donne un diagnostic clair et une cause probable, "
          "ne pose pas de question à l'utilisateur."
        ),
    },
    {
        "role": "user",
        "content": (
            "Le pod flask-demo-5d9ccbb686-pk74q dans le namespace default "
            "redémarre en boucle. Diagnostique."
        ),
    },
]

reponse = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=messages,
    tools=[TOOL_GET_POD_EVENTS, TOOL_QUERY_PROMETHEUS, TOOL_SEARCH_LOGS],
  )
print(reponse)

while reponse.choices[0].message.tool_calls:
    appel = reponse.choices[0].message.tool_calls[0]
    print(appel)
    nom_tool = appel.function.name
    arguments = json.loads(appel.function.arguments)
    print(nom_tool)
    print(arguments)
    resultat = TOOLS[nom_tool](**arguments)
    print(resultat)
    
    messages.append(reponse.choices[0].message.model_dump(exclude_none=True))
    messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})
  
    reponse = client.chat.completions.create(
      model="openai/gpt-oss-120b",
      messages=messages,
      tools=[TOOL_GET_POD_EVENTS, TOOL_QUERY_PROMETHEUS, TOOL_SEARCH_LOGS],
  )
    
print(reponse.choices[0].message.content)

"""Test des tools:

#print(get_pod_events("flask-demo-864cc9b79c-ggc6q", "default"))
#print(query_prometheus('up'))
#print(search_logs("flask-demo-864cc9b79c-ggc6q"))

"""