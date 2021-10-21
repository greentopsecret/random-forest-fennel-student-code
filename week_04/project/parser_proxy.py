from parser import Parser
import hashlib
import os
import json


class ParserProxy(Parser):
    __verbose = False
    __cache_folder = os.path.dirname(os.path.realpath(__file__)) + '/cache/parser/'

    @staticmethod
    def verbose():
        ParserProxy.__verbose = True

    @staticmethod
    def set_cache_folder(path: str):
        ParserProxy.__cache_folder = path

    def get_lyrics_url_by_song_dict(self, html: str) -> dict:

        file_name = ParserProxy.__build_file_name(html)

        if not os.path.isfile(file_name):

            ParserProxy.__log('Cache file does not exist')
            ParserProxy.__ensure_directory()

            result = super().get_lyrics_url_by_song_dict(html)

            f = open(file_name, 'w')
            f.write(json.dumps(result))
            f.close()

            ParserProxy.__log('Result stored in the file %s' % file_name)

            return result
        else:

            f = open(file_name, 'r')
            result = f.read()
            f.close()

            ParserProxy.__log('Result returned from cache file %s' % file_name)

            return json.loads(result)

    def parse_lyrics(self, html: str) -> str:

        file_name = ParserProxy.__build_file_name(html)

        if not os.path.isfile(file_name):

            ParserProxy.__log('Cache file does not exist')
            ParserProxy.__ensure_directory()

            result = super().parse_lyrics(html)

            f = open(file_name, 'w')
            f.write(result)
            f.close()

            ParserProxy.__log('Result stored in the file %s' % file_name)

            return result
        else:

            f = open(file_name, 'r')
            result = f.read()
            f.close()

            ParserProxy.__log('Result returned from cache file %s' % file_name)

            return result

    @staticmethod
    def __transform_to_id(string: str) -> str:
        return hashlib.sha256(string.encode('utf-8')).hexdigest()[:15]

    @staticmethod
    def __build_file_name(string: str) -> str:
        return ParserProxy.__cache_folder + ParserProxy.__transform_to_id(string) + '.txt'

    @staticmethod
    def __ensure_directory():
        if not os.path.isdir(ParserProxy.__cache_folder):
            os.makedirs(ParserProxy.__cache_folder)

    @staticmethod
    def __log(message):
        if ParserProxy.__verbose:
            print('[PARSER PROXY]   ' + message)
