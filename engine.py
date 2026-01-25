import json
import os
import logging
import subprocess
from datetime import datetime
from ollama import chat

logging.basicConfig(
    filename='g1sh.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

DEFAULT_CONFIG = {
    "model": "llama3.2:3b",
    "streaming": True,
    "max_messages": 20,
    "temperature": 0.7,
    "top_p": 0.9,
    "num_ctx": 4096,
    "num_predict": 120
}

class G1shEngine:
    def __init__(self, memory_file="g1sh_memory.json", config_file="g1sh_config.json"):
        self.memory_file = memory_file
        self.config_file = config_file
        self.config = self.load_config()
        self.messages = self.load_memory()
        
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return {**DEFAULT_CONFIG, **json.load(f)}
            except Exception as e:
                logging.error(f"Error loading config: {e}")
        return DEFAULT_CONFIG
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def get_system_prompt(self, message_count):
        return (
            "you are g1sh. respond in lowercase only (except code/acronyms). "
            "be concise - max 2-3 sentences unless user asks for detail. "
            "casual tone, no formalities, no 'happy to help' bullshit. "
            "just answer the question directly. "
            "if you don't know, say so. "
            f"conversation has {message_count} messages."
        )
    
    def refresh_system_prompt(self):
        """Update system prompt with current message count"""
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = self.get_system_prompt(len(self.messages))
    
    def load_memory(self):
        """Load conversation history from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    data = json.load(f)
                    if data and isinstance(data, list):
                        return data
            except Exception as e:
                logging.error(f"Error loading memory: {e}")
        return [{"role": "system", "content": self.get_system_prompt(0)}]
    
    def save_memory(self):
        """Save conversation history to file"""
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.messages, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving memory: {e}")
    
    def trim_memory(self, max_messages=None):
        """Keep system prompt + last N exchanges to prevent context overflow"""
        if max_messages is None:
            max_messages = self.config["max_messages"]
        
        if len(self.messages) > max_messages:
            self.messages = [self.messages[0]] + self.messages[-(max_messages-1):]
            self.save_memory()
            return True
        return False
    
    def estimate_tokens(self, text):
        """Better token estimate for llama models (~1.3 tokens per word)"""
        return int(len(text.split()) * 1.3)
    
    def get_total_tokens(self):
        """Get total token count of conversation"""
        return sum(self.estimate_tokens(m["content"]) for m in self.messages)
    
    def check_context_overflow(self):
        """Check if context is approaching limit"""
        total = self.get_total_tokens()
        max_tokens = self.config["num_ctx"]
        if total > max_tokens * 0.8:
            return True, total, max_tokens
        return False, total, max_tokens
    
    def get_stats(self):
        """Get conversation statistics"""
        total_tokens = self.get_total_tokens()
        user_msgs = sum(1 for m in self.messages if m["role"] == "user")
        assistant_msgs = sum(1 for m in self.messages if m["role"] == "assistant")
        return {
            "total_messages": len(self.messages),
            "user_messages": user_msgs,
            "assistant_messages": assistant_msgs,
            "total_tokens": total_tokens,
            "model": self.config["model"]
        }
    
    def export_conversation(self, filename=None):
        """Export conversation to text file"""
        if filename is None:
            filename = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, "w") as f:
                f.write(f"G1SH Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                for msg in self.messages[1:]:
                    role = msg["role"].upper()
                    f.write(f"{role}: {msg['content']}\n\n")
            logging.info(f"Conversation exported to {filename}")
            return True, filename
        except Exception as e:
            logging.error(f"Export error: {e}")
            return False, str(e)
    
    def search_conversation(self, query):
        """Search through conversation history"""
        results = []
        for i, msg in enumerate(self.messages[1:], 1):
            if query.lower() in msg["content"].lower():
                preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                results.append((i, msg["role"], preview))
        return results
    
    def undo_last_exchange(self):
        """Remove last user-assistant exchange"""
        if len(self.messages) > 1:
            if self.messages[-1]["role"] == "assistant":
                self.messages.pop()
            if self.messages and self.messages[-1]["role"] == "user":
                self.messages.pop()
            self.save_memory()
            return True
        return False
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.messages.clear()
        self.messages.append({"role": "system", "content": self.get_system_prompt(0)})
        self.save_memory()
        logging.info("Memory reset")
    
    def get_available_models(self):
        """Fetch actual installed models from Ollama"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                models = []
                for line in result.stdout.split('\n')[1:]:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models if models else ["llama3.2:3b"]
            return ["llama3.2:3b"]
        except Exception as e:
            logging.error(f"Error fetching models: {e}")
            return ["llama3.2:3b"]
    
    def check_ollama_running(self):
        """Verify Ollama is running"""
        try:
            available = self.get_available_models()
            test_model = available[0] if available else "llama3.2:3b"
            chat(model=test_model, messages=[{"role": "user", "content": "test"}], options={"num_predict": 1})
            return True, None
        except Exception as e:
            return False, str(e)
    
    def switch_model(self, model_name):
        """Switch to a different model"""
        available = self.get_available_models()
        if model_name in available:
            self.config["model"] = model_name
            self.save_config()
            logging.info(f"Model switched to {model_name}")
            return True
        return False
    
    def set_temperature(self, temp):
        """Set temperature value"""
        if 0 <= temp <= 2:
            self.config["temperature"] = temp
            self.save_config()
            return True
        return False
    
    def toggle_streaming(self, enabled):
        """Toggle streaming mode"""
        self.config["streaming"] = enabled
        self.save_config()
    
    def chat(self, user_message, callback=None):
        """
        Send a message and get response
        callback: function(chunk) called for each streaming chunk
        """
        self.messages.append({"role": "user", "content": user_message})
        logging.info(f"USER: {user_message}")
        
        self.refresh_system_prompt()
        
        try:
            use_streaming = self.config["streaming"]
            model = self.config["model"]
            
            if use_streaming and callback:
                full_response = ""
                
                for chunk in chat(
                    model=model,
                    messages=self.messages,
                    stream=True,
                    options={
                        "temperature": self.config["temperature"],
                        "top_p": self.config["top_p"],
                        "num_ctx": self.config["num_ctx"],
                        "num_predict": self.config["num_predict"],
                    }
                ):
                    content = chunk["message"]["content"]
                    callback(content)
                    full_response += content
                
                assistant_message = full_response
            else:
                response = chat(
                    model=model,
                    messages=self.messages,
                    options={
                        "temperature": self.config["temperature"],
                        "top_p": self.config["top_p"],
                        "num_ctx": self.config["num_ctx"],
                    }
                )
                assistant_message = response["message"]["content"]
            
            self.messages.append({"role": "assistant", "content": assistant_message})
            logging.info(f"ASSISTANT: {assistant_message}")
            
            self.trim_memory()
            self.save_memory()
            
            return True, assistant_message
        
        except Exception as e:
            self.messages.pop()
            error_msg = f"oof, something broke: {str(e)}"
            logging.error(f"Chat error: {e}")
            return False, error_msg
    
    def get_last_assistant_message(self):
        """Get the last assistant message"""
        for msg in reversed(self.messages):
            if msg["role"] == "assistant":
                return msg["content"]
        return None
    
    def retry_last_message(self, callback=None):
        """Regenerate the last response"""
        if len(self.messages) > 1 and self.messages[-1]["role"] == "assistant":
            self.messages.pop()
            if self.messages[-1]["role"] == "user":
                last_user_msg = self.messages[-1]["content"]
                self.messages.pop()
                return self.chat(last_user_msg, callback)
        return False, "nothing to retry"