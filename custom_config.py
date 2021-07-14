
import os
from typing import Optional
import pulumi
import yaml

class CustomConfig:
    """
    Below is an example of a user-defined config to be used with a pulumi python program. Only a handful of "get" methods have been
    re-created below and the rest would need to be written, as the need arises.
    
    Note: this "config" is user-defined, so any schema/standard can be used to store the configuration items
    This example will use the pulumi standard of:
        config:
            namespace:key value
    """
    config: dict()
    default_config: dict()
    pulumi_config: pulumi.Config
    bag_name: str

    def __init__(self, bag_name: Optional[str] = None) -> None:
        """
        Using the stack name, search for a single configuration to be used to extend the "default" config
        Stack names should follow the {environment}-{identifier}. Eg- prod-my_stack
        This results in ./prod/my_stack.yaml being loaded into a dictionary
        Pulumi config is also loaded with an optional bag_name to specify a unique bag. If bag_name is None, the project name (pulumi default) will be used
        """
        if not bag_name:
            self.bag_name = pulumi.get_project()
        else:
            self.bag_name = bag_name

        stack = pulumi.get_stack()
        stack_pieces = stack.split('-')
        if len(stack_pieces) != 2:
            raise Exception('Stack name must the format {stage}-{customer}')

        customer_path = os.path.join(os.getcwd(), "customer_config")
        if not os.path.exists(customer_path):
            raise Exception(f'Customer config path at {customer_path} does not exist')

        config_file = os.path.join(customer_path, stack_pieces[0], stack_pieces[1]) + ".yaml"
        default_config_file = os.path.join(customer_path, 'default.yaml')

        pulumi.log.debug(f'Loading configuration file from {config_file}')
        with open(config_file) as file:
            self.config = yaml.full_load(file)

        """follow pulumi's yaml configuration schema, if its configured as such"""
        if 'config' in self.config:
            self.config = self.config['config']

        if os.path.exists(default_config_file):
            pulumi.log.debug(f'Loading configuration file from {default_config_file}')
            with open(default_config_file) as file:
                self.default_config = yaml.full_load(file)

                if  'config' in self.default_config:
                    self.default_config = self.default_config['config']

        if bag_name:
            pulumi.log.debug(f'pulumi config loaded for bag {bag_name}')
            self.pulumi_config = pulumi.Config(bag_name)
        else:
            pulumi.log.debug('pulumi config loaded with no bag name')
            self.pulumi_config = pulumi.Config()

    def _get_full_key(self, key) -> str:
        return f'{self.bag_name}:{key}'

    def get_boolean(self, key) -> Optional[bool]:
        """
        returns an option boolean value from configuration
        """

        value = self._get_value(key)
        if value is None:
            return None
        if value in ['True', 'true']:
            return True
        if value in ['False', 'false']:
            return False

        raise Exception(f'Configuration {key} value {value} is not a valid boolean')

    def get_string(self, key) -> Optional[str]: 
        """
        returns an optional string value from configuration
        """
        return self._get_value(key )

    def require_string(self, key) -> str:
        """
        returns a string value if configuration item is found by key or exception if not
        """
        value = self.get_string(key)
        if value is None:
            raise self._missing_value(key)
        
        return value

    def get_float(self, key) -> Optional[float]:
        """
        returns an optional float value from configuration
        """
        value = self._get_value(key)
        if value is None:
            return None
        
        try:
            return float(value)
        except Exception as e:
            raise self._config_type_error(key, value, type(float)) from e

    def require_float(self, key) -> float:
        """
        returns a float value if configuration item is found by key or exception if not
        """
        value = self.get_float(key)
        if value is None:
            raise self._missing_value(key)

    def get_int(self, key) -> Optional[int]:
        value = self._get_value(key)
        if value is None:
            return None
    
        try:
            return int(value)
        except Exception as e:
            raise self._config_type_error(key, value, type(int)) from e


    def _get_value(self, key) -> Optional[str]:
        """
        Hierarchy goes as follows: 
            1. check stack specific config
            2. check stack specific config using "config" dictionary item
            3. check config used by pulumi CLI
        """

        """look for our key in the stack specific config defined for our customer"""
        full_key = self._get_full_key(key)
        if full_key in self.config:
            pulumi.log.debug(f'Retrieving key {full_key} from stack config for specific customer')

            return self.config[full_key]

        """next look to our 'default' config defined in our customer directory"""
        if full_key in self.default_config:
            pulumi.log.debug(f'Retrieving key {full_key} from defaul.yaml config')

            return self.default_config[full_key]

        """finally, look to the pulumi-stack specific config for the key. This is our last hope"""
        pulumi.log.debug(f'Retrieving key {full_key} from pulumi config')
        
        return self.pulumi_config.get(key)       

    def _missing_value_error(key) -> Exception:
        return Exception(f'Key {key} is missing from configuration file')

    def _config_type_error(key, value, type) -> Exception:
        return Exception(f'Configuration {key} value {value} is not a valid {type}')