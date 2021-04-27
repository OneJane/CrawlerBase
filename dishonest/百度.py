import json

import requests

url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?resource_id=6899&query=失信人&pn=10&rn=10&ie=utf-8&oe=utf-8'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'Referer': 'https://www.baidu.com/s?ie=UTF-8&wd=%E5%A4%B1%E4%BF%A1%E4%BA%BA'
}

response = requests.get(url, headers=headers)
print(response.status_code)
print(json.dumps(response.json(), sort_keys=True, indent=4, separators=(', ', ': '),ensure_ascii=False))
