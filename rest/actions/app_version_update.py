def handler(jwt: dict, new_data: dict, old_data: dict, well_known_urls: list[str], method: str = ""):
    del new_data["major_version"]
    del new_data["minor_version"]
    del new_data["version"]
    return new_data
