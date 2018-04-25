import requests

def slack(message):
  payload = { 'text': message }
  requests.post('https://hooks.slack.com/services/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', json=payload)
