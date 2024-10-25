import requests

microservice_resp = requests.post(
    "http://172.28.31.70:3000/api/v1/posts",
    json={"a": "b"},
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer "
    },
)
print(microservice_resp.text)
