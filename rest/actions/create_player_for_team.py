async def handler(
    jwt: dict,
    new_data: dict,
    old_data: dict,
    well_known_urls: dict,
    method: str = ""
):
    req_data = {
      "name": str(new_data["name"]),
      "short_name": str(new_data["short_name"]),
      "position": "staff",
      "is_active": True,
      "team": str(new_data["id"]),
    }
    import httpx
    url=f"{well_known_urls['self']}players/"
    AUTH_HEADERS = {
        "Authorization": f"Bearer {jwt}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url=url,json=req_data,headers=AUTH_HEADERS)
    return res
