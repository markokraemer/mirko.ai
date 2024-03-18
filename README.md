# Mirko.ai – the AI Software Engineer!

## Current: 4 Week Sprint 17th March – 17th April 

*GOAL*: Working, reliable-demo-ready Mirko.ai within this 4 WEEK SPRINT on the level as Devin --> meaning we have an fully implemented AI Agent Service + Frontend that you can self-host.

*Move fast, build, ship & break things!!!*

### Roadmap / Next Steps

1. Get the Docker Env Setup (Workspace for the Agent) https://github.com/markokraemer/mirko.ai/issues/1
-> Get the World/Env Setup, so we eliminate the dependancy and can build abilities on top that interact with this world env, so we can then work on the actual processing layers/agents

2. Create v1 Abilities:
https://github.com/markokraemer/mirko.ai/issues/2
https://github.com/markokraemer/mirko.ai/issues/3
-> Get a couple of useful MVP abilities working, so we eliminate the dependancy & can work on the Layers which use the abilities to interact with the Workspace.

3. Setup v1 Layers to work --> create base layers with some simple prompts connecting them to the v1 abilities – get the complete Mirko working:
https://github.com/markokraemer/mirko.ai/issues/4
https://github.com/markokraemer/mirko.ai/issues/5
https://github.com/markokraemer/mirko.ai/issues/6

4. Start working on the visual Frontend parallely to all of this + create v1 API for the intermediate-working version + connect it up to the frontend
https://github.com/markokraemer/mirko.ai/issues/17
https://github.com/markokraemer/mirko.ai/issues/19

––– These topics will give us an fully intermediate-working version. Then we have all the subsequent issues to get it to Devin-level https://snipboard.io/CSVgv7.jpg.

https://github.com/markokraemer/mirko.ai/issues All the High Priority issues are ready to be worked on. WIP meaning its still missing some information from my end.

## Setup

```
*** Requires Poetry for dependency management (https://python-poetry.org/) ***

poetry install

```

Run tests
```
python -m pytest
```

Include tests that require docker workspace running. Can use `-s` to show output.
```
INTEGRATION=1 python -m pytest
```

See `workspace` dir for docker setup.
