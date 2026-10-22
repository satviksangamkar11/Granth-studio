"""UNVALIDATED reference runner for IndicTrans2 (O-007). Never executed on this project.

Written from the model's published usage and NOT checked against a pinned release: pick the
checkpoint and IndicTransToolkit revision, run it once on the GPU host, review real output, and
only then set models.yaml translation.status to validated. Dependencies (torch, transformers,
IndicTransToolkit) are installed on the GPU host only, never in this repository.

Contract (see src/granthstudio/runners.py):
  stdin  {"src_lang": "mar_Deva", "tgt_lang": "hin_Deva", "texts": [...]}
  stdout {"translations": [...]}
Environment: INDICTRANS2_CHECKPOINT = local directory or hub id of the pinned checkpoint.
"""
import json
import os
import sys


def main() -> None:
    payload = json.load(sys.stdin)
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    from IndicTransToolkit.processor import IndicProcessor

    checkpoint = os.environ["INDICTRANS2_CHECKPOINT"]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = IndicProcessor(inference=True)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint, trust_remote_code=True).to(device)
    batch = processor.preprocess_batch(payload["texts"], src_lang=payload["src_lang"], tgt_lang=payload["tgt_lang"])
    inputs = tokenizer(batch, truncation=True, padding="longest", return_tensors="pt").to(device)
    with torch.no_grad():
        tokens = model.generate(**inputs, use_cache=True, max_length=256, num_beams=5, num_return_sequences=1)
    decoded = tokenizer.batch_decode(tokens.detach().cpu().tolist(), skip_special_tokens=True, clean_up_tokenization_spaces=True)
    print(json.dumps({"translations": processor.postprocess_batch(decoded, lang=payload["tgt_lang"])}, ensure_ascii=True))


if __name__ == "__main__":
    main()
