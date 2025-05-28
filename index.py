import os
import sys
import tkinter as tk
from tkinter import scrolledtext
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found. Please set it in a .env file.")
    sys.exit(1)

# Global chat history to maintain context
chat_history = []

def ask_gemini(message):
    """
    Calls the Gemini AI API to get a response.
    """
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Append the current user message to the chat history
    chat_history.append({"role": "user", "parts": [{"text": message}]})

    payload = {
        "contents": chat_history
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()

        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0:
            bot_response = result["candidates"][0]["content"]["parts"][0]["text"]
            # Append the bot's response to the chat history
            chat_history.append({"role": "model", "parts": [{"text": bot_response}]})
            return bot_response
        else:
            print("Unexpected Gemini API response structure:", result)
            return "Error: Could not get a valid response from Gemini AI."
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {response.text}")
        return f"Error: API request failed with status {response.status_code}"
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return "Error: Could not connect to the Gemini API. Check your internet connection."
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return "Error: Gemini API request timed out."
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected request error occurred: {req_err}")
        return f"Error: An unexpected error occurred during the API request."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"Error: {e}"

def send_message():
    """
    Handles sending a message from the user and displaying the bot's response.
    """
    user_input_text = input_field.get().strip()
    
    # If the input is empty or just the placeholder, do nothing
    if not user_input_text or user_input_text == PLACEHOLDER_TEXT:
        return 

    # Display user message on the right
    chat_log.config(state=tk.NORMAL)
    # The message is inserted within a smaller lmargin/rmargin to simulate a bubble
    chat_log.insert(tk.END, "You: " + user_input_text + "\n", "user")
    chat_log.insert(tk.END, "\n") # Add a blank line for spacing between bubbles
    chat_log.config(state=tk.DISABLED)
    
    # Clear input field and set placeholder after displaying user message
    input_field.delete(0, tk.END)
    set_placeholder()

    # Disable input and show typing indicator
    input_field.config(state=tk.DISABLED)
    send_button.config(state=tk.DISABLED)
    loading_label.config(text="Bot: Typing...", fg="#6c757d")
    root.update_idletasks()

    bot_response = ask_gemini(user_input_text)

    # Display bot message on the left
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "Bot: " + bot_response + "\n", "bot")
    chat_log.insert(tk.END, "\n") # Add a blank line for spacing between bubbles
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END)

    # Re-enable input and hide typing indicator
    input_field.config(state=tk.NORMAL)
    send_button.config(state=tk.NORMAL)
    loading_label.config(text="", fg="black")
    input_field.focus_set()

# --- Placeholder functionality ---
PLACEHOLDER_TEXT = "Ask me a question..."
PLACEHOLDER_COLOR = '#888888'
NORMAL_TEXT_COLOR = '#000000'

def on_focus_in(event):
    if input_field.get() == PLACEHOLDER_TEXT:
        input_field.delete(0, tk.END)
        input_field.config(fg=NORMAL_TEXT_COLOR)

def on_focus_out(event):
    if not input_field.get():
        set_placeholder()

def set_placeholder():
    input_field.delete(0, tk.END)
    input_field.insert(0, PLACEHOLDER_TEXT)
    input_field.config(fg=PLACEHOLDER_COLOR)
# --- End Placeholder functionality ---

# --- GUI Setup ---

root = tk.Tk()
root.title("Gemini AI Chatbot")
root.geometry("700x700")
root.configure(bg="#F4F6F8")  # Light gray background
root.resizable(True, True)

# Fonts and Colors
FONT = ("Segoe UI", 12)
USER_TEXT_COLOR = "#FFFFFF" # White text for user bubble
BOT_TEXT_COLOR = "#263238"  # Original bot text color
USER_BUBBLE_BG = "#1E88E5" # Blue background for user bubble
BOT_BUBBLE_BG = "#E0E0E0" # Light gray background for bot bubble
BG_COLOR = "#F4F6F8" # Main window background
INPUT_BG = "#FFFFFF"
BUTTON_BG = "#0D47A1"
BUTTON_HOVER = "#1565C0"

# Configure layout
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Chat log styling
chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED,
                                     font=FONT, bg=BG_COLOR, fg=BOT_TEXT_COLOR, # Chat log background matches window
                                     relief=tk.FLAT, bd=0)
chat_log.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

# Configure tags for user and bot messages
chat_log.tag_configure("user",
                       foreground=USER_TEXT_COLOR, # White text
                       background=USER_BUBBLE_BG,  # Blue background
                       justify='right',
                       lmargin1=250,  # Indent from left for user messages
                       rmargin=20,    # Right margin for user messages
                       spacing1=5,    # Space above the tagged line
                       spacing3=5,    # Space below the tagged line
                       lmargin2=250   # Used for subsequent lines of a wrapped tag
                       )

chat_log.tag_configure("bot",
                       foreground=BOT_TEXT_COLOR,
                       background=BOT_BUBBLE_BG, # Light gray background
                       justify='left',
                       lmargin1=20,   # Left margin for bot messages
                       rmargin=250,   # Indent from right for bot messages
                       spacing1=5,    # Space above the tagged line
                       spacing3=5,    # Space below the tagged line
                       lmargin2=20    # Used for subsequent lines of a wrapped tag
                       )

chat_log.config(state=tk.NORMAL)
chat_log.insert(tk.END, "Bot: Hello! How can I help you today?\n", "bot")
chat_log.insert(tk.END, "\n") # Extra newline for spacing
chat_log.config(state=tk.DISABLED)

# Loading label
loading_label = tk.Label(root, text="", font=("Segoe UI", 10, "italic"), fg="#6c757d", bg=BG_COLOR, anchor="w")
loading_label.grid(row=1, column=0, columnspan=2, padx=20, sticky="ew")

input_frame = tk.Frame(root, bg=INPUT_BG, highlightthickness=2, highlightbackground=BUTTON_BG, highlightcolor=BUTTON_BG)
input_frame.grid(row=2, column=0, padx=(20, 10), pady=(0, 20), sticky="ew", ipady=8)

input_field = tk.Entry(input_frame, font=FONT, bg=INPUT_BG, relief=tk.FLAT, fg=PLACEHOLDER_COLOR, bd=0)
input_field.pack(fill="both", expand=True, ipady=6)

input_field.bind("<FocusIn>", on_focus_in)
input_field.bind("<FocusOut>", on_focus_out)
input_field.bind("<Return>", lambda event=None: send_message())

set_placeholder()

# Send Button
send_button = tk.Button(root, text="Send", command=send_message, font=("Segoe UI", 10, "bold"),
                         bg=BUTTON_BG, fg="white", relief=tk.FLAT, padx=10, pady=5)
send_button.grid(row=2, column=1, padx=(10, 20), pady=(0, 20), sticky="e")

# Hover effect
def on_enter(e):
    send_button.config(bg=BUTTON_HOVER)
def on_leave(e):
    send_button.config(bg=BUTTON_BG)

send_button.bind("<Enter>", on_enter)
send_button.bind("<Leave>", on_leave)

root.mainloop()