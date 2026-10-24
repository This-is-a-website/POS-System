from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import time
import tkinter as tk
from tkinter import filedialog

# Global variable to store the path of the selected file
SELECTED_FILE_PATH = ""


class JSONStreamingHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global SELECTED_FILE_PATH

        # 1. Double check if a file was selected and still exists
        if not SELECTED_FILE_PATH or not os.path.exists(SELECTED_FILE_PATH):
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(
                b"Error: No JSON file selected or the file no longer exists."
            )
            return

        # 2. Send successful HTTP streaming headers
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()

        try:
            # 3. Read and parse the selected JSON file
            with open(SELECTED_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert to a pretty-printed string format
            json_string = json.dumps(data, indent=4)

            print(f"\n[!] Streaming {os.path.basename(SELECTED_FILE_PATH)}...")

            # 4. Stream the JSON string line by line
            for line in json_string.splitlines(keepends=True):
                chunk = line.encode("utf-8")

                # Format as a standard HTTP chunk: hex(length) + \r\n + data + \r\n
                self.wfile.write(f"{len(chunk):X}\r\n".encode("utf-8"))
                self.wfile.write(chunk + b"\r\n")
                self.wfile.flush()  # Force send to browser immediately

                time.sleep(0.15)  # Delay in seconds between lines

            # Send the final empty chunk to signal the end of the stream
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
            print("[+] Streaming complete.")

        except json.JSONDecodeError:
            print("\nError: The selected file is not valid JSON.")
        except (ConnectionResetError, BrokenPipeError):
            print("\nClient disconnected early.")


def pick_json_file():
    """Opens a native file dialog window to choose a JSON file."""
    root = tk.Tk()
    root.withdraw()  # Hide the main tiny tkinter window
    root.attributes("-topmost", True)  # Bring the file dialog to the front

    print("Opening file picker... Please select a JSON file.")
    file_path = filedialog.askopenfilename(
        title="Select a JSON file to stream",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    )

    return file_path


def run_server():
    global SELECTED_FILE_PATH

    # Prompt the user to pick a file before starting the server
    SELECTED_FILE_PATH = pick_json_file()

    if not SELECTED_FILE_PATH:
        print("No file selected. Exiting script.")
        return

    print(f"[+] Loaded file: {SELECTED_FILE_PATH}")

    port = 2017
    server_address = ("", port)
    httpd = HTTPServer(server_address, JSONStreamingHandler)
    print(f"[+] Streaming server running on http://localhost:{port}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
