import requests
import json
import datetime

from config import BOT_AUTH_PARAMS
from config import BACKEND_HOST, BACKEND_PORT


def authorize_bot(bot_auth_params=BOT_AUTH_PARAMS):
    with requests.post(f'http://{BACKEND_HOST}:{BACKEND_PORT}/api/accounts/sign_in', json=bot_auth_params) as r:
        if r.status_code == 200:
            content = r.content
            decoded = content.decode("utf-8")
            sign_in_response = json.loads(decoded)
            token = sign_in_response["data"]["token"]
            return token
        else:
            r.raise_for_status()


# List Profiles
def check_tenant_auth(tenant_telegram_id, token):
    with requests.get(
            f'http://{BACKEND_HOST}:{BACKEND_PORT}/api/bots/tenants/?telegram_id={tenant_telegram_id}',
            headers={"Authorization": f"Bearer {token}"}) as r:
        if r.ok:
            content = r.content
            decoded = content.decode("utf-8")
            sign_in_response = json.loads(decoded)
            body = sign_in_response["data"]
            if len(body) == 0:
                return False
            else:
                return True
        else:
            return r.status_code


# List Modules
def list_tenant_modules(tenant_telegram_id, token):
    with requests.get(
            f'http://{BACKEND_HOST}:{BACKEND_PORT}/api/bots/properties?telegram_id={tenant_telegram_id}',
            headers={"Authorization": f"Bearer {token}"}
    ) as r:
        if r.status_code == 200:
            content = r.content
            decoded = content.decode("utf-8")
            sign_in_response = json.loads(decoded)
            body = sign_in_response["data"]
            prettify_response = _prettify_tenant_modules(body)
            return prettify_response, body
        else:
            return r.status_code


def _prettify_tenant_modules(owner_properties):
    if len(owner_properties) == 0:
        return "No active contracts"
    else:
        num_properties_template = f"Modules for rent: {len(owner_properties)}\n\n"
        module_template = "Module #*{id}*\n{name}\nПо адресу {adress}\n\n"
        result = ""
        result += num_properties_template

        for owner_property in owner_properties:
            result += module_template.format_map(owner_property)

        result += "Select the module number for which you want to put meters"

        return result


def list_module_meters(property_id, token):
    with requests.get(
            f'http://{BACKEND_HOST}:{BACKEND_PORT}/api/bots/properties/{property_id}/meters/',
            headers={"Authorization": f"Bearer {token}"}
    ) as r:
        if r.status_code == 200:
            content = r.content
            decoded = content.decode("utf-8")
            sign_in_response = json.loads(decoded)
            body = sign_in_response["data"]
            prettify_response = _prettify_module_meters(body)
            return prettify_response, body
        else:
            return r.status_code


def get_module_meter(property_id, meter_id, token):
    with requests.get(
            f'http://{BACKEND_HOST}:{BACKEND_PORT}/api/bots/tenants/properties/{property_id}/meters/{meter_id}/',
            headers={"Authorization": f"Bearer {token}"}
    ) as r:
        if r.status_code == 200:
            content = r.content
            decoded = content.decode("utf-8")
            sign_in_response = json.loads(decoded)
            body = sign_in_response["data"]
            return body
        else:
            return r.status_code


def _prettify_module_meters(list_meters):
    if len(list_meters) == 0:
        return "This month this module has no meters for which you need to put meters"
    else:
        num_meters_template = f"Available meters: {len(list_meters)}\n\n"
        meter_template = "Meter *{name}*\n"

        result = ""
        result += num_meters_template
        for meter in list_meters:
            result += meter_template.format_map(meter)

        result += "\nSelect the meter for which you want to transmit readings"

        return result


def list_meter_transactions(property_id, meter_id, token):
    with requests.get(
            f'http://{BACKEND_HOST}:{BACKEND_PORT}/api/bots/properties/{property_id}/meters/{meter_id}/transactions/',
            headers={"Authorization": f"Bearer {token}"}
    ) as r:
        if r.status_code == 200:
            content = r.content
            decoded = content.decode("utf-8")
            sign_in_response = json.loads(decoded)
            body = sign_in_response["data"]
            return body
        else:
            return r.status_code


def create_meter_transaction(property_id, meter_id, value, token):
    current_date = datetime.date.today()
    data = {
        "transaction": {
            "value": value,
            "month": current_date.month,
            "year": current_date.year,
        }
    }
    with requests.post(
            f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/bots/properties/{property_id}/meters/{meter_id}/transactions/",
            headers={"Authorization": f"Bearer {token}"},
            json=data
    ) as r:
        return r.status_code


def get_last_module_contract(module_id, token):
    with requests.get(
            f'http://{BACKEND_HOST}:{BACKEND_PORT}/api/bots/properties/{module_id}/contract/',
            headers={"Authorization": f"Bearer {token}"}
    ) as r:
        if r.status_code == 200:
            content = r.content
            decoded = content.decode("utf-8")
            sign_in_response = json.loads(decoded)
            body = sign_in_response["data"]
            return body['tenant_id']
        else:
            return r.status_code


def claim_invitation_code(claim_code, telegram_id, token):
    data = {
        "code": claim_code,
        "telegram_id": telegram_id
    }
    with requests.post(
            f'http://{BACKEND_HOST}:{BACKEND_PORT}/api/bots/tenants/',
            headers={"Authorization": f"Bearer {token}"},
            json=data
    ) as r:
        """200 – new user
           422 – user already exist
           else error         
        """
        return r.status_code


def update_tenant(telegram_id, first_name, last_name, patronymic, token):
    data = {
        "tenant": {
            "first_name": first_name,
            "last_name": last_name,
            "patronymic": patronymic
        }
    }
    with requests.put(
            f'http://{BACKEND_HOST}:{BACKEND_PORT}/api/bots/tenants/?telegram_id={telegram_id}',
            headers={"Authorization": f"Bearer {token}"},
            json=data
    ) as r:
        if r.status_code == 200:
            content = r.content
            decoded = content.decode("utf-8")
            sign_in_response = json.loads(decoded)
            body = sign_in_response["data"]
            prettify_response = _prettify_update_tenant_response(body)
            return prettify_response, body
        else:
            return r.status_code


def _prettify_update_tenant_response(update_tenant_response: dict):
    pretty_response = f"*Second Name*: {update_tenant_response['last_name']}\n" \
                      f"*Name*: {update_tenant_response['first_name']}\n" \
                      f"*Patronymic*: {update_tenant_response['patronymic']}\n"
    return pretty_response
