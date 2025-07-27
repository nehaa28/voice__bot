# from llama_cpp import Llama

# #llm = Llama(model_path="models/ggml-mistral-7b-instruct.q4_0.bin")
# llm = Llama(model_path="models/tinyllama.gguf")

# def generate_response(prompt: str) -> str:
#     response = llm(f"Q: {prompt}\nA:", max_tokens=200)
#     return response["choices"][0]["text"].strip()

from transformers import pipeline

interviewer = pipeline("text-generation", model="tiiuae/falcon-rw-1b")  # free and small

def generate_response(prompt):
    result = interviewer(f"### Interviewer:\n{prompt}\n### Candidate:", max_length=100, do_sample=True)
    return result[0]["generated_text"].split("### Candidate:")[-1].strip()
