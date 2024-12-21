```py
translator = EasyGoogleTranslate(
    source_language='en',
    target_language='de',
    timeout=10,
    proxies={
        'http': 'http://your_proxy_address:port',
        'https': 'https://your_proxy_address:port'
    }
)
result = translator.translate('This is an example.')
print(result)
```
