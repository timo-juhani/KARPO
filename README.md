# Configure ACI with Python!

## Functionality
This repository contains Python scripts that are used to automate ACI configuration tasks. The point of this work is to treat ACI implementation as an infrastructure-as-code project using minimalistic set of open source tools.

createOverlay.py pushes complete tenant configuration to APIC based on the configuration variables recorded in .json. Since the script consumes the native ACI REST API I'm maintaining the payload templates in a folder where they can be fetched and rendered using the configuration data. I'm currently developing this repo quite actively which means improvements, but also changing approaches as I learn more about what works and what doesn't. 

## Example

![image](example.jpg)


## Roadmap features
- Add fabric access policies
- Think about using per tenant configuration files
- Create MACD plays for tenants
