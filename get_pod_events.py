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

print(get_pod_events("flask-demo-864cc9b79c-ggc6q", "default"))