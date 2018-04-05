import requests

def track(event_name: str='Unnamed event', event_details: str='', data: dict=None):
  url = 'https://hooks.zapier.com/hooks/catch/3134011/kv4k3j/'
  requests.post(url, json={'event_name': event_name, 'event_details': event_details, 'data': data})

track('Jeremy Clicked a Button', 'He did so proudly', {
  'button_text': 'Give Me Food',
  'number_of_times': 3
})
