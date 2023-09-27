# Venus

Venus is a FastAPI microservice that manages Fern's auth (users, organizations, tokens).

## 🌿 Fern-managed API

Venus uses [Fern](https://www.buildwithfern.com/) to manage its API.

With Fern, you define your API in YAML. On the server side, Fern generates boilerplate-like Pydantic models and FastAPI-compatible abstract classes that give you compile time safety when implementing the API. Fern also generates and publishes SDKs/Client Libraries.

https://user-images.githubusercontent.com/10870189/212732794-4254030e-679d-4fb5-9be9-47afe23f9077.mp4

## Modifying the API

The API definition lives in [fern/venus-api/definition/](fern/venus-api/definition/). You can see an
example service defined in [user.yml](fern/venus-api/definition/user.yml). The [Fern
docs](https://www.buildwithfern.com/docs/definition) are helpful to learn about
the different things you can define!

## Updating generated code

After modifying the Fern Definition, you need to re-generate the server
interfaces and Pydantic models:

```bash
npm install -g fern-api # you only need to do this the first time
fern generate
```

The generated code will be placed in [src/venus/generated/server](src/venus/generated/server).

## Implementing a service

With Fern, services are implemented using abstract classes. Simply extend the
Fern-generated abstract class and mypy will guide you through implementing the
API correctly. See the [user service](src/venus/user_service.py) for
an example.

## Errors

Fern also generates exceptions for us. If your endpoint has failure modes, be
sure to list them as errors in the Fern Definition. When implementing your
endpoint, feel free to `raise` the generated exceptions. Fern will handle
serializing them into the correct JSON.
