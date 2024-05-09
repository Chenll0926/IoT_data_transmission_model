import requests
import json
from data_send import Get_data

personal_info_path = Get_data.personal_info_path['personal_info']

url = 'http://100.81.240.82:5000/api/data'

response = Get_data.http_send_personal_data(url, personal_info_path)

print('Status CODE: ', response.status_code)
print('Response CONTENT: ', response.text)



