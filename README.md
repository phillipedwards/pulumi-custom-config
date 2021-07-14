# Pulumi and Custom Configuration
The purpose of this repository is to show an example of a user-defined configuration layer which can extend pulumi's configuration capabilities, by adding user-defined organization and options.

For more information on getting started with pulumi, visit [Get Started with Pulumi](https://www.pulumi.com/docs/get-started/).

See the following links for more information about pulumi and it's out of the box configuration model.
- [Configuration Concepts](https://www.pulumi.com/docs/intro/concepts/config/)
- [Pulumi YAML Reference](https://www.pulumi.com/docs/reference/pulumi-yaml/)

**This user-defined custom config does not support pulumi secrets!!! You should continue to use pulumi's out of the box configuration that provides excellent support for secrets!
[YAY Secrets!](https://www.pulumi.com/docs/intro/concepts/secrets/)

### Why
Pulumi configuration currently supports the use of a single yaml file, in a single location (Eg- Pulumi.stack.yaml). One cannot support a hierarchical configuration or organize individual stack configurations in a directory structure, without some effort.

### What
To support hierarchical configuration or directory organization, we'd need to write some code to interact with pulumi and it's configuration system.

### How
Using an intermediary configuration layer, we will support hierarchical configuration, organization of our stack configuratiions, and multi-tenant configurations. This configuration layer will wrap the existing configuration model and automatically search for configuration keys in other stack specific files.

In this solution, there are two main top-level directories:
- pulumi_config - pulumi cli will look here for basic stack related info. All stacks should have a yaml file in this directory for pulumi's mimimum required config values
- customer_config - all other user-defined configuration files.

**Keep in mind you can define the directory structure and configuration access model as you see fit! This is but one example.**

The custom config will retrieve configuration values for keys based on the following hierarchy:
1. Configuration items located in an environment configuration. Eg- ./customer_config/prod/customer-123.yaml
2. Configuration items located in the default configuration. Eg- ./customer_config/default.yaml
3. Configuration items located in the pulumi configuration. Eg- ./pulumi_config/Pulumi.my-stack.yaml

To allow this custom configuration to retrieve all configuration values, all stacks should follow the naming scheme of: 

{environment}-{customer} where environment is 'prod' or 'stage', in this case, and customer is whatever value you'd like to use to differentiate your 'customer'.

For this example, we have defined our configuration system as follows:
pulumi_config
|
|__Pulumi.my-stack.yaml

customer_config  
|  
|__prod  
|     |  
|     |__customer-123.yaml  
|     |  
|     |__customer-abc.yaml  
|  
|__stage  
|     |  
|     |__customer-123.yaml  
|     |  
|     |__customer-abc.yaml  
|  
|__defaults.yaml  

