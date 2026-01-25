#!/usr/bin/env python3
import os
import sys
from engine import G1shEngine

class G1shCLI:
    def __init__(self):
        self.engine = G1shEngine()
        self.last_response = None
        
    def print_help(self):
        """Print available commands"""
        print("\nAvailable Commands:")
        print("  /help          - show this help message")
        print("  /reset         - wipe conversation memory")
        print("  /multi         - enter multiline mode")
        print("  /export [file] - export conversation to file")
        print("  /stats         - show conversation statistics")
        print("  /model <name>  - switch model")
        print("  /models        - list available models")
        print("  /stream on/off - toggle streaming mode")
        print("  /temp <0-2>    - set temperature (default: 0.7)")
        print("  /search <text> - search conversation history")
        print("  /undo          - remove last exchange")
        print("  /last          - repeat last assistant response")
        print("  /retry         - regenerate last response")
        print("  /clear         - clear screen (keep history)")
        print("  /trim          - trim old messages manually")
        print("  exit/quit      - quit the program")
        print()
    
    def get_multiline_input(self):
        """Get multiline input from user"""
        print("You (end with empty line or type 'send'):")
        lines = []
        while True:
            try:
                line = input()
                if not line or line.lower() == "send":
                    break
                lines.append(line)
            except (KeyboardInterrupt, EOFError):
                return None
        if not lines:
            print("g1sh: cancelled multiline input\n")
            return None
        return "\n".join(lines)
    
    def handle_command(self, user_input):
        """Handle slash commands, return True if command was handled"""
        
        if user_input.lower() in {"/help", "help", "?"}:
            self.print_help()
            return True
        
        if user_input.lower() == "/reset":
            self.engine.reset_conversation()
            print("g1sh: memory wiped. fresh start\n")
            return True
        
        if user_input.lower() == "/multi":
            multi_input = self.get_multiline_input()
            if multi_input:
                return self.send_message(multi_input)
            return True
        
        if user_input.lower().startswith("/export"):
            parts = user_input.split(maxsplit=1)
            filename = parts[1] if len(parts) > 1 else None
            success, result = self.engine.export_conversation(filename)
            if success:
                print(f"exported to {result}\n")
            else:
                print(f"export failed: {result}\n")
            return True
        
        if user_input.lower() == "/stats":
            stats = self.engine.get_stats()
            print(f"\nStats:")
            print(f"  Messages: {stats['total_messages']} (user: {stats['user_messages']}, assistant: {stats['assistant_messages']})")
            print(f"  Estimated tokens: ~{stats['total_tokens']}")
            print(f"  Model: {stats['model']}")
            print()
            return True
        
        if user_input.lower() == "/models":
            available = self.engine.get_available_models()
            print(f"\nAvailable models: {', '.join(available)}")
            print(f"   Current model: {self.engine.config['model']}\n")
            return True
        
        if user_input.lower().startswith("/model "):
            new_model = user_input.split(" ", 1)[1].strip()
            if self.engine.switch_model(new_model):
                print(f"g1sh: switched to {new_model}\n")
            else:
                available = self.engine.get_available_models()
                print(f"g1sh: unknown model. available: {', '.join(available)}\n")
            return True
        
        if user_input.lower().startswith("/stream "):
            mode = user_input.split(" ", 1)[1].strip().lower()
            if mode == "on":
                self.engine.toggle_streaming(True)
                print("g1sh: streaming enabled\n")
            elif mode == "off":
                self.engine.toggle_streaming(False)
                print("g1sh: streaming disabled\n")
            else:
                print("g1sh: use '/stream on' or '/stream off'\n")
            return True
        
        if user_input.lower().startswith("/temp "):
            try:
                temp = float(user_input.split(" ", 1)[1].strip())
                if self.engine.set_temperature(temp):
                    print(f"g1sh: temperature set to {temp}\n")
                else:
                    print("g1sh: temperature must be between 0 and 2\n")
            except ValueError:
                print("g1sh: invalid temperature value\n")
            return True
        
        if user_input.lower().startswith("/search "):
            query = user_input.split(" ", 1)[1].strip()
            results = self.engine.search_conversation(query)
            if results:
                print(f"\nFound {len(results)} result(s):\n")
                for idx, role, preview in results:
                    print(f"  [{idx}] {role.upper()}: {preview}")
                print()
            else:
                print("g1sh: no results found\n")
            return True
        
        if user_input.lower() == "/undo":
            if self.engine.undo_last_exchange():
                print("g1sh: last exchange removed\n")
            else:
                print("g1sh: nothing to undo\n")
            return True
        
        if user_input.lower() == "/last":
            last_msg = self.last_response or self.engine.get_last_assistant_message()
            if last_msg:
                print(f"g1sh: {last_msg}\n")
            else:
                print("g1sh: no previous response\n")
            return True
        
        if user_input.lower() == "/retry":
            print("g1sh: regenerating response...\n")
            return self.retry_message()
        
        if user_input.lower() == "/clear":
            os.system('clear' if os.name != 'nt' else 'cls')
            print("g1sh online. type '/help' for commands.\n")
            return True
        
        if user_input.lower() == "/trim":
            original_len = len(self.engine.messages)
            self.engine.trim_memory()
            removed = original_len - len(self.engine.messages)
            print(f"g1sh: trimmed {removed} old messages\n")
            return True
        
        return False
    
    def send_message(self, message):
        """Send a message to the AI"""
        def stream_callback(chunk):
            print(chunk, end="", flush=True)
        
        if self.engine.config["streaming"]:
            print("g1sh: ", end="", flush=True)
            success, response = self.engine.chat(message, callback=stream_callback)
            print()
        else:
            success, response = self.engine.chat(message)
            print(f"g1sh: {response}\n")
        
        if success:
            self.last_response = response
            
            # Check for context overflow
            overflow, total, max_tokens = self.engine.check_context_overflow()
            if overflow:
                print(f" Context usage: {total}/{max_tokens} tokens (consider using /trim or /reset)")
        else:
            print(f"g1sh: {response}\n")
        
        return True
    
    def retry_message(self):
        """Retry the last message"""
        def stream_callback(chunk):
            print(chunk, end="", flush=True)
        
        if self.engine.config["streaming"]:
            print("g1sh: ", end="", flush=True)
            success, response = self.engine.retry_last_message(callback=stream_callback)
            print()
        else:
            success, response = self.engine.retry_last_message()
            print(f"g1sh: {response}\n")  # always print even on error
        
        if success:
            self.last_response = response
        
        return True
    
    def run(self):
        """Main CLI loop"""
        running, error = self.engine.check_ollama_running()
        if not running:
            print(f"   Can't connect to Ollama. Is it running?")
            print(f"   Start it with: ollama serve")
            print(f"   Error: {error}\n")
            return
        
        print("g1sh online. type '/help' for commands.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\ng1sh: aight, later")
                break
            
            if not user_input:
                continue
            
            if user_input.lower() in {"exit", "quit"}:
                print("g1sh: aight, later")
                break

            if not self.handle_command(user_input):
                self.send_message(user_input)

def main():
    cli = G1shCLI()
    cli.run()

if __name__ == "__main__":
    main()