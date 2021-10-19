import argparse, requests, re
from bs4 import BeautifulSoup
from scraper_proxy import ScraperProxy
from tqdm import tqdm

def get_args():
    parser = argparse.ArgumentParser(description="Command that scraps lyrics from an external source")
    
    # parser.add_argument('-a', '--artist', help='Artist\'s name', required=True) # TODO: handle artist name
    # parser.add_argument('-???', '--???', help='') # TODO: handle hyperparameters
    parser.add_argument('--refresh-cache', help='refresh cache files', default=False)    

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', help='verbose output', default=False)
    group.add_argument('-q', '--quiet', help='no output', default=False)

    return parser.parse_args()

# incoming/outcomming parameters type
def get_lyrics_urn_by_song_dict(html):
    result = {}
    soup = BeautifulSoup(html, 'html.parser')
    for tr in soup.find('table', class_='tdata').find('tbody').find_all('tr'):
        link = tr.find_all('td')[0].find('a')
        song_name = link.text.lower()
        song_name = re.sub(r'[,\.:\'"]', '', song_name)
        song_name = re.sub(r'\[[\w]+\]', '', song_name) # remove strings like "[live]"
        song_name = song_name.strip()
        result[song_name] = link.attrs['href']

    return result

def main():
    args = get_args()
    # TODO: handle "--refresh-cache" option

    url = 'https://www.lyrics.com/artist.php?name=Guano-Apes&aid=295621&o=1'
    domain = '/'.join(url.split('/')[0:3])

    scriper = ScraperProxy()
    
    html = scriper.get_songs_list_html(url)
    lyrics_urn_by_song = get_lyrics_urn_by_song_dict(html)

    # print(lyrics_urn_by_song)

    for song_name, urn in tqdm(lyrics_urn_by_song.items()):
        lyrics = scriper.get_lyrics(domain + urn)

    # print(lyrics_url_by_song_name)

if __name__ == '__main__':
    main()