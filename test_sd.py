import sounddevice as sd
apis = sd.query_hostapis()
for i, a in enumerate(apis):
    print(f"[{i}] {a['name']}")
