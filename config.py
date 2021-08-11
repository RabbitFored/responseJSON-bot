import os
import yaml

secrets_path = "secrets.yaml"
ENV = bool(os.environ.get('ENV', False))
if ENV:

    apiID = os.environ.get('apiID', None)
    apiHASH = os.environ.get('apiHASH', None)
    botTOKEN = os.environ.get('botTOKEN', None)

    MongoDB_URI = os.environ.get("MongoDB_URI", "")
    database = os.environ.get("database", None)
    user_collection = os.environ.get('userCollection', "")
    group_collection = os.environ.get('groupCollection', "")
    collection = {'user': user_collection, 'group': group_collection}

elif os.path.isfile(secrets_path):
    yaml_file = open(secrets_path, 'r')
    yaml_content = yaml.load(yaml_file, Loader=yaml.FullLoader)
    apiID = yaml_content['telegram'][0]['apiID']
    apiHASH = yaml_content['telegram'][1]['apiHASH']
    botTOKEN = yaml_content['telegram'][2]['botTOKEN']

    MongoDB_URI = yaml_content['MongoDB'][0]['URI']
    database = yaml_content['MongoDB'][1]["database"]
    collection = yaml_content['MongoDB'][2]["collection"]
    print(collection)

else:
    print(
        'This app is not configured correctly. Check README or contact support team.'
    )
    quit(1)
