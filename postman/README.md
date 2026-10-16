# Postman Assets

Import both files:

1. `Sentinel_UAS_Assurance.postman_collection.json`
2. `Sentinel_UAS_Local.postman_environment.json`

Start the API on `http://127.0.0.1:8080`, select the local environment, and run the collection. Dynamic pre-request scripts generate current timestamps and unique identifiers where freshness or replay controls require them.

The environment contains obvious local-lab tokens only. Do not replace them with real credentials in a file that will be committed.
