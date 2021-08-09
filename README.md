# Pulumi and Custom Configuration
The purpose of this repository is to show an example of a user-defined configuration layer which can extend pulumi's configuration capabilities, by adding user-defined organization and options.

For more information on getting started with pulumi, visit [Get Started with Pulumi](https://www.pulumi.com/docs/get-started/).

See the following links for more information about pulumi and it's out of the box configuration model.
- [Configuration Concepts](https://www.pulumi.com/docs/intro/concepts/config/)
- [Pulumi YAML Reference](https://www.pulumi.com/docs/reference/pulumi-yaml/)

**This user-defined custom config does not support pulumi secrets!!! You should continue to use pulumi's out of the box configuration that provides excellent support for secrets!**
[YAY Secrets!](https://www.pulumi.com/docs/intro/concepts/secrets/)

### Why
Pulumi configuration currently supports the use of a single yaml file, in a single location (Eg- Pulumi.stack.yaml). One cannot support a hierarchical configuration or organize individual stack configurations in a directory structure, without some effort.

### What
To support hierarchical configuration or directory organization, we'd need to write some code to interact with pulumi and it's configuration system.

### How
Using an intermediary configuration layer, we will support hierarchical configuration, organization of our stack configuratiions, and multi-tenant configurations. This configuration layer will wrap the existing configuration model and automatically search for configuration keys in other stack specific files.

The custom_config will resolve configuration items through the following order:
1. Look in the stack configuration in the environments/{env}/ directory.
2. Look in the defaults.yaml file in the environments/{env}/ directory.

## Getting Started
We'll use a new pulumi python app to demonstrate how to use the custom_config. AWS will be the cloud provider used, however, this solution is not cloud provider specific.

```mkdir pulumi_custom_config && cd pulumi_custom_config```  
```pulumi new aws-python```  

Walk through the interactive CLI prompt and fill out, as you need. Most importantly to the custom_config, your stack must be named following a specific scheme and your stack configuration file must be located in a unique directory. 
- Stack name must be in the following scheme: {environment}-{customer-id} where environment is either 'prod' or 'sdlc' and customer-id is a user chosen value. Eg- 'sdlc-ks123'.
- Stack configuration file must be located in a directory that corresponds to the environment portion, in the stack name. Eg- if the stack name is sdlc-ks123, the `Pulumi.sdlc-ks123.yaml` file must be located at: `./environments/sdlc/Pulumi.sdlc-ks123.yaml`.

Assuming we added two stacks, prod-customer123 and sdlc-customer123 your dashboard on app.pulumi.com should look like:

![Screen Shot 2021-07-19 at 9 59 53 AM](https://user-images.githubusercontent.com/25461821/126201592-8c058ecb-706a-4d5b-bffd-4b5c1efb4fca.png)

The next step is we need to make a couple of changes to our project structure. Our current project structure should look like this:

![Screen Shot 2021-07-19 at 10 58 02 AM](https://user-images.githubusercontent.com/25461821/126221918-32d5b02f-65f1-45a5-9f3f-b7776dcbe100.png)

We need to alter our project directory, by creating 2 new folders at the root of our pulumi project. Create 'pulumi_config' and 'customer_config'. After the directory should look like this:

![image](https://user-images.githubusercontent.com/25461821/126225592-339bc450-296b-46b6-9800-6beea52c2a65.png)

As the number of stacks in a pulumi project grows, it can be helpful to locate all stack configs in a directory of its own. Next, go ahead and move both stacks yaml files into the pulumi_config directory. Our directory should now look like:

![image](https://user-images.githubusercontent.com/25461821/126223060-baf9bb8f-421a-401c-84f6-d3ac2f5ea8db.png)

We have two more steps to make this solution complete. First we will tell the pulumi program to look for a stacks yaml config file in the pulumi_config directory and second we will create our user-defined, custom yaml config files.

**NOTE**: each new stack you create should have a pulumi configuration file located in the pulumi_config directory. These config files should contain a minimum amount of information in order for pulumi to successfully run. For example, config items like aws:region should be located here.

In the root of the pulumi project, open the Pulumi.yaml file. You can read more about the 'config' option in [pulumi configuration](https://www.pulumi.com/docs/reference/pulumi-yaml/), but we need to insert the following: ```config: ./pulumi_config```. This will tell the pulumi CLI to look in the pulumi_config directory for a stack's configuration.

Your Pulumi.yaml file should now look like:

![image](https://user-images.githubusercontent.com/25461821/126223596-e44a6419-c367-48ad-94fc-7a6ba1fdbd59.png)

The last item of this solution is creating user-defined configurations for each of our stacks. These stack configurations are organized in an environment specific fashion, which helps minimize the possibility of human error while maximizing ease of use. We will create two files, with the same name, and place one in a prod directory and one in a stage directory. You're project should now look like:

![image](https://user-images.githubusercontent.com/25461821/126223978-9024cb0e-3dc4-4e86-949f-964913bd1481.png)

The last configuration step in this process is optional. In the customer_config directory, you can create a defaults.yaml configuration file which can be used to store common configuration items, between stacks.

After adding the custom_config.py file to your solution, your directory should now be complete and look like:

![image](https://user-images.githubusercontent.com/25461821/126224483-cbe28591-0e22-4ed1-b401-9989db5b9ed7.png)

Our project setup is now complete. Populate the necessary pulumi configuration files, execute ```pulumi up```, and see the different values retrieved! Using the output of our main.py file in this repo, the output looks as follows:

![image](https://user-images.githubusercontent.com/25461821/126227537-5243641b-f1e5-4d06-8969-8960c872f365.png)
