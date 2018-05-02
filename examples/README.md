# How to run the examples

1) Open `config_template.ini` and insert your `api_id` and `api_hash`.
Pyrogram provides an explanation on how to obtain these over at the [Pyrogram Docs - API Keys](https://docs.pyrogram.ml/start/ProjectSetup#api-keys)

2) Rename the template file `config_template.ini` to just `config.ini` in order to allow 
Pyrogram to parse it automatically.

Remember that in a productive environment, you should probably use environment variables or 
another configuration source and pass them directly to the initializer of the Client. 
However, for the sakeof simplicity in these example, the .ini approach works quite well to get 
up and running quickly.
