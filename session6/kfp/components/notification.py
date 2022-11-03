def notification(namespace: str, run_id: str, pipeline_name: str, status, duration: str, failures: str):
    print(f"""
        Pipeline: {pipeline_name}
        URL: http://localhost:8080/_/pipeline/?ns={namespace}#/runs/details/{run_id}
        Status: {status}
        Duration: {duration} seconds
        Failures: {failures}
    """)
