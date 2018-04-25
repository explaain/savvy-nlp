import index, os
from dotenv import load_dotenv
from raven import Client as SentryClient


try:
  # Loads .env into environment variables
  from pathlib import Path  # python3 only
  env_path = Path('.') / '.env'
  load_dotenv(dotenv_path=env_path)
except Exception as e:
  print(e)
  sentry.captureException()

try:
  indexing = os.getenv('SAVVY_INDEXING')
  print(indexing)
  if indexing:
    index.startIndexing()
except Exception as e:
  print(e)
  sentry.captureException()
