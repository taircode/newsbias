from azureml.core import Workspace
"Upload training data to azure blob storage"

print("Connecting to Azure ML Workspace from config.json...")
ws = Workspace.from_config()

print("Connecting to workspace default datastore...")
ds = ws.get_default_datastore()

print("Uploading train articles")
ds.upload(src_dir="../articles",target_path="./news/articles",overwrite=True)