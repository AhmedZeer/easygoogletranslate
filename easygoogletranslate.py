import concurrent.futures
import requests
import re
import os
import html
import urllib.parse

class EasyGoogleTranslate:
    '''
        Unofficial Google Translate API. 

        This library does not need an API key or something else to use, it's free and simple.
        You can either use a string or a file to translate but the text must be equal to or less than 5000 characters. 
        You can split your text into 5000 characters to translate more.

        Google Translate supports 108 different languages. You can use any of them as source and target language in this application.
        If source language is not specified, it will detect source language automatically.
        This application supports multi-thread translation, you can use it to translate multiple languages at once.
        Detailed language list can be found here:  https://cloud.google.com/translate/docs/languages

        Examples:
            #1: Specify default source and target language at beginning and use it any time.
                translator = EasyGoogleTranslate(
                    source_language='en',
                    target_language='de',
                    timeout=10,
                    proxies={
                        'http': 'http://your_proxy:port',
                        'https': 'https://your_proxy:port'
                    }
                )
                result = translator.translate('This is an example.')
                print(result)

            #2: Don't specify default parameters.
                translator = EasyGoogleTranslate()
                result = translator.translate('This is an example.', target_language='tr', proxies={
                    'http': 'http://your_proxy:port',
                    'https': 'https://your_proxy:port'
                })
                print(result)

            #3: Override default parameters.
                translator = EasyGoogleTranslate(target_language='tr')
                result = translator.translate('This is an example.', target_language='fr', proxies={
                    'http': 'http://your_proxy:port',
                    'https': 'https://your_proxy:port'
                })
                print(result)

            #4: Translate a text in multiple languages at once via multi-threading.
                translator = EasyGoogleTranslate(proxies={
                    'http': 'http://your_proxy:port',
                    'https': 'https://your_proxy:port'
                })
                result = translator.translate(text='This is an example.', target_language=['tr', 'fr', 'de'])
                print(result)

            #5: Translate a file in multiple languages at once via multi-threading.
                translator = EasyGoogleTranslate(proxies={
                    'http': 'http://your_proxy:port',
                    'https': 'https://your_proxy:port'
                })
                result = translator.translate_file(file_path='text.txt', target_language=['tr', 'fr', 'de'])
                print(result)
    '''

    def __init__(self, source_language='auto', target_language='tr', timeout=5, proxies=None):
        """
        Initialize the translator.

        :param source_language: Source language code (default is 'auto' for auto-detection).
        :param target_language: Target language code.
        :param timeout: Request timeout in seconds.
        :param proxies: Dictionary of proxies to use for requests (e.g., {'http': 'http://proxy.com:8080', 'https': 'https://proxy.com:8080'}).
        """
        self.source_language = source_language
        self.target_language = target_language
        self.timeout = timeout
        self.proxies = proxies  # Store proxies
        self.pattern = r'(?s)class="(?:t0|result-container)">(.*?)<'

    def make_request(self, target_language, source_language, text, timeout, proxies=None):
        """
        Make a request to Google Translate.

        :param target_language: Target language code.
        :param source_language: Source language code.
        :param text: Text to translate.
        :param timeout: Request timeout in seconds.
        :param proxies: Proxies to use for this request.
        :return: Translated text.
        """
        escaped_text = urllib.parse.quote(text.encode('utf8'))
        url = f'https://translate.google.com/m?tl={target_language}&sl={source_language}&q={escaped_text}'
        try:
            response = requests.get(url, timeout=timeout, proxies=proxies)
            response.raise_for_status()  # Raise an error for bad status codes
            result = response.text.encode('utf8').decode('utf8')
            result = re.findall(self.pattern, result)
            if not result:
                print('\nError: Unknown error.')
                with open('error.txt', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                exit(1)
            return html.unescape(result[0])
        except requests.exceptions.RequestException as e:
            print(f'\nError: {e}')
            exit(1)

    def translate(self, text, target_language=None, source_language=None, timeout=None, proxies=None):
        """
        Translate text to the target language(s).

        :param text: Text to translate.
        :param target_language: Target language code or list of codes.
        :param source_language: Source language code.
        :param timeout: Request timeout in seconds.
        :param proxies: Proxies to use for this request.
        :return: Translated text or list of translated texts.
        """
        target_language = target_language or self.target_language
        source_language = source_language or self.source_language
        timeout = timeout or self.timeout
        proxies = proxies or self.proxies

        if len(text) > 5000:
            print(f'\nError: It can only detect 5000 characters at once. ({len(text)} characters found.)')
            exit(1)

        if isinstance(target_language, list):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(self.make_request, target, source_language, text, timeout, proxies)
                    for target in target_language
                ]
                return [f.result() for f in concurrent.futures.as_completed(futures)]
        
        return self.make_request(target_language, source_language, text, timeout, proxies)

    def translate_file(self, file_path, target_language=None, source_language=None, timeout=None, proxies=None):
        """
        Translate the contents of a file to the target language(s).

        :param file_path: Path to the file to translate.
        :param target_language: Target language code or list of codes.
        :param source_language: Source language code.
        :param timeout: Request timeout in seconds.
        :param proxies: Proxies to use for this request.
        :return: Translated text or list of translated texts.
        """
        if not os.path.isfile(file_path):
            print('\nError: The file or path is incorrect.')
            exit(1)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return self.translate(text, target_language, source_language, timeout, proxies)
