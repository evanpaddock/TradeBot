import requests
import base64

def authenticate_user(
    AUTH_URL=DATA["AUTH_URL"],
    APP_CALLBACK_URL=DATA["APP_CALLBACK_URL"],
    APP_KEY=DATA["APP_KEY"],
    APP_SECRET=DATA["APP_SECRET"],
) -> dict[str, str]:
    AUTH_URL = AUTH_URL.replace("APP_KEY", APP_KEY).replace(
        "APP_CALLBACK_URL", APP_CALLBACK_URL
    )

    print(f"Click to authenticate: {AUTH_URL}")
    response_url = input("Paste the redirect URL here: ")
    code = f"{response_url[response_url.index('code=') + 5:response_url.index('%40')]}@"

    headers = {
        "Authorization": f'Basic {base64.b64encode(bytes(f"{APP_KEY}:{APP_SECRET}", "utf-8")).decode("utf-8")}',
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": APP_CALLBACK_URL,
    }

    response = requests.post(
        "https://api.schwabapi.com/v1/oauth/token", headers=headers, data=data
    )
    rD = response.json()
    return {"refreshToken": rD["refresh_token"], "access_token": rD["access_token"]}


def refresh_access_token(
    refreshToken=DATA["refreshToken"],
    APP_KEY=DATA["APP_KEY"],
    APP_SECRET=DATA["APP_SECRET"],
    TOKEN_URL=DATA["TOKEN_URL"],
) -> str:
    headers = {
        "Authorization": f'Basic {base64.b64encode(bytes(f"{APP_KEY}:{APP_SECRET}", "utf-8")).decode("utf-8")}',
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refreshToken,
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    return response.json()["access_token"]


def get_account_info(
    encryted_account_id, accessToken, BASE_URL=DATA["BASE_URL"]
) -> dict[str, str]:
    headers = {"accept": "application/json", "Authorization": f"Bearer {accessToken}"}
    response = requests.get(
        f"{BASE_URL}/accounts/{encryted_account_id}", headers=headers
    )
    return response.json()


def get_account_id(accessToken, BASE_URL=DATA["BASE_URL"]) -> str:
    response = requests.get(
        f"{BASE_URL}/accounts/accountNumbers",
        headers={"Authorization": f"Bearer {accessToken}"},
    )

    return response.json()[0]["hashValue"]
