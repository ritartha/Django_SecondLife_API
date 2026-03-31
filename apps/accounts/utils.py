import requests
from bs4 import BeautifulSoup
from django.conf import settings


def fetch_sl_profile_image(sl_uuid: str) -> str:
    """Scrape SL profile page to get the profile image URL."""
    if not sl_uuid:
        return ''
    url = f'{settings.SL_PROFILE_BASE_URL}{sl_uuid}'
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return ''
        soup = BeautifulSoup(resp.text, 'html.parser')
        img = soup.find('img', {'id': 'profile_img'})
        if not img:
            meta = soup.find('meta', {'name': 'imageSrc'})
            return meta.get('content', '') if meta else ''
        return img.get('src', '')
    except Exception:
        return ''