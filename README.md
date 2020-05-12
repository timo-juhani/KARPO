# Configure ACI with Python!

## Functionality
- Python script repository for simple Cisco ACI automation tasks.
- At this point concentrates on provisioning and "pushing" Tenants configurations.
- createOverlay.py is the main script at the moment. It creates a new overlay network and policies attached to that based on configuration database maintained in configuration.json.
- payloads folder contain the Jinja2 templates that are used to render payloads for the REST calls that are sent to APIC.
- all payloads in the folder are supported in the code and POST'ed by default.

## Example

![image](example.jpg)


## Next steps
- Add fabric access policies
- Think about using per tenant configuration files
- Create MACD plays for tenants
