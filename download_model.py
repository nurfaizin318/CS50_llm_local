from huggingface_hub import snapshot_download

MODEL_ID = "mlx-community/Llama-3.2-3B-Instruct-4bit"
LOCAL_DIR = "./models/tinyllama_mlx"

snapshot_download(
    repo_id=MODEL_ID,
    local_dir=LOCAL_DIR,
    local_dir_use_symlinks=False
)

print("Model MLX downloaded successfully!")
