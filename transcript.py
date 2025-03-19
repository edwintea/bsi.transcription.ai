import sys
import time  # For simulating progress
from pydub import AudioSegment
import torch
from transformers import pipeline


# Function to convert MP3 to WAV
def convert_mp3_to_wav(mp3_file, wav_file):
    """Convert MP3 file to WAV format."""
    audio = AudioSegment.from_mp3(mp3_file)
    audio.export(wav_file, format="wav")
    print(f"Converted {mp3_file} to {wav_file}")


# Function to transcribe audio and save to a text file
# Function to transcribe audio and save to a text file
def transcribe_audio(wav_file):
    """Transcribe the given WAV file and save the transcription to a text file."""
    # Model Configuration
    #model_id = "kotoba-tech/kotoba-whisper-v2.2"
    model_id = "./kotoba-whisper-v2.0-banana"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    model_kwargs = {"attn_implementation": "sdpa"} if torch.cuda.is_available() else {}

    # Enable timestamp generation and set language to English if needed
    generate_kwargs = {
        #"language": "japanese",  # Set to 'en' if you want to always translate to English
        #"task": "transcribe",
        "return_timestamps": True  # Enable timestamp generation
    }

    # Load Model
    try:
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model_id,
            torch_dtype=torch_dtype,
            device=device,
            model_kwargs=model_kwargs,
            # chunk_length_s=15,
            # batch_size=16
        )
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Check if using GPU
    if torch.cuda.is_available():
        print("Using GPU for transcription.")
    else:
        print("Using CPU for transcription.")

    # Enable long-form generation for longer audio files
    print("Starting transcription...")

    # Start time for transcription
    start_time = time.time()

    # Transcribe the provided WAV file
    try:
        result = pipe(wav_file, **generate_kwargs)  # Use unpacking for generate_kwargs
        print(result["text"])  # Print the transcribed text
        print(result["chunks"])  # Print the timestamped chunks
    except Exception as e:
        print(f"Error during transcription: {e}")
        return

    # End time for transcription
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Transcription completed in {elapsed_time:.2f} seconds.")

    # Save transcription to a text file
    transcription_file = "transcription_result.txt"
    try:
        with open(transcription_file, "w", encoding="utf-8") as f:
            f.write(result["text"])
        print(f"Transcription saved to {transcription_file}")
    except Exception as e:
        print(f"Error saving transcription: {e}")


# Main function
def main():
    if len(sys.argv) < 2:
        print("Please provide a WAV or MP3 file.")
        return

    input_file = sys.argv[1]  # Get the input file from command line arguments
    wav_file = "converted_audio.wav"  # Temporary WAV file name

    # Check the file extension
    if input_file.lower().endswith('.mp3'):
        convert_mp3_to_wav(input_file, wav_file)
    elif input_file.lower().endswith('.wav'):
        wav_file = input_file
    else:
        print("Unsupported file format. Please provide a WAV or MP3 file.")
        return

    # Call the transcription function
    transcribe_audio(wav_file)
    print("Transcription completed.")


if __name__ == "__main__":
    main()