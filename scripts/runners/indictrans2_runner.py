"""UNVALIDATED reference runner for IndicTrans2 (O-007). Never executed on this project.

Written from the model's published usage and NOT checked against a pinned release: pick the
checkpoint and IndicTransToolkit revision, run it once on the GPU host, review real output, and
only then set models.yaml translation.status to validated. Dependencies (torch, transformers,
IndicTransToolkit) are installed on the GPU host only, never in this repository.

Contract (see src/granthstudio/runners.py):
  stdin  {"src_lang": "mar_Deva", "tgt_lang": "hin_Deva", "texts": [...], "model", "revision"}
  stdout {"translations": [...], "verified": {"model", "revision"}}
The payload carries the approved model and revision (config/models.yaml translation). The checkpoint is loaded at that
revision and must prove it (config._commit_hash); otherwise the runner exits non-zero. INDICTRANS2_CHECKPOINT, if set,
may only restate the approved model; it cannot substitute other weights.
"""
import json
import sys

from _identity import IdentityError, approved_identity, verified_identity


def main() -> None:
    payload = json.load(sys.stdin)
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    from IndicTransToolkit.processor import IndicProcessor

    checkpoint, revision = approved_identity(payload, "INDICTRANS2_CHECKPOINT")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = IndicProcessor(inference=True)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint, revision=revision, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint, revision=revision, trust_remote_code=True)
    verified = verified_identity(checkpoint, revision, getattr(getattr(model, "config", None), "_commit_hash", None))
    model = model.to(device)
    batch = processor.preprocess_batch(payload["texts"], src_lang=payload["src_lang"], tgt_lang=payload["tgt_lang"])
    inputs = tokenizer(batch, truncation=True, padding="longest", return_tensors="pt").to(device)
    with torch.no_grad():
        tokens = model.generate(**inputs, use_cache=True, max_length=256, num_beams=5, num_return_sequences=1)
    decoded = tokenizer.batch_decode(tokens.detach().cpu().tolist(), skip_special_tokens=True, clean_up_tokenization_spaces=True)
    print(json.dumps({"translations": processor.postprocess_batch(decoded, lang=payload["tgt_lang"]), "verified": verified},
                     ensure_ascii=True))


if __name__ == "__main__":
    try:
        main()
    except IdentityError as exc:
        print(f"model identity check failed: {exc}", file=sys.stderr)
        sys.exit(2)
