import os
import tkinter as tk
from tkinter import scrolledtext
import requests
from dotenv import load_dotenv

# Load API key from .env file
# Create a .env file in the same directory as this script and add:
# GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API key is loaded
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
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
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
    if not user_input_text:
        return # Don't send empty messages

    # Display user message
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "You: " + user_input_text + "\n")
    chat_log.config(state=tk.DISABLED)
    input_field.delete(0, tk.END)

    # Disable input and show typing indicator
    input_field.config(state=tk.DISABLED)
    send_button.config(state=tk.DISABLED)
    loading_label.config(text="Bot: Typing...", fg="#6c757d")
    root.update_idletasks() # Update GUI to show changes immediately

    # Get bot response (run in a separate thread for non-blocking UI if complex,
    # but for simple requests, it's often fine to block briefly)
    # For a more robust solution, especially for long-running API calls,
    # consider using threading or asyncio. For this example, we'll keep it synchronous for simplicity.
    bot_response = ask_gemini(user_input_text)

    # Display bot message
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "Bot: " + bot_response + "\n\n")
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END) # Scroll to the end

    # Re-enable input and hide typing indicator
    input_field.config(state=tk.NORMAL)
    send_button.config(state=tk.NORMAL)
    loading_label.config(text="", fg="black") # Clear loading text
    input_field.focus_set() # Set focus back to input field

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
chat_log.tag_configure("user", foreground="#007bff", justify='right')
chat_log.tag_configure("bot", foreground="#343a40", justify='left')

# Initial bot message
chat_log.config(state=tk.NORMAL)
chat_log.insert(tk.END, "Bot: Hello! How can I help you today?\n\n")
chat_log.config(state=tk.DISABLED)

# Loading indicator label
loading_label = tk.Label(root, text="", font=("Arial", 10, "italic"), fg="#6c757d", anchor="w")
loading_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="ew")

# Input field
input_field = tk.Entry(root, width=60, font=("Arial", 12), relief=tk.FLAT, bd=1, highlightbackground="#ced4da", highlightthickness=1)
input_field.grid(row=2, column=0, padx=(10, 5), pady=(0, 10), sticky="ew")
input_field.bind("<Return>", lambda event=None: send_message()) # Bind Enter key

# Send button
send_button = tk.Button(root, text="Send", command=send_message, font=("Arial", 12, "bold"), 
                        bg="#28a745", fg="white", activebackground="#218838", activeforeground="white",
                        relief=tk.GROOVE, bd=2) # Grooved border for a slightly raised effect
send_button.grid(row=2, column=1, padx=(5, 10), pady=(0, 10), sticky="e")

# Start the GUI loop
root.mainloop()
