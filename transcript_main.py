import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from subprocess import Popen, PIPE
import threading
import requests
from pydub import AudioSegment  # Import pydub for audio conversion
import torch  # Import PyTorch

# Set the device for PyTorch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")  # Print the device being used

# Global variable to store the transcription result
transcription_result = ""

# Function to check internet connection
def check_internet_connection():
    try:
        response = requests.get("https://www.google.com", timeout=5)
        response.raise_for_status()  # Raise an error for bad responses
        return True
    except requests.RequestException:
        return False

# Function to convert MP4 to WAV
def convert_mp4_to_wav(mp4_file, wav_file):
    try:
        output_text.insert(tk.END, "Converting file to wav .....\n")
        audio = AudioSegment.from_file(mp4_file, format="mp4")
        audio.export(wav_file, format="wav", parameters=["-sample_fmt", "s16"], tags={"title": "Converted Audio"})
        output_text.insert(tk.END, "Conversion completed successfully.\n")
        output_text.see(tk.END)  # Scroll to the end
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to convert MP4 to WAV: {str(e)}")
        return False

# Function to run the transcription script
def run_transcription():
    global transcription_result  # Use the global variable
    #if not check_internet_connection():
    #    messagebox.showerror("Error", "No internet connection. Please check your network settings.")
    #    return

    mp4_file = filedialog.askopenfilename(title="Select MP4 File", filetypes=[("MP4 Files", "*.mp4")])
    if not mp4_file:
        return

    wav_file = os.path.splitext(mp4_file)[0] + ".wav"

    transcribe_button.config(state=tk.DISABLED)
    progress_bar.start()
    output_text.delete(1.0, tk.END)

    def run_conversion():
        if not convert_mp4_to_wav(mp4_file, wav_file):
            return

        output_text.insert(tk.END, "Transcribing MOM .....\n")

        command = f'python "{os.path.abspath("transcript.py")}" "{os.path.abspath(wav_file)}"'

        def run_command():
            global transcription_result  # Use the global variable
            try:
                print(f"Running command: {command}")
                process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)

                def read_output(stream):
                    for line in iter(stream.readline, ''):
                        output_text.insert(tk.END, line)
                        output_text.see(tk.END)  # Scroll to the end
                        output_text.update_idletasks()  # Update the GUI

                stdout_thread = threading.Thread(target=read_output, args=(process.stdout,))
                stderr_thread = threading.Thread(target=read_output, args=(process.stderr,))

                stdout_thread.start()
                stderr_thread.start()

                # Wait for the process to complete
                process.wait()

                # Wait for the threads to finish
                stdout_thread.join()
                stderr_thread.join()

                # Check the return code
                if process.returncode != 0:
                    output_text.insert(tk.END, f"Process exited with code {process.returncode}\n")
                else:
                    # Read the transcription result from the file
                    with open("transcription_result.txt", "r", encoding="utf-8") as f:
                        transcription_result = f.read()  # Store the transcription result
                    output_text.insert(tk.END, "Transcription completed successfully.\n")
                    download_button.config(state=tk.NORMAL)  # Enable the download button

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while running the transcription: {str(e)}")
            finally:
                progress_bar.stop()
                transcribe_button.config(state=tk.NORMAL)
                #if os.path.exists(wav_file):
                    #os.remove(wav_file)

        threading.Thread(target=run_command).start()

    threading.Thread(target=run_conversion).start()

# Function to download the transcription result
def download_transcription():
    if not transcription_result:
        messagebox.showwarning("Warning", "No transcription available to download.")
        return

    # Prompt user to select a location to save the transcription
    save_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if save_file:
        try:
            with open(save_file, 'w', encoding='utf-8') as f:
                f.write(transcription_result)  # Save the transcription result
            messagebox.showinfo("Success", "Transcription downloaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save transcription: {str(e)}")

# Create the main application window
root = tk.Tk()
root.title("Minute Of Meeting Transcription App")

# Set the window size (width x height)
window_width = 600
window_height = 400

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the x and y coordinates to center the window
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)

# Set the geometry of the window
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Create a button to run the transcription with increased size
transcribe_button = tk.Button(root, text="Choose MOM File", command=run_transcription, width=20, height=2)
transcribe_button.grid(row=0, column=0, padx=10, pady=10, sticky='w')  # Align to the left

# Create a progress bar
progress_bar = ttk.Progressbar(root, mode='indeterminate')
progress_bar.grid(row=0, column=1, padx=10, pady=10, sticky='e')  # Align to the right

# Create a Text widget for output with black background and white text
output_text = tk.Text(root, wrap=tk.WORD, height=10, bg="black", fg="white", insertbackground='white')
output_text.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 20), sticky='nsew')  # Fill both columns

# Create a button to download the transcription result
download_button = tk.Button(root, text="Download Transcription", command=download_transcription, width=20, height=2)
download_button.grid(row=2, column=0, padx=10, pady=10, sticky='w')  # Align to the left
download_button.config(state=tk.DISABLED)  # Initially disabled

# Configure grid weights to allow resizing
root.grid_rowconfigure(1, weight=1)  # Allow the text area to expand
root.grid_columnconfigure(0, weight=1)  # Allow the button column to expand
root.grid_columnconfigure(1, weight=0)  # Keep the progress bar column fixed

# Run the application
root.mainloop()