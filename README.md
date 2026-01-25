# g1sh

**a lightweight CLI for chatting with local LLMs**

simple, fast, and easy to customize. built for learning and experimenting with AI stuff

---

## what is this?

g1sh is a terminal-based chat interface for local language models. it uses [ollama](https://ollama.com) to run models on your machine. no API keys, no cloud costs.

perfect for:
- learning how LLM interfaces work
- building AI tools locally
- experimenting without rate limits
- running on low-end hardware

---

## features

- **local-first**: everything runs on your machine
- **persistent memory**: conversations saved between sessions
- **streaming responses**: see the AI think in real-time
- **model switching**: easily swap between different models
- **config management**: persistent settings via JSON
- **search history**: find past conversations
- **export chats**: save conversations to text files
- **undo/retry**: fix mistakes or regenerate responses
- **clean architecture**: separated CLI and engine logic

---

## quick start

### requirements

- python 3.10+
- ollama ([install guide](https://ollama.com))
- 8GB+ RAM recommended
- linux / macOS / WSL2

### installation

```bash
# clone the repo
git clone https://github.com/6r3eN/g1sh-llm.git
cd g1sh-llm

# install ollama (if not already)
# visit https://ollama.com

# pull a model (recommended for most hardware)
ollama pull llama3.2:3b

# run g1sh
python3 cli.py
```

that's it. start chatting.

---

## usage

### basic chat

```bash
python3 cli.py
```

### available commands

```
/help          - show all commands
/reset         - clear conversation history
/stats         - show token usage and message count
/model <name>  - switch to a different model
/models        - list available models
/search <text> - search conversation history
/export        - save conversation to file
/undo          - remove last exchange
/retry         - regenerate last response
/temp <0-2>    - adjust response creativity
/clear         - clear screen (keep history)
exit/quit      - close g1sh
```

### example session

```
You: explain quantum computing in simple terms
g1sh: quantum computers use qubits instead of bits. unlike normal bits (0 or 1), qubits can be both at once until measured. this lets them solve certain problems way faster than regular computers.

You: /stats

Stats:
  Messages: 3 (user: 1, assistant: 1)
  Estimated tokens: ~65
  Model: llama3.2:3b

You: /export myconvo.txt
exported to myconvo.txt
```

---

## configuration

g1sh uses `g1sh_config.json` for settings:

```json
{
  "model": "llama3.2:3b",
  "streaming": true,
  "temperature": 0.7,
  "num_ctx": 4096,
  "num_predict": 512
}
```

**key settings:**
- `model`: which ollama model to use
- `temperature`: randomness (0 = focused, 2 = creative)
- `num_ctx`: conversation memory window (in tokens)
- `num_predict`: max response length

edit this file directly or use `/temp` and `/model` commands that is provided in `/help`

---

## recommended models

for different hardware:

**low-end (8-16GB RAM, iGPU):**
```bash
ollama pull llama3.2:1b    # blazing fast
ollama pull llama3.2:3b    # balanced (recommended)
ollama pull phi3:3.8b      # good for code
```

**mid-range (16-32GB RAM, decent GPU):**
```bash
ollama pull llama3.2:7b    # high quality
ollama pull mistral:7b     # fast and smart
ollama pull codellama:7b   # best for coding
```

**high-end (32GB+ RAM, strong GPU):**
```bash
ollama pull llama3:70b     # top quality
ollama pull mixtral:8x7b   # very capable
```

switch models anytime with `/model <name>`

---

## architecture

```
cli.py          # user interface, commands, display
engine.py       # AI logic, memory, config management
g1sh_config.json # persistent settings
g1sh_memory.json # conversation history
g1sh.log        # debug logs
```

clean separation means you can:
- build a GUI on top of `engine.py`
- integrate g1sh into other projects
- swap out the CLI for discord/telegram/etc

---

## hardware tips

**running on integrated graphics?**
- use smaller models (`llama3.2:1b` or `3b`)
- reduce `num_ctx` to 1024-2048
- expect 5-15 second response times

**have a dedicated GPU?**
- try larger models (`7b` or `13b`)
- increase `num_ctx` to 8192+
- sub-second responses possible

**low on disk space?**
- each model is like 1-5GB
- just remove unused models: `ollama rm <model>`

---

## troubleshooting

**"can't connect to ollama"**
```bash
# start ollama server
ollama serve
```

**"model not found"**
```bash
# list available models
ollama list

# pull the model
ollama pull llama3.2:3b
```

**responses cutting off**
- increase `num_predict` in config to 512-1024

**responses too slow**
- try a smaller model
- reduce `num_ctx` to 1024

---

## why "g1sh"?

it's pronounced like "gish" (soft g). name comes from my nickname (green or greenish) which is shortened into gish/g1sh

**tested on:** ryzen 5 5600gt (igpu), 32gb ram, debian 13 - works great with llama3.2:3b

---
