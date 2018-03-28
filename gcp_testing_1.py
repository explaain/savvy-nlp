from google.cloud import storage as google_storage



google_storage_client = google_storage.Client.from_service_account_json(
        'google-cloud-platform-Savvy-credentials.json')
google_bucket = google_storage_client.get_bucket('savvy')
blob = google_bucket.blob('destination_blob_name123')
blob.upload_from_filename('405.jpg')



#
# key = client.key('Person')
#
# entity = datastore.Entity(key=key)
# entity['name'] = 'Your name'
# entity['age'] = 25
# client.put(entity)
