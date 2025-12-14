import requests, json, os
from colorama import Fore, Style, init
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

prompt_style = Style.from_dict({
    "": "ansigreen",   # semua input user berwarna hijau
})

a = "sk-or-v1-7995770d42"
b = "78c5cbb2d0ab4335adf3"
c = "b69dfff451870ce8"
d = "9f73cf8b7a9544ce02"

OPENROUTER_API_KEY = a+b+c+d
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class LLM_API:
    def __init__(self):
        self.model = "x-ai/grok-4-fast"
        self.headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json"}
        self.payload = {"model": self.model, "messages": [], "stream": True}
    
    def set_system_prompt(self, system_prompt: str):
        self.payload['messages'].append({"role": "system", "content": system_prompt})
    
    def add_message(self, role: str, content: str):
        self.payload['messages'].append({"role": role, "content": content})
    
    def clear_messages(self):
        self.payload['messages'] = []
    
    def get_response(self):
        response_text = ""

        print(Fore.YELLOW + "Sedang merangkum teks...", flush=True)

        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=self.headers, json=self.payload, stream=True
        )
        response.raise_for_status()

        first_chunk = True

        for chunk in response.iter_lines():
            if chunk:
                data = chunk.decode('utf-8')
                if data.startswith("data: "):
                    data = data[6:]
                    if data.strip() != "[DONE]":
                        data = json.loads(data)
                        delta = data['choices'][0]['delta']['content']

                        if delta:
                            if first_chunk:
                                # Hapus baris "AI thinking..."
                                print("\033[F\033[K", end="")  
                                first_chunk = False

                            print(Fore.WHITE + delta, end='', flush=True)
                            response_text += delta

        return response_text

    def start_chat(self):
        while True:
            user_input = prompt(
                HTML('<ansigreen>You:</ansigreen> '),
                style=prompt_style
            )

            if user_input.lower() in ["q", "quit", "exit"]:
                break

            # --- FITUR RANGKUM FILE ---
            if user_input.startswith("ringkas "):
                filepath = user_input.replace("ringkas ", "").strip()
                filepath = filepath.strip('"').strip("'")

                ext = os.path.splitext(filepath)[1].lower()
                if ext == ".pdf":
                    text = self.read_pdf(filepath)
                else:
                    text = self.read_txt(filepath)

                ringkasan = self.summarize_text(text)
                print("\n=== Ringkasan ===\n", ringkasan)

                continue  # <<< MENCEGAH AI MEMBACA PATH FILE

            # Chat normal
            self.add_message("user", user_input)
            print("AI: ", end="", flush=True)
            self.get_response()
            print()
            self.clear_messages()

    def read_txt(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error membaca file: {str(e)}"
        
    def read_pdf(self, filepath):
        import PyPDF2
        try:
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text
        except Exception as e:
            return f"Error membaca PDF: {str(e)}"

    def summarize_text(self, text):
        self.clear_messages()
        self.add_message("user", f"Tolong ringkas teks berikut:\n\n{text}")

        print(Fore.WHITE + "Chatbot:")
        return self.get_response()

llm_api = LLM_API()
llm_api.set_system_prompt(
    "Anda adalah asisten yang sangat bagus dalam merangkum teks."
)
llm_api.start_chat()
