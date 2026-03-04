import yaml
import io

def is_raspberry_pi():
    try:
        with io.open('/proc/cpuinfo', 'r') as cpuinfo:
            for line in cpuinfo:
                if line.startswith('Hardware') and 'BCM' in line:
                    return True
                elif line.startswith('Revision'):
                    # Check revision number (specific to Pi models)
                    # More comprehensive checking may involve a lookup table
                    if line.strip().split()[-1] != '00000000': 
                        return True
    except IOError:
        pass
    return False


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