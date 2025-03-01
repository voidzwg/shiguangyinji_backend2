import requests
from django.conf import settings

personal_access_token = settings.SECRETS['personal_access_token']
bot_id = settings.SECRETS['bot_id']
post_url = 'https://api.coze.cn/open_api/v2/chat'

headers = {
    'Authorization': f'Bearer {personal_access_token}',
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Connection': 'keep-alive'
}

payload_base = {
    'bot_id': bot_id,
    'stream': False
}

def send(query, user, conversation_id=''):
    post_payload = payload_base

    if conversation_id != '':
        post_payload['conversation_id'] = conversation_id
    
    post_payload['query'] = query
    post_payload['user'] = user
    post_response = requests.post(post_url, headers=headers, json=post_payload)
    
    if post_response.ok:
        isOk = True
        post_response_data = post_response.json()
        ret_conversation_id = post_response_data['conversation_id']
        ret_content = post_response_data['messages'][0]['content']
        ret_status_code = ''
        ret_err_text = ''
    else:
        isOk = False
        post_response_data = post_response.json()
        ret_conversation_id = ''
        ret_content = ''
        ret_status_code = post_response.status_code
        ret_err_text = post_response.text
    
    return isOk, ret_conversation_id, ret_content, ret_status_code, ret_err_text
