import os
import hashlib
import requests


class RequestsProxy:

    def __init__(self):
        self.__verbose = False
        self.cache_folder = os.path.dirname(os.path.realpath(__file__)) + '/cache/'

    def verbose(self):
        self.__verbose = True

    def get(self, url: str):

        self.__log('Request %s' % url)

        file_name = self.__build_file_name(url)

        if not os.path.isfile(file_name):

            self.__log('Cache file does not exist. Request from the remote server.')

            self.__ensure_directory()

            result = requests.get(url).text

            f = open(file_name, 'w')
            f.write(result)
            f.close()

            self.__log('Result stored in the file %s' % os.path.basename(file_name))

            return result
        else:

            f = open(file_name, 'r')
            result = f.read()
            f.close()

            self.__log('Result returned from cache.')

            return result

    @staticmethod
    def __transform_to_id(string: str) -> str:
        return hashlib.sha256(string.encode('utf-8')).hexdigest()[:15]

    def __build_file_name(self, string: str) -> str:
        return self.cache_folder + self.__transform_to_id(string) + '.html'

    def __ensure_directory(self):
        if not os.path.isdir(self.cache_folder):
            os.makedirs(self.cache_folder)

    def __log(self, message):
        if self.__verbose:
            print(message)