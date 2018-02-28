import index, bugsnag

bugsnag.configure(
    api_key="d0731cc66b977d432f6e328d4952c168",
    project_root="/path/to/your/app",
)

index.startIndexing()
