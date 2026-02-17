import yaml

config = False

def load_config():
    global config
    
    if config:
        return config
    
    with open('config/constants.yaml', 'r') as file:

        try:
            config = yaml.safe_load(file)
            return config
        except yaml.YAMLError as exc:
            print(exc)