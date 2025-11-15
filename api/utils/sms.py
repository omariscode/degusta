# utils/sms.py
import requests

token = "aa9ba784-36a7-49e7-ac37-8a838558b133"


def send_sms(message: str, to: str, sender: str = "952276121", schedule: str = None):
    url = "https://api.useombala.ao/v1/messages"
    payload = {
        "message": message,
        "from": sender,
        "to": to,
    }

    if schedule:
        payload["schedule"] = schedule

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        return {"success": True, "data": response.json()}
    else:
        return {"success": False, "error": response.text}
