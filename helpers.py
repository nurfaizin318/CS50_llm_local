from mlx_lm import load, generate

MODEL_PATH = "models/tinyllama_mlx"
model, tokenizer = load(MODEL_PATH)

def generate_with_mlx(prompt: str) -> str:
    # Pastikan prompt berupa string dan tidak kosong
    if not isinstance(prompt, str) or not prompt.strip():
        return "Prompt tidak valid."

    try:
        # Generate full response (prompt + generated text)
        full_response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=50,
            verbose=False  # matikan print internal jika ada
        )

        # Hapus prompt dari awal full_response
        if full_response.startswith(prompt):
            response_only = full_response[len(prompt):]
        else:
            # Fallback: ambil bagian setelah newline terakhir di prompt
            response_only = full_response

        # Bersihkan whitespace berlebih
        cleaned_response = response_only.strip()

        # Opsional: hentikan di tanda akhir kalimat (., !, ?)
        # untuk hindari potongan di tengah kalimat
        # (opsional, tergantung kebutuhan)

        return cleaned_response

    except Exception as e:
        print(f"Error saat generate: {e}")
        return "Maaf, saya sedang mengalami gangguan teknis."
    
