import requests
from rich import print

def download_file(url, destination):
    response = requests.get(url, stream=True)  # Stream the response
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)  # Write file in chunks to avoid memory issues
        print(f"File downloaded successfully: {destination}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")


def download_track(name: str, output: str):
    
    url = "https://spotify-scraper.p.rapidapi.com/v1/track/download"
    querystring = {"track":name}

    headers = {
        "x-rapidapi-key": "8db2800c94mshe39e76b5612a5c9p18e0d2jsnabdee6a6b23b",
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    j = response.json()
    
    mp3_url = j['youtubeVideo']['audio'][0]['url']
    
    download_file(mp3_url, output)
        