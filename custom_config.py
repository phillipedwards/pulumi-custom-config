
import os
import json
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
        stack_pieces = stack.split("-")
        if len(stack_pieces) != 2:
            raise Exception("Stack name must the format {stage}-{customer}")

        # should be "production" or "sdlc"
        env = stack_pieces[0]

        # should be "ks123" or some customer id
        customer = stack_pieces[1]

        pulumi.log.debug(f"Calculated environment: {env}")
        pulumi.log.debug(f"Calculated customer: {customer}")

        # path should endup being ~/environments/production or ~/environments/sdlc
        env_path = os.path.join(os.getcwd(), "environments", env)
        pulumi.log.debug(f"Calculated full environment path: {env_path}")

        if not os.path.exists(env_path):
            raise Exception(f"Environments config path at {env_path} does not exist")

        default_config_file = os.path.join(env_path, "defaults.yaml")

        if os.path.exists(default_config_file):
            pulumi.log.debug(f"Loading defaults configuration file from {default_config_file}")
            with open(default_config_file) as file:
                self.default_config = yaml.full_load(file)

                if "config" in self.default_config:
                    self.default_config = self.default_config["config"]

        """load an instance of the Pulumi standard config"""
        if bag_name:
            pulumi.log.debug(f"pulumi config loaded for bag {bag_name}")
            self.pulumi_config = pulumi.Config(bag_name)
        else:
            pulumi.log.debug("pulumi config loaded with no bag name")
            self.pulumi_config = pulumi.Config()

    def _get_full_key(self, key) -> str:
        return f'{self.bag_name}:{key}'

    def get_bool(self, key) -> Optional[bool]:
        """
        returns an option boolean value from configuration
        """
        value = self._get_value(key)
        if value is None:
            return None
        if str(value) in ['True', 'true']:
            return True
        if str(value) in ['False', 'false']:
            return False

        raise self._config_type_error(key, value, bool)

    def require_bool(self, key) -> bool:
        """
        returns a boolean value if key is found or exception if not
        """
        value = self.get_bool(key)
        if value is None:
            raise self._missing_value_error(key)

        return value

    def get(self, key) -> Optional[str]:
        """
        returns an optional string value from configuration
        """
        return self._get_value(key)

    def require(self, key) -> str:
        """
        returns a string value if key is found by key or exception if not
        """
        value = self.get(key)
        if value is None:
            raise self._missing_value_error(key)

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
            raise self._config_type_error(key, value, float) from e

    def require_float(self, key) -> float:
        """
        returns a float value if key is found by key or exception if not
        """
        value = self.get_float(key)
        if value is None:
            raise self._missing_value_error(key)

        return value

    def get_int(self, key) -> Optional[int]:
        """
        returns an optional integer value from configuration
        """
        value = self._get_value(key)
        if value is None:
            return None

        try:
            return int(value)
        except Exception as e:
            raise self._config_type_error(key, value, int) from e

    def require_int(self, key) -> int:
        """
        returns an integer value if key is found or exception if not
        """

        value = self.get_int(key)
        if value is None:
            raise self._missing_value_error(key)

        return value

    def get_object(self, key):
        """
        returns an optional object value from configuration
        """

        value = self._get_value(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except Exception as e:
            raise self._config_type_error(key, value, object) from e
        

    def require_object(self, key):
        """
        returns an integer value if key is found or exception if not
        """

        value = self.get_object(key)
        if value is None:
            raise self._missing_value_error(key)
        
        return value

    def _get_value(self, key) -> Optional[str]:
        """
        Hierarchy goes as follows: 
            1. check stack specific config per environment. eg- /environments/prod/Pulumi.prod-ks123.yaml, which should be config used by CLI
            2. check defaults config per environment. eg- /environments/prod/defaults.yaml
        """

        """look for our key in the stack specific config defined for our customer"""
        full_key = self._get_full_key(key)

        """look in the stack specific config for our key"""
        value = self.pulumi_config.get(key)
        if value:
            pulumi.log.debug(f"Retrieving key {full_key} from Pulumi configuration file")

            return value

        """next look to our 'default' config defined in our customer directory"""
        if full_key in self.default_config:
            pulumi.log.debug(f"Retrieving key {full_key} from defaul.yaml config")

            return self.default_config[full_key]

        """finally, we did not find a key in either our Pulumi.{customer}.yaml file or our defaults.yaml file, so return None"""
        pulumi.log.debug(f"Value for configuration key {full_key} not found!")

        return None

    def _missing_value_error(self, key) -> Exception:
        return Exception(f"Key {key} is missing from configuration file")

    def _config_type_error(self, key, value, type) -> Exception:
        return Exception(f"Configuration key {key} value '{value}' is not a valid {type}")
