def handler(
    jwt: dict,
    new_data: dict,
    old_data: dict,
    well_known_urls: dict,
    method: str = ""
):
    import requests  
    AUTH_HEADERS = {'Authorization': f"Bearer {jwt}"}
    url=f"{well_known_urls['self']}solutions/q"
    filter_payload = {
        "project": ["name", "short_name", "description", "is_active", "provider__details", "apps__solutions"],
        "filter": { "id": str(new_data['solution']) }
    }
    solution_data = requests.post(url=url, json=filter_payload, headers=AUTH_HEADERS)
    solution_data = solution_data.json().get('data')[0]
    if len(solution_data["apps__solutions"]) == 0:
      raise Exception("Solution must cotain apps before releasing a version")
    new_data["snapshot"] = solution_data

    if new_data['is_sections']: 
      sections_url=f"{well_known_urls['self']}solution_sections/q"
      sections_filter_payload = {
          "filter": { "solution": str(new_data['solution']) }
      }
      sections_data = requests.post(url=sections_url, json=sections_filter_payload, headers=AUTH_HEADERS)

      solution_def = {}
      sections = sections_data.json().get('data')
      for section in sections:
        if section.get("zdl") is not None:
          solution_def[section.get("type")] = section["zdl"][section.get("type")]
      new_data["zdl"] = solution_def

    return new_data
