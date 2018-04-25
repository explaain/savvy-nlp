import requests

def slack(message: str=None):
  if not message:
    return None
  payload = { 'text': message }
  return requests.post('https://hooks.slack.com/services/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', json=payload)
