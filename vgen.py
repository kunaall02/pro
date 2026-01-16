import random
import string
import os
import subprocess
import sys

# Character: Haruki (Male, 18)
# "Fixed the path error and removed the headers. 
# It's just the raw codes now. Let's try again."

# ==========================================
# CONFIGURATION
# ==========================================
PREFIX = "SVD"
TOTAL_LENGTH = 15
BATCH_SIZE = 10000
OUTPUT_FILE = "vouchers.txt"
TARGET_SCRIPT = "gen.py"

def generate_vouchers(prefix, batch_size, length):
    print(f"[Haruki] Generating {batch_size} unique vouchers...")
    vouchers = set()
    suffix_length = length - len(prefix)
    chars = string.ascii_uppercase + string.digits
    
    while len(vouchers) < batch_size:
        suffix = ''.join(random.choices(chars, k=suffix_length))
        vouchers.add(f"{prefix}{suffix}")
    
    return list(vouchers)

def save_to_file(vouchers, filename):
    print(f"[Haruki] Saving raw codes to {filename}...")
    with open(filename, "w", encoding="utf-8") as f:
        # Strictly line by line, no extra headers
        for i, code in enumerate(vouchers):
            if i == len(vouchers) - 1:
                f.write(code) # No trailing newline on the last line
            else:
                f.write(f"{code}\n")
    print(f"[Haruki] Successfully saved {len(vouchers)} vouchers.")

def run_target_script(script_name):
    if os.path.exists(script_name):
        print(f"[Haruki] Launching {script_name}...")
        try:
            # sys.executable points to the current python3 path automatically
            subprocess.run([sys.executable, script_name], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[Haruki] The script returned an error: {e}")
        except KeyboardInterrupt:
            print("\n[Haruki] Process stopped. I'm heading out.")
    else:
        print(f"[Haruki] Error: {script_name} not found in {os.getcwd()}")

def main():
    # 1. Generate unique codes
    vouchers = generate_vouchers(PREFIX, BATCH_SIZE, TOTAL_LENGTH)
    
    # 2. Save raw to file
    save_to_file(vouchers, OUTPUT_FILE)
    
    # 3. Hand off to gen.py
    run_target_script(TARGET_SCRIPT)

if __name__ == "__main__":
    main()
