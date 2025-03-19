from transformers import pipeline

# Load the model and save it locally
model_id = "kotoba-tech/kotoba-whisper-v2.2"
asr_pipeline = pipeline("automatic-speech-recognition", model=model_id)

# Save the model locally
asr_pipeline.save_pretrained("./local_kotoba_whisper_2_2")