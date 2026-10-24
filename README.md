# Agent IA d'observabilité Kubernetes

Agent de diagnostic qui analyse les pods en problème sur le cluster k8s, en s'appuyant
sur Prometheus (métriques), Elasticsearch (logs) et `kubectl` (events), avec un LLM
hébergé (Groq) pour la synthèse finale en langage naturel.

Projet mentorat : le code est écrit par David, Claude accompagne pas à pas (sauf
indication contraire dans l'historique ci-dessous).

## Fichier principal

Tout le code actif est dans **`ao.py`**. Il contient, dans l'ordre :

1. **3 tools** (fonctions appelables par un LLM) :
   - `get_pod_events(pod_name, namespace="default")` — `kubectl describe pod`, lit les events (OOMKilled, CrashLoopBackOff, FailedScheduling...)
   - `query_prometheus(promql)` — requête HTTP sur l'API Prometheus (`/api/v1/query`)
   - `search_logs(pod_name, namespace="default")` — requête Elasticsearch, renvoie les logs applicatifs récents d'un pod
   - Chaque tool a une description JSON associée (`TOOL_GET_POD_EVENTS`, etc.) et un annuaire `TOOLS` (nom string → fonction Python) pour que le LLM puisse les désigner par leur nom.

2. **`diagnostiquer(probleme)`** — agent "generaliste" : le LLM (Groq, `openai/gpt-oss-120b`) reçoit les 3 tools en option (`tools=[...]`) et **décide lui-même** quel tool appeler et dans quel ordre, en boucle (`while ... tool_calls`), jusqu'à produire une conclusion en texte. Utilisé par le chatbot Streamlit (`main_streamlit.py` / Nova).

3. **`skill_pod_crash(pod_name, namespace="default")`** — skill pour diagnostiquer UN pod déjà identifié comme en panne. Différence clé avec `diagnostiquer()` : c'est **le code Python** qui décide l'ordre des appels (`get_pod_events` toujours, puis `query_prometheus` si `OOMKilled`, ou `search_logs` si `CrashLoopBackOff`/`Error`), pas le modèle. Le LLM n'est appelé **qu'une fois**, à la fin, pour rédiger la conclusion à partir du contexte déjà assemblé (pas de `tools=[...]` dans cet appel).

4. **`get_problem_pods()`** — scanne tout le cluster (`kubectl get pods -A -o json`) et repère seul les pods en `CrashLoopBackOff` / `ImagePullBackOff` / `ErrImagePull` / `OOMKilled`, sans nom de pod fourni en entrée.

5. **`skill_scan_cluster()`** — combine les deux précédents : liste les pods en problème via `get_problem_pods()`, puis appelle `skill_pod_crash` sur chacun. Retourne un dict `{"namespace/nom": diagnostic}`.

## Lancer un test

```bash
cd AGENT-OBSERVABILITE
./venv/bin/python test_skill.py
```

`./venv/bin/python` est l'interpréteur du venv local (pas le Python système, verrouillé
PEP 668) — c'est lui qui a les packages installés (`groq`, `requests`...).
`test_skill.py` importe `skill_scan_cluster`, l'exécute, et affiche chaque diagnostic
proprement (un bloc `=== namespace/nom ===` par pod).

## Chatbot Nova (Streamlit)

```bash
./venv/bin/streamlit run main_streamlit.py
```

Interface de chat qui appelle `diagnostiquer(prompt)` à chaque message — utile pour
poser une question libre plutôt que lancer un scan complet du cluster.

## État actuel / reste à faire

- `skill_scan_cluster` testée avec succès sur des pods `whoami` en OOMKilled (limite
  mémoire volontairement abaissée dans `whoami-test/k8s/whoami.yaml` pour provoquer le
  crash). **Cette limite basse (2Mi) est restée appliquée** sur le cluster — à remettre
  à une valeur normale si on n'a plus besoin de ce scénario de test.
- `query_prometheus` et `search_logs` utilisent des IP `ClusterIP` en dur dans `ao.py`
  (Prometheus, Elasticsearch) — fragile si les Services sont recréés. À remplacer par
  les noms DNS internes (`<service>.<namespace>.svc.cluster.local`).
- Pas de gestion d'erreur sur les tools (ex: timeout HTTP, pod inexistant).
- Pas de couche "skills" au-delà de `skill_pod_crash` / `skill_scan_cluster`.
- Mise en prod (webhook AlertManager en déclencheur, image Docker + Deployment k8s,
  ServiceAccount RBAC read-only dédié, clé Groq en Secret) **différée** — on travaille
  encore l'agent lui-même avant d'y passer.
- Autres fichiers présents dans le dossier (`ao-modele_local.py`, `ao_modele_externe.py`,
  `get_pod_events.py`, `query_prometheus.py`, `search_logs.py`, `resume.py`) sont des
  brouillons/versions antérieures, non branchés sur le code actif.

## Historique détaillé

Le journal complet des sessions (décisions, bugs rencontrés, pédagogie) est dans
`agent-ia-alertmanager.txt`, à lire en début de session avant de reprendre le projet.
