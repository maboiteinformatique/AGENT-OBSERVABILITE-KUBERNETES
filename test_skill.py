from ao import skill_scan_cluster

resultats = skill_scan_cluster()

for pod, diagnostic in resultats.items():
    print(f"=== {pod} ===")
    print(diagnostic)
    print()
