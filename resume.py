{
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

{
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

{
"type": "function",
"function": {
    "name": "search_logs",              # le nom EXACT de ta fonction Python
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