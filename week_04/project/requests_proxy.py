import os
import hashlib
import requests

class RequestsProxy():

    cache_folder = '/Users/maxim/codebase/python/spiced_projects/random-forest-fennel-student-code/week_04/project/cache/'
    __verbose = False

    def verbose():
        RequestsProxy.__verbose = True

    def get(url):

        RequestsProxy.__log('Request %s' % url)

        file_name = RequestsProxy.__build_file_name(url)

        if not os.path.isfile(file_name):

            RequestsProxy.__log('Cache file does not exist. Request from the remote server.')

            RequestsProxy.__ensure_directory()

            result = requests.get(url).text

            f = open(file_name, 'w')
            f.write(result)
            f.close

            RequestsProxy.__log('Result stored in the file %s' % os.path.basename(file_name))

            return result
        else:

            f = open(file_name, 'r')
            result = f.read()
            f.close()

            RequestsProxy.__log('Result returned from cache.')

            return result

    def __transform_to_id(string):
        return hashlib.sha256(string.encode('utf-8')).hexdigest()[:15]

    def __build_file_name(string):
        return RequestsProxy.cache_folder + RequestsProxy.__transform_to_id(string) + '.html'

    def __ensure_directory():
        if not os.path.isdir(RequestsProxy.cache_folder):
            os.makedirs(RequestsProxy.cache_folder)

    def __log(message):
        if RequestsProxy.__verbose:
            print(message)