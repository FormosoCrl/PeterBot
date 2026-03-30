import requests
from bs4 import BeautifulSoup


def get_trending_repo():
    try:
        url = "https://github.com/trending"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Pillamos el primer repo de la lista
        repo = soup.select_one('article.Box-row')
        title = repo.select_one('h2 a').text.replace('\n', '').replace(' ', '')
        desc = repo.select_one('p').text.strip() if repo.select_one('p') else "No description"
        stars = repo.select_one('a[href$="/stargazers"]').text.strip()

        return {"name": title, "desc": desc, "stars": stars}
    except:
        return {"name": "AutoGPT", "desc": "An autonomous AI agent", "stars": "160k"}