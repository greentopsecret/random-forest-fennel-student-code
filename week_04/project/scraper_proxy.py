from scraper_remote import ScraperRemote
import os
import hashlib

class ScraperProxy(ScraperRemote):

    cache_folder = './cache/'

    def __init__(self) -> None:
        super().__init__()

    def get_songs_list_html(self, url):

        print('Getting list of songs from %s' % url)

        file_name = self.__build_file_name(url)

        if not os.path.isfile(file_name):

            ScraperProxy.__ensure_directory()

            result = super().get_songs_list_html(url)

            f = open(file_name, 'w')
            f.write(result)
            f.close

            return result
        else:
            f = open(file_name, 'r')
            result = f.read()
            f.close()
            return result

    # TODO: refactor get_lyrics and get_songs_list_html
    def get_lyrics_html(self, url):

        file_name = self.__build_file_name(url)

        if not os.path.isfile(file_name):

            ScraperProxy.__ensure_directory()

            result = super().get_lyrics_html(url)

            f = open(file_name, 'w')
            f.write(result)
            f.close

            return result
        else:
            f = open(file_name, 'r')
            result = f.read()
            f.close()
            return result

    def __transform_to_id(self, string):
        return hashlib.sha256(string.encode('utf-8')).hexdigest()[:15]

    def __build_file_name(self, string):
        return self.cache_folder + self.__transform_to_id(string) + '.txt'
    
    def __ensure_directory():
        if not os.path.isdir(ScraperProxy.cache_folder):
            os.makedirs(ScraperProxy.cache_folder)