import os
import hashlib
import requests


class RequestsProxy:

    __verbose = False
    __cache_folder = os.path.dirname(os.path.realpath(__file__)) + '/cache/'

    @staticmethod
    def verbose():
        RequestsProxy.__verbose = True

    @staticmethod
    def set_cache_folder(path):
        RequestsProxy.__cache_folder = path

    @staticmethod
    def get(url):
        RequestsProxy.__log('Request %s' % url)

        file_name = RequestsProxy.__build_file_name(url)

        if not os.path.isfile(file_name):

            RequestsProxy.__log('Cache file does not exist. Request from the remote server.')

            RequestsProxy.__ensure_directory()

            result = requests.get(url).text

            f = open(file_name, 'w')
            f.write(result)
            f.close()

            RequestsProxy.__log('Result stored in the file %s' % file_name)

            return result
        else:

            f = open(file_name, 'r')
            result = f.read()
            f.close()

            RequestsProxy.__log('Result returned from cache file %s' % file_name)

            return result

    @staticmethod
    def __transform_to_id(string: str) -> str:
        return hashlib.sha256(string.encode('utf-8')).hexdigest()[:15]

    @staticmethod
    def __build_file_name(string: str) -> str:
        return RequestsProxy.__cache_folder + RequestsProxy.__transform_to_id(string) + '.html'

    @staticmethod
    def __ensure_directory():
        if not os.path.isdir(RequestsProxy.__cache_folder):
            os.makedirs(RequestsProxy.__cache_folder)

    @staticmethod
    def __log(message):
        if RequestsProxy.__verbose:
            print(message)