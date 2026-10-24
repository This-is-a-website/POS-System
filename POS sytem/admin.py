import json
import random
import os
import subprocess
import platform
import time
import tkinter as tk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "gift_cards.json")

def load_database():
    """Loads data securely. Returns clean dictionary even if file has 1 or many items."""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            # Force parse as dict
            data = json.loads(content)
            if isinstance(data, dict):
                return data
            return {}
    except Exception as e:
        print(f"[SYSTEM WARNING] Resetting file read cache: {e}")
        return {}

def save_database(data):
    """Forces your operating system to write data to disk IMMEDIATELY."""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            f.flush()
            os.fsync(f.fileno())
        print(f"[DISK SAFE] Database saved securely with {len(data)} total code(s).")
    except Exception as e:
        print(f"[CRITICAL ERROR] Could not save data: {e}")

def copy_to_clipboard(text_content):
    """Ensures operating system captures text string natively."""
    current_os = platform.system()
    if current_os == "Windows":
        try:
            subprocess.run("clip", input=text_content, text=True, check=True)
            return True
        except Exception:
            pass
    try:
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text_content)
        root.update()
        time.sleep(0.5)
        root.destroy()
        return True
    except Exception:
        return False

def encode_name(name):
    """Converts text characters to string numbers."""
    return "-".join(str(ord(char)) for char in name)

def decode_name(encoded_str):
    """Converts string numbers back to clear text."""
    try:
        return "".join(chr(int(code)) for code in encoded_str.split("-"))
    except:
        return "Unknown User"

def generate_short_code():
    """Generates standard XXXX-XXXX formatted cards."""
    part1 = "".join(str(random.randint(0, 9)) for _ in range(4))
    part2 = "".join(str(random.randint(0, 9)) for _ in range(4))
    return f"{part1}-{part2}"

def main():
    print(f"--- SYSTEM ONLINE ---")
    print(f"Target Database File: {DB_FILE}\n")
    
    while True:
        print("\n=== REGISTRY CONTROLLER ===")
        print("1. Generate a Small Code")
        print("2. Look Up Code Info")
        print("3. Add Money to a Code")
        print("4. Paste Updated JSON Database (From POS HTML)")
        print("5. Copy Database to Clipboard (For POS HTML Setup)")
        print("6. Exit")
        choice = input("Select an option (1-6): ")

        if choice == "1":
            # FIXED: Always read existing file items first so we ADD to them instead of locking up!
            db = load_database()
            
            name = input("Enter cardholder name: ")
            try:
                balance = float(input("Enter starting balance ($): "))
                
                code = generate_short_code()
                while code in db:
                    code = generate_short_code()
                
                db[code] = {
                    "encoded_name": encode_name(name),
                    "balance": balance
                }
                
                save_database(db)
                print(f"\n[SUCCESS] New card added alongside existing codes.")
                print(f"Code to use: {code}")
            except ValueError:
                print("[ERROR] Balance must be a clean number.")

        elif choice == "2":
            code = input("Enter code (XXXX-XXXX): ").strip()
            db = load_database()
            if code in db:
                real_name = decode_name(db[code]["encoded_name"])
                print("\n=== SYSTEM DATA CARD ===")
                print(f"User Identification: {real_name}")
                print(f"Encrypted Registry:   {db[code]['encoded_name']}")
                print(f"Balance Matrix:       ${db[code]['balance']:.2f}")
            else:
                print("[ERROR] Code token not registered.")

        elif choice == "3":
            code = input("Enter code (XXXX-XXXX): ").strip()
            db = load_database()
            if code in db:
                real_name = decode_name(db[code]["encoded_name"])
                print(f"\nCardholder: {real_name}")
                print(f"Current Value: ${db[code]['balance']:.2f}")
                try:
                    amount_to_add = float(input("Enter load amount ($): "))
                    db[code]["balance"] += amount_to_add
                    save_database(db)
                    print(f"[SUCCESS] Code balance updated to: ${db[code]['balance']:.2f}")
                except ValueError:
                    print("[ERROR] Invalid number format.")
            else:
                print("[ERROR] Code token not registered.")

        elif choice == "4":
            print("\n--- PASTE DATABASE CONTENT ---")
            print("Paste the exact text from the bottom of your HTML checkout screen and press Enter:")
            raw_input = input().strip()
            try:
                parsed_data = json.loads(raw_input)
                if isinstance(parsed_data, dict):
                    save_database(parsed_data)
                    print("[SUCCESS] The database file has been successfully overwritten and synced!")
                else:
                    print("[ERROR] Input data format error.")
            except json.JSONDecodeError:
                print("[ERROR] Invalid JSON data string.")

        elif choice == "5":
            db = load_database()
            raw_json_string = json.dumps(db)
            if copy_to_clipboard(raw_json_string):
                print(f"\n[SUCCESS] All {len(db)} card(s) copied directly to your clipboard!")
            else:
                print("\n[ERROR] Automated clipboard action failed.")

        elif choice == "6":
            print("System down.")
            break
        else:
            print("[ERROR] Invalid selection option.")

if __name__ == "__main__":
    main()
