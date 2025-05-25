import os
import tkinter as tk
from tkinter import scrolledtext, PhotoImage
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found. Please set it in a .env file.")
    exit()

def ask_gemini(message):
    """
    Calls the Gemini AI API to get a response.
    """
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    chat_history = []
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
            return result["candidates"][0]["content"]["parts"][0]["text"]
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
    
    # Check if the input is just the placeholder text or empty
    if user_input_text == PLACEHOLDER_TEXT or not user_input_text:
        return 

    # Display user message on the right
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "You: " + user_input_text + "\n", "user") # Apply 'user' tag
    chat_log.insert(tk.END, "\n") # Add an extra newline for spacing between messages
    chat_log.config(state=tk.DISABLED)
    
    input_field.delete(0, tk.END)
    # After sending, re-apply placeholder if field is empty (which it will be)
    set_placeholder()

    # Disable input and show typing indicator
    input_field.config(state=tk.DISABLED)
    send_button.config(state=tk.DISABLED)
    loading_label.config(text="Bot: Typing...", fg="#6c757d")
    root.update_idletasks() # Update GUI to show changes immediately

    bot_response = ask_gemini(user_input_text)

    # Display bot message on the left
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "Bot: " + bot_response + "\n", "bot") # Apply 'bot' tag
    chat_log.insert(tk.END, "\n") # Add an extra newline for spacing
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END) # Scroll to the end

    # Re-enable input and hide typing indicator
    input_field.config(state=tk.NORMAL)
    send_button.config(state=tk.NORMAL)
    loading_label.config(text="", fg="black") # Clear loading text
    input_field.focus_set() # Set focus back to input field

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
    input_field.insert(0, PLACEHOLDER_TEXT)
    input_field.config(fg=PLACEHOLDER_COLOR)
# --- End Placeholder functionality ---


# GUI window setup
root = tk.Tk()
root.title("Gemini AI Chatbot")
root.geometry("600x600") # Set initial window size
root.resizable(True, True) # Allow resizing

# Configure grid layout
root.grid_rowconfigure(0, weight=1) # Chat log expands vertically
root.grid_columnconfigure(0, weight=1) # Input field expands horizontally

# Chat log window
chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, 
                                     width=60, height=20, font=("Arial", 12),
                                     bg="#e9ecef", fg="#343a40",
                                     relief=tk.FLAT, bd=0) # Flat border
chat_log.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Configure tags for alignment and color
chat_log.tag_configure("user", foreground="#007bff", justify='right') # User messages on the right
chat_log.tag_configure("bot", foreground="#343a40", justify='left')   # Bot messages on the left

# Initial bot message
chat_log.config(state=tk.NORMAL)
chat_log.insert(tk.END, "Bot: Hello! How can I help you today?\n\n", "bot") # Apply 'bot' tag for initial message
chat_log.config(state=tk.DISABLED)

# Loading indicator label
loading_label = tk.Label(root, text="", font=("Arial", 10, "italic"), fg="#6c757d", anchor="w")
loading_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="ew")

# Input field
input_field = tk.Entry(root, width=60, font=("Arial", 12), relief=tk.FLAT, bd=1, highlightbackground="#ced4da", highlightthickness=1)
input_field.grid(row=2, column=0, padx=(10, 5), pady=(0, 10), sticky="ew")

# Bind placeholder events
input_field.bind("<FocusIn>", on_focus_in)
input_field.bind("<FocusOut>", on_focus_out)
input_field.bind("<Return>", lambda event=None: send_message()) # Bind Enter key

# Set initial placeholder
set_placeholder()

# Send button
send_button = tk.Button(root, text="Send", command=send_message, font=("Arial", 12, "bold"), 
                        bg="#082297", fg="white", activebackground="#4F7AC9", activeforeground="white",
                        relief=tk.GROOVE, bd=2) # Grooved border for a slightly raised effect
send_button.grid(row=2, column=1, padx=(5, 10), pady=(0, 10), sticky="e")

# Start the GUI loop
root.mainloop()