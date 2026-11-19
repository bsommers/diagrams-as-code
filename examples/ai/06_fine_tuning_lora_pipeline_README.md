# Foundation Model LoRA Fine-Tuning Pipeline

![Architecture Diagram](./06_fine_tuning_lora_pipeline.svg)

## Bill of Materials

| Symbol / ID | Label | Kind | Group | Technical Notes / Metadata |
| :--- | :--- | :--- | :--- | :--- |
| `base_model` | **Base Llama-3 70B Weights** | box | Input Artifacts | precision: FP16 Baseline |
| `dataset` | **Curated Instruction Corpus** | box | Input Artifacts | samples: 50,000 Verified Q&A |
| `lora_trainer` | **LoRA PEFT Trainer** | box | Training Compute | rank: r=64, alpha=128 |
| `adapter` | **LoRA Adapter Checkpoint** | box | Trained Artifacts | size: 320MB SafeTensors |
| `quantizer` | **AWQ / GGUF Quantizer** | box | Packaging Tier | target: 4-bit AWQ / Q4_K_M |
| `registry` | **Hugging Face Model Registry** | box | Packaging Tier | status: Production Release |

## Connections

| Source | Target | Protocol / Label | Style | Routing |
| :--- | :--- | :--- | :--- | :--- |
| **Base Llama-3 70B Weights** (`base_model`) | **LoRA PEFT Trainer** (`lora_trainer`) | Load Frozen Weights | solid | orthogonal |
| **Curated Instruction Corpus** (`dataset`) | **LoRA PEFT Trainer** (`lora_trainer`) | Instruction Tuning Batch | solid | orthogonal |
| **LoRA PEFT Trainer** (`lora_trainer`) | **LoRA Adapter Checkpoint** (`adapter`) | Export Delta Weights | solid | orthogonal |
| **LoRA Adapter Checkpoint** (`adapter`) | **AWQ / GGUF Quantizer** (`quantizer`) | Fuse & Quantize | solid | orthogonal |
| **AWQ / GGUF Quantizer** (`quantizer`) | **Hugging Face Model Registry** (`registry`) | Register Model Package | solid | orthogonal |
