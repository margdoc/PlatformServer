# Platform Server

## Run Server

Enter
```
uvicorn main:app
```
to run server. It will be running on localhost on port 8000. To see swagger, go to "/docs".

## Requirements

You must have python packages listed in requirements.txt and environment variables:
* SECRET_KEY   - key for generating jwt token
* DATABASE_URL - mongodb database url with username and password. This database contains all users data.
