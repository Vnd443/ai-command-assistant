import os
import platform, subprocess
import re
from openai import OpenAI
from dotenv import load_dotenv
from colorama import Fore, Style, init

# ── Init Colorama ────────────────────────────────────
init(autoreset=True)

# ── Load env ─────────────────────────────────────────
load_dotenv(".env")

api_key   = os.getenv('api_key')
base_url  = os.getenv('base_url')
model_id  = os.getenv('model_id')

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# ── Tool: Run Command ────────────────────────────────
def run_command(cmd: str):
    try:
        system = platform.system()
        print(Fore.GREEN + f"[INFO] Running on {system}")

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        output = result.stdout.strip() if result.stdout else result.stderr.strip()
        return output if output else "[No Output]"

    except Exception as e:
        return f"[ERROR]: {str(e)}"

# ── Safety Filter ────────────────────────────────────
BLOCKED_COMMANDS = [
    "format", "del /f", "rd /s", "shutdown",
    "diskpart", "mkfs", "rm -rf /", "reboot"
]

def is_safe_command(cmd: str):
    return not any(bad in cmd.lower() for bad in BLOCKED_COMMANDS)

# ── System Prompt ────────────────────────────────────
SYSTEM_PROMPT = f"""
You are an expert AI Command-Line Agent.

OS Detected: {platform.system()}

Follow strictly:

🔥 START
Understand the user request.

🧠 PLAN
Break into steps and decide best command based on OS.

🛠️ OUTPUT
- Provide explanation
- If command needed, MUST include:

CMD: <command>

Rules:
- Use OS-specific commands:
  - Windows → dir, ipconfig, tasklist
  - Linux → ls, ifconfig/ip, ps
- Only ONE command at a time
- Keep commands safe
- No JSON output
"""

# ── Safety Filter ────────────────────────────────────
BLOCKED_COMMANDS = [
    "format", "del /f", "rd /s", "shutdown",
    "diskpart", "mkfs", "rm -rf /", "reboot"
]

def is_safe_command(cmd: str):
    return not any(bad in cmd.lower() for bad in BLOCKED_COMMANDS)

# ── Extract Multiple Commands ────────────────────────
def extract_commands(text: str):
    matches = re.findall(r"CMD:\s*(.*)", text)

    cleaned_cmds = []
    for cmd in matches:
        cmd = re.sub(r"[`]", "", cmd)   # remove backticks
        cmd = cmd.strip()
        cleaned_cmds.append(cmd)

    return cleaned_cmds

# ── Crazy CLI Header UI ──────────────────────────────
def print_header():
    green = Fore.GREEN
    cyan = Fore.CYAN
    yellow = Fore.YELLOW
    magenta = Fore.MAGENTA
    white = Fore.WHITE

    print("\n" + green + "─" * 25 + " Welcome to " + "─" * 25 + "\n")

    logo = f"""
{green}        ██████╗███╗   ███╗██████╗      █████╗  ██████╗ ███████╗███╗   ██╗████████╗
{green}       ██╔════╝████╗ ████║██╔══██╗    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
{green}       ██║     ██╔████╔██║██║  ██║    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
{green}       ██║     ██║╚██╔╝██║██║  ██║    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
{green}       ╚██████╗██║ ╚═╝ ██║██████╔╝    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
{green}        ╚═════╝╚═╝     ╚═╝╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
"""

    print(logo)

    print(green + " " * 10 + "─" * 20 + " Version 1.0.0 " + "─" * 20 + "\n")

    print(cyan + " " * 12 + "⚡ Advanced AI Command Line Tool")
    print(magenta + " " * 12 + "Developed by V.N.D")
    print(yellow + " " * 12 + "Type 'exit' to quit\n")

    print(white + " " * 8 + "Here are some helpful commands to get started:\n")

    print(green + "\n" + "─" * 70 + "\n")

# ── Main ─────────────────────────────────────────────
def main():
    print_header()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            prompt = Fore.GREEN + "⚡ CMD-Agent " + Fore.WHITE + "➤ " + Style.RESET_ALL
            user_input = input(prompt).strip()

            if user_input.lower() in ["exit", "quit"]:
                print(Fore.GREEN + "\n👋 Goodbye!\n")
                break

            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model=model_id,
                messages=messages
            )

            reply = response.choices[0].message.content
            print(Fore.GREEN + f"\n🤖 Assistant:\n{reply}")

            # ── Extract ALL commands ─────────────────
            commands = extract_commands(reply)

            if not commands:
                messages.append({"role": "assistant", "content": reply})
                continue

            # ── Execute Commands One by One ──────────
            for cmd in commands:
                print(Fore.YELLOW + f"\n⚙️ Detected Command: {cmd}")

                if not is_safe_command(cmd):
                    print(Fore.RED + "🚫 Unsafe command blocked!")
                    continue

                confirm = input(Fore.CYAN + "Run command? (y/n): ").strip().lower()
                if confirm != "y":
                    print(Fore.RED + "❌ Skipped")
                    continue

                result = run_command(cmd)
                print(Fore.GREEN + f"\n📄 Output:\n{result}")

                messages.append({
                    "role": "assistant",
                    "content": f"Executed: {cmd}\nOutput:\n{result}"
                })

        except KeyboardInterrupt:
            print(Fore.RED + "\n👋 Interrupted")
            break

        except Exception as e:
            print(Fore.RED + f"\n[ERROR]: {str(e)}")

# ── Entry ────────────────────────────────────────────
if __name__ == "__main__":
    main()