# g1sh-llm

a simple shell-based interface to interact with LLMs.  
built for learning, and experimenting.

## what is this?
`g1sh-llm` is a CLI project that lets you talk to a local LLM directly from your shell.

## features (WIP)
- shell-based workflow
- lightweight & minimal
- easy to extend
- made for learning how LLM tooling works (for myself, but can be used by other people)

## requirements
- linux / macOS
- python 3.10+
- git
- ollama

## setup
clone the repo:
```bash
git clone https://github.com/6r3eN/g1sh-local.git
cd g1sh-local
````

## install ollama and start it:
```bash
ollama serve
```

## pull the model:

```bash
ollama pull llama3.2:3b
```

## usage

run the CLI with a prompt:

```bash
python cli.py "bla bla bla"
```

or just run it and chat:

```bash
python cli.py
```

## how it works

* `cli.py` handles user input
* `engine.py` sends prompts to ollama
* ollama runs the LLM locally and gives responses
* config is stored in `g1sh_config.json`

## notes

* this is a learning project
* expect bugs (even though i haven't experienced one)

```
