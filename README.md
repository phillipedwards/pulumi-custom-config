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

![image](https://user-images.githubusercontent.com/25461821/128745949-62c144bb-4548-49d0-8d16-eab440f2be8b.png)

The next step is we need to make a couple of changes to our project structure. Our current project structure should look like this:

![image](https://user-images.githubusercontent.com/25461821/128745809-9435fabb-bf4d-41b8-b84c-853c28ab38af.png)

Notice the `environments` directory. This directory should have a sub-directory for each `environment` you wish to support per stack. Eg- prod and sdlc. Expanded view should look like:

![image](https://user-images.githubusercontent.com/25461821/128746148-7c2ef4dd-325d-41d7-9567-6dc04e1961ee.png)

The last configuration step in this process is optional. In each `environment` directory located in `environments`, you can create a defaults.yaml configuration file which can be used to store common configuration items, for a specific environment. These would be common reusable values all stacks in an environment share.

Our project setup is now complete. Before we execute a `pulumi up` or `pulumi preview`, we need to account for one details. The Pulumi CLI, be default, looks in the root directory of the Pulumi project for a stack configuration file. For example, if the stack is named `sdlc-ks123` the Pulumi CLI will look for a yaml file named `Pulumi.sdlc-ks123.yaml` located in the root directory of the project. If this file is not found, an error will be experienced.

To accomodate for our custom configuration directories, we will take advantage of an optional flag/parameter Pulumi allows when using `preview` or `up`, the `--config-file` flag. According to [pulumi docs](https://www.pulumi.com/docs/reference/cli/pulumi_preview/) the flag allows _"Use the configuration values in the specified file rather than detecting the file name"_

Wrapping up, we now must specify what config we want Pulumi to utilize when executing an `up` or `preview`. For example, using the `sdlc-ks123` stack, we would exeucte a `preview` with `pulumi preview --config-file ./environments/sdlc/Pulumi.sdlc-123.yaml`.

Populate the necessary pulumi configuration files, execute ```pulumi up```, and see the different values retrieved! Using the output of our main.py file in this repo, the output looks as follows:

![image](https://user-images.githubusercontent.com/25461821/128747536-89f5ac73-f02d-4ff6-9958-0e884a056361.png)
