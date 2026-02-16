import yaml

config = None

def load_config():
    with open('config/constants.yaml', 'r') as file:

        if config:
            return config

        try:
            config = yaml.safe_load(file)
            return config
        except yaml.YAMLError as exc:
            print(exc)