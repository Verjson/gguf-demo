#!/usr/bin/env python3
"""
Step 5 — Domain fine-tuning with LoRA on instruction QA pairs.

Prefers data/processed/qa_pairs.jsonl (from 01b_generate_qa_pairs.py):
  ### Context / ### Question / ### Answer

Falls back to abstract-style pairs if qa_pairs.jsonl is missing.
"""

from __future__ import annotations

import json
import logging
import os
import sys

import mlflow
import torch
import yaml
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cpu_runtime import configure_threads
from src.hardware import detect_hardware
from src.mlflow_tracker import init_mlflow_experiment
from src.resource_metrics import memory_snapshot

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/app/config/config.yaml")


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_qa_pairs(processed_dir: str) -> list[dict]:
    path = os.path.join(processed_dir, "qa_pairs.jsonl")
    if not os.path.isfile(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if row.get("split", "train") == "train":
                rows.append(row)
    return rows


def format_qa_example(row: dict) -> str:
    """Instruction format that teaches the model to use context."""
    return (
        f"### Context:\n{row.get('context', '')}\n\n"
        f"### Question:\n{row['question']}\n\n"
        f"### Answer:\n{row['answer']}"
    )


def fallback_from_metadata(papers_dir: str) -> list[dict]:
    meta_path = os.path.join(papers_dir, "papers_metadata.json")
    if not os.path.isfile(meta_path):
        return []
    records = []
    for paper in json.loads(open(meta_path, encoding="utf-8").read()):
        title = paper.get("title", "Unknown")
        summary = paper.get("summary", "")
        if not summary:
            continue
        records.append(
            {
                "question": f"Summarize the research paper '{title}'.",
                "answer": summary,
                "context": summary,
            }
        )
    return records


def main() -> None:
    hardware = detect_hardware()
    config = load_config()
    papers_dir = config.get("paths", {}).get("papers_dir", "/app/data/papers")
    processed_dir = config.get("paths", {}).get("processed_dir", "/app/data/processed")
    output_dir = os.path.join(
        config.get("paths", {}).get("models_dir", "/app/models"), "fine_tuned"
    )

    records = load_qa_pairs(processed_dir)
    if not records:
        logger.warning("No qa_pairs.jsonl train split — falling back to abstracts")
        records = fallback_from_metadata(papers_dir)
    if not records:
        raise SystemExit(
            "No training data. Run 01_download_papers.py and 01b_generate_qa_pairs.py first."
        )

    logger.info("Fine-tuning on %d examples | %s", len(records), hardware.summary())

    configure_threads()
    init_mlflow_experiment()

    ft = config["fine_tuning"]
    base_model = ft["base_model"]
    use_cuda = hardware.cuda_available

    with mlflow.start_run(run_name=f"lora-finetune@{hardware.device}"):
        mlflow.set_tag("stage", "fine_tune")
        mlflow.set_tag("device", hardware.device)
        mlflow.log_params(
            {
                "base_model": base_model,
                "lora_r": ft.get("lora_r", 8),
                "lora_alpha": ft.get("lora_alpha", 16),
                "epochs": ft["epochs"],
                "batch_size": ft["batch_size"],
                "learning_rate": ft["learning_rate"],
                "n_train": len(records),
                **{k: str(v) for k, v in hardware.as_params().items()},
            }
        )

        base_revision = ft.get("base_revision")
        tokenizer = AutoTokenizer.from_pretrained(base_model, revision=base_revision)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            revision=base_revision,
            # bf16 on Ampere+ GPUs: half memory vs fp32, better numerical range than fp16
            # for training. fp32 on CPU so we do not need CUDA AMP there.
            torch_dtype=torch.bfloat16 if use_cuda else torch.float32,
            device_map={"": 0} if use_cuda else None,
            low_cpu_mem_usage=True,
        )

        # Attention projections only: q/k/v/o dominate generation behavior for instruction
        # following, while leaving MLP/embed frozen reduces trainable size and overfitting
        # risk on a handful of paper-derived Q&A pairs.
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=ft.get("lora_r", 8),
            lora_alpha=ft.get("lora_alpha", 16),
            # Light dropout regularizes adapters when n_train is small.
            lora_dropout=0.05,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        )
        model = get_peft_model(model, lora_config)
        # PEFT may leave adapter weights in the base dtype (bf16/fp16). Trainer AMP
        # unscales fp16 grads and raises "Attempting to unscale FP16 gradients" unless
        # trainable params are fp32 — cast adapters only, keep frozen base in bf16.
        for name, param in model.named_parameters():
            if param.requires_grad:
                param.data = param.data.to(torch.float32)
        model.print_trainable_parameters()
        try:
            trainable, total = model.get_nb_trainable_parameters()
        except Exception:  # noqa: BLE001
            trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
            total = sum(p.numel() for p in model.parameters())
        mlflow.log_metrics(
            {
                "trainable_params": float(trainable),
                "total_params": float(total),
                **memory_snapshot(),
            }
        )

        texts = [format_qa_example(r) for r in records]
        ds = Dataset.from_dict({"text": texts})

        def tokenize(batch):
            return tokenizer(
                batch["text"], truncation=True, max_length=512, padding="max_length"
            )

        with mlflow.start_span(name="tokenize"):
            tokenized = ds.map(tokenize, batched=True, remove_columns=ds.column_names)

        use_bf16 = bool(use_cuda and torch.cuda.is_bf16_supported())
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=ft["epochs"],
            per_device_train_batch_size=ft["batch_size"],
            learning_rate=ft["learning_rate"],
            logging_steps=5,
            save_strategy="epoch",
            report_to="mlflow",
            # Prefer bf16 AMP on modern NVIDIA; avoid fp16 GradScaler path that breaks LoRA.
            fp16=False,
            bf16=use_bf16,
            # With batch_size=1, accumulate 4 steps → effective batch 4 without the VRAM hit.
            gradient_accumulation_steps=4,
            overwrite_output_dir=True,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized,
            data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
        )

        logger.info("Starting LoRA fine-tuning on %s...", hardware.device.upper())
        with mlflow.start_span(name="train"):
            result = trainer.train()

        adapter_path = os.path.join(output_dir, "adapter")
        with mlflow.start_span(name="save_model"):
            trainer.save_model(adapter_path)
            tokenizer.save_pretrained(adapter_path)

        train_metrics = {
            k: float(v) for k, v in result.metrics.items() if isinstance(v, (int, float))
        }
        if "train_runtime" in train_metrics:
            mlflow.log_metric("train_runtime", train_metrics["train_runtime"])
        mlflow.log_metrics(train_metrics)

        # Persist a small hardware + train metrics sidecar for later comparison
        sidecar = {
            "hardware": hardware.as_params(),
            "train_metrics": train_metrics,
            "n_train": len(records),
            "base_model": base_model,
            "trainable_params": int(trainable),
            "total_params": int(total),
            "lora_r": ft.get("lora_r", 8),
        }
        with open(os.path.join(adapter_path, "train_info.json"), "w", encoding="utf-8") as f:
            json.dump(sidecar, f, indent=2)

        logger.info("Fine-tuned adapter saved to %s", adapter_path)

    # Separate registry run — must not nest under the Trainer parent run
    try:
        from src.model_registry import register_lora_adapter, registered_model_name

        version = register_lora_adapter(
            adapter_path=adapter_path,
            base_model_id=base_model,
            train_metrics=sidecar["train_metrics"],
            hardware_params=hardware.as_params(),
            registered_name=registered_model_name(config),
            extra_tags={
                "device": hardware.device,
                "n_train": str(len(records)),
                "lora_r": str(ft.get("lora_r", 8)),
                "trainable_params": str(int(trainable)),
            },
        )
        sidecar["registered_model"] = registered_model_name(config)
        sidecar["registered_version"] = version
        with open(os.path.join(adapter_path, "train_info.json"), "w", encoding="utf-8") as f:
            json.dump(sidecar, f, indent=2)
        logger.info(
            "Model Registry: %s v%s (open MLflow → Model Training → Models)",
            sidecar["registered_model"],
            version,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Model Registry registration failed (adapter still on disk): %s", exc)

    logger.info("Set llm.fine_tuned_path to that path before step 6 (auto-detected if default).")


if __name__ == "__main__":
    main()
