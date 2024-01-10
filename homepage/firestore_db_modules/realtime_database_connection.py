import requests

def update_water_scheduling(package_key, am_pm, hours, minutes, repeat_days, schedule_type,is_daily):
    firebase_url = "https://sustainasoil-22edf-default-rtdb.firebaseio.com/"
    data_path = f"{schedule_type}/{package_key}.json"
    # Get the existing data from Firebase for the specific package_key
    existing_data_url = f"{firebase_url}/{data_path}"
    existing_data_response = requests.get(existing_data_url)
    existing_data = existing_data_response.json()

    if existing_data:
        existing_data["am_pm"] = am_pm
        existing_data["hours"] = hours
        existing_data["minutes"] = minutes
        for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
            existing_data[day] = repeat_days.get(day)
        existing_data["daily"] = 'true' if is_daily else 'false'

        update_url = f"{firebase_url}/{data_path}"

        # Make a PATCH request to update the data
        response = requests.patch(update_url, json=existing_data)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Indicate success by returning a dictionary
            return {"status": "success", "message": "Data updated successfully"}
        else:
            # Indicate failure by returning a dictionary
            return {"status": "error", "message": f"Failed to update data. Status code: {response.status_code}"}
    else:
        # Indicate package not found by returning a dictionary
        return {"status": "error", "message": f"Package with key {package_key} not found"}


def turning_on_off(schedule_type, package_key, is_on):
    firebase_url = "https://sustainasoil-22edf-default-rtdb.firebaseio.com"
    data_path = f"{schedule_type}/{package_key}.json"
    print(type(is_on))
    existing_data_url = f"{firebase_url}/{data_path}"
    print(existing_data_url)
    existing_data_response = requests.get(existing_data_url)

    if existing_data_response.ok:
        existing_data = existing_data_response.json()

        existing_data["isSchedule"] = is_on

        update_url = f"{firebase_url}/{data_path}"

        # Make a PATCH request to update the data
        response = requests.patch(update_url, json=existing_data)

        # Check if the request was successful (status code 200)
        if response.ok:
            # Indicate success by returning a dictionary

            message = "Schedule is turned on" if is_on else "Schedule is turned off"
            return {"status": "success", "message": message}
        else:
            # Indicate failure by returning a dictionary
            return {"status": "error", "message": f"Failed to update data. Status code: {response.status_code}"}
    else:
        # Indicate package not found by returning a dictionary
        return {"status": "error", "message": f"Package with key {package_key} not found"}

def update_parameter(collection_name,package_key, max_moisture, max_temp, min_moisture, min_temp):
    firebase_url = "https://sustainasoil-22edf-default-rtdb.firebaseio.com/"
    data_path = f"{collection_name}/{package_key}.json"
    # Get the existing data from Firebase for the specific package_key
    existing_data_url = f"{firebase_url}/{data_path}"
    existing_data_response = requests.get(existing_data_url)
    existing_data = existing_data_response.json()

    if existing_data:
        existing_data["max_moisture"] = max_moisture
        existing_data["max_temp"] = max_temp
        existing_data["min_moisture"] = min_moisture
        existing_data["min_temp"] = min_temp

        update_url = f"{firebase_url}/{data_path}"

        # Make a PATCH request to update the data
        response = requests.patch(update_url, json=existing_data)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Indicate success by returning a dictionary
            return {"status": "success", "message": "Data updated successfully"}
        else:
            # Indicate failure by returning a dictionary
            return {"status": "error", "message": f"Failed to update data. Status code: {response.status_code}"}
    else:
        # Indicate package not found by returning a dictionary
        return {"status": "error", "message": f"Package with key {package_key} not found"}

