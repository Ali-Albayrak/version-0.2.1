def handler(
  jwt: dict,
  new_data: dict,
  old_data: dict,
  well_known_urls: dict,
  method: str = ""
):
    import requests, jsonschema
    from fastapi import HTTPException
    AUTH_HEADERS = {'Authorization': f"Bearer {jwt}"}
    apps_url=f"{well_known_urls['self']}apps/q"
    apps_filter_payload = {
        "project": ["name", "short_name", "description", "status", "public", "is_active", "provider__details"],
        "filter": { "id": str(new_data['app']) }
    }
    app_data = requests.post(url=apps_url, json=apps_filter_payload, headers=AUTH_HEADERS)
    new_data["snapshot"] = app_data.json().get('data')[0]
    if new_data['is_sections']: 
      sections_url=f"{well_known_urls['self']}sections/q"
      sections_filter_payload = {
          "filter": { "app": str(new_data['app']) }
      }
      sections_data = requests.post(url=sections_url, json=sections_filter_payload, headers=AUTH_HEADERS)
      generated_sections = {
        "web": "web-app",
        "data" :"rest"
      }
      app_def = {
        "id": "REL2023",
        "schemaVersion": float(0.1),
        "app" : {
          "name": new_data['snapshot']["short_name"].replace(' ', '').replace('_', '').lower(),
          "provider": new_data['snapshot']["provider__details"]["short_name"].replace(' ', '').replace('_', '').lower(),
          "version": float(new_data["version"])
        },
        "generate": []
      }
      sections = sections_data.json().get('data')
      is_generate = False
      generatable_list = ["web", "data", "services"]
      for i in sections:
        if i.get("zdl") is not None:
          app_def[i.get("type")] = i.get("zdl")[i.get("type")]
          if i.get("type") in generated_sections.keys():
            app_def["generate"].append(generated_sections[i.get("type")])
          if i.get("type") in generatable_list:
            is_generate = True

      if not is_generate:
        raise HTTPException(status_code=400, detail="Error: at least one of data, web or services sections must be implemented to make an app version")

      # validate ZDL
      try:
        schema_res = requests.get("https://storage.googleapis.com/zaekoder-dev-schemas/zdl_0_1_schema.json")
        schema_res.raise_for_status()  # Raise an exception for HTTP errors
        jsonschema.validate(instance=app_def, schema=schema_res.json())
        print("Validation successful: ZDL is valid")
      except requests.exceptions.RequestException as e:
          raise HTTPException(status_code=400, detail="Failed fetching ZDL schema")
      except jsonschema.exceptions.ValidationError as e:
          raise HTTPException(status_code=400, detail=f"App definition is not matching ZDL schema version, details:{e}")

      new_data["zdl"] = app_def
    return new_data
