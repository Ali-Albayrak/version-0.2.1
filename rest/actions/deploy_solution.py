def handler(
    jwt: dict,
    new_data: dict,
    old_data: dict,
    well_known_urls: dict,
    method: str = ""
):
    req_data = {"deployment_id": str(new_data["id"])}
    import requests
    url="http://zekoder-zeagent-operator-service.zestudio-dev.svc.cluster.local/deploy"
    AUTH_HEADERS = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    return requests.post(url=url, json=req_data, headers=AUTH_HEADERS).json()
