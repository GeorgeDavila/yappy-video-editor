"""Speech restoration / enhancement via nineninesix/diamond-1.0.

Install:
  pip install "diamond-s2s[mp3] @ git+https://github.com/nineninesix-ai/diamond-inference.git"

Model: https://huggingface.co/nineninesix/diamond-1.0
Inference: https://github.com/nineninesix-ai/diamond-inference
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from huggingface_hub import hf_hub_download

HF_REPO = "nineninesix/diamond-1.0"
WEIGHTS_FILE = "diamond.safetensors"
CONFIG_FILE = "diamond.json"


def _default_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def download_checkpoint(
    repo_id: str = HF_REPO,
    weights: str = WEIGHTS_FILE,
    config: str = CONFIG_FILE,
) -> str:
    """Download Diamond weights + config sidecar; return path to .safetensors."""
    ckpt_path = hf_hub_download(repo_id, weights)
    hf_hub_download(repo_id, config)  # sibling .json in the same snapshot dir
    return ckpt_path


def _load_audio(path: str | Path) -> tuple[np.ndarray, int]:
    path = str(path)
    try:
        wav, sr = sf.read(path, dtype="float32", always_2d=False)
    except Exception:
        import librosa

        wav, sr = librosa.load(path, sr=None, mono=True)
        wav = wav.astype(np.float32)
    if isinstance(wav, np.ndarray) and wav.ndim > 1:
        wav = wav.mean(axis=-1)
    return wav, int(sr)


class DiamondEnhance:
    """Offline speech restoration with Diamond (44.1 kHz output)."""

    def __init__(
        self,
        checkpoint: str | None = None,
        device: str | None = None,
        repo_id: str = HF_REPO,
    ):
        from diamond import Diamond  # lazy — optional / heavy dependency

        self.device = device or _default_device()
        ckpt = checkpoint or download_checkpoint(repo_id=repo_id)
        self.model = Diamond.from_pretrained(ckpt, device=self.device)

    def enhance(
        self,
        wav: np.ndarray,
        sample_rate: int,
        *,
        chunk_sec: float = 2.5,
        overlap_sec: float = 0.4,
        warmup_sec: float = 1.0,
        tail_pad_sec: float = 1.0,
        rep_penalty: float = 1.3,
        normalize: bool = True,
        trim_leadin: bool = True,
        recover_collapse: bool = True,
        seed: int = 42,
    ) -> tuple[np.ndarray, int]:
        """Restore a waveform in memory. Returns (restored_wav, out_sr)."""
        from diamond import SampleConfig

        torch.manual_seed(seed)
        np.random.seed(seed)

        return self.model.restore(
            wav,
            sample_rate,
            chunk_sec=chunk_sec,
            overlap_sec=overlap_sec,
            warmup_sec=warmup_sec,
            tail_pad_sec=tail_pad_sec,
            normalize=normalize,
            trim_leadin=trim_leadin,
            recover_collapse=recover_collapse,
            sample=SampleConfig(rep_penalty=rep_penalty),
        )

    def enhance_file(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        **kwargs,
    ) -> str:
        """Restore an audio file to a 44.1 kHz WAV. Returns output path."""
        input_path = Path(input_path)
        if output_path is None:
            output_path = input_path.with_name(f"{input_path.stem}_restored.wav")
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        wav, sr = _load_audio(input_path)
        restored, out_sr = self.enhance(wav, sr, **kwargs)
        sf.write(str(output_path), restored, out_sr, subtype="PCM_16")
        return str(output_path)


def enhance_audio(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    checkpoint: str | None = None,
    device: str | None = None,
    **kwargs,
) -> str:
    """One-shot restore: load Diamond, enhance file, return output path."""
    enhancer = DiamondEnhance(checkpoint=checkpoint, device=device)
    return enhancer.enhance_file(input_path, output_path, **kwargs)


if __name__ == "__main__":
    audio_path = os.environ.get("DIAMOND_INPUT", "data/feudalism.mp3")
    out = enhance_audio(audio_path)
    print(f"Restored audio written to: {out}")
