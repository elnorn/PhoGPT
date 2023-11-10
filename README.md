- [Introduction](#introduction)
- [Evaluation](#evaluation)
- [Model download](#download)
- [Run the model](#inference)
- [Fine-tuning the model](#finetuning)
- [Limitations](#limitations)
- [License](https://github.com/VinAIResearch/PhoGPT/blob/main/LICENSE)

# PhoGPT: Generative Pre-training for Vietnamese 

We open-source a state-of-the-art 7.5B-parameter generative model series named PhoGPT for Vietnamese, which includes the base pre-trained monolingual model **PhoGPT-7B5** and its instruction-following variant **PhoGPT-7B5-Instruct**. More details about the general architecture and experimental results of PhoGPT can be found in our [technical report](https://arxiv.org/abs/2311.02945):

```
@article{PhoGPT,
title     = {{PhoGPT: Generative Pre-training for Vietnamese}},
author    = {Dat Quoc Nguyen and Linh The Nguyen and Chi Tran and Dung Ngoc Nguyen and Nhung Nguyen and Thien Huu Nguyen and Dinh Phung and Hung Bui},
journal   = {arXiv preprint},
volume    = {arXiv:2311.02945},
year      = {2023}
}
```

## Introduction <a name="introduction"></a>

PhoGPT is a [Transformer](https://arxiv.org/abs/1706.03762) decoder-based model,  which incorporates (Triton) [flash attention](https://github.com/Dao-AILab/flash-attention) and [ALiBi](https://arxiv.org/abs/2108.12409) for context length extrapolation. Utilizing the [Mosaicml llm-foundry library](https://github.com/mosaicml/llm-foundry), we pre-train PhoGPT from scratch on a 41GB pre-training corpus of Vietnamese texts. This pre-training corpus consists of 1GB of Wikipedia texts and a 40GB deduplicated variant of the ["binhvq" news dataset](https://github.com/binhvq/news-corpus)  (version 21/05/2021).

We fine-tune the pre-trained PhoGPT for instruction following, using a dataset consisting of 150K Vietnamese prompt and response pairs. This dataset is constructed by concatenating the following sources: (i) 67K pairs from the Vietnamese subset of [Bactrian-X](https://huggingface.co/datasets/MBZUAI/Bactrian-X); (ii) 40K [ShareGPT](https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/resolve/main/ShareGPT_V3_unfiltered_cleaned_split_no_imsorry.json) pairs without code and math, translated from English to Vietnamese by using [VinAI Translate](https://github.com/VinAIResearch/VinAI_Translate); (iii) 40K prompts covering hate, offense, toxicity, and safety awareness, largely including Vietnamese-translated ones; and (iv) 1000 pairs for context-based question answering, 500 for poem writing, 500 for essay writing, 500 for spelling correction, and 500 for single-document summarization.

## Evaluation <a name="evaluation"></a>

We conduct a human evaluation experiment to compare PhoGPT-7B5-Instruct with the closed-source ChatGPT (gpt-3.5-turbo) and other open-source instruction-following models, including Vietcuna-3B, [Vietcuna](https://www.vilm.org/research/how-did-we-train-vietcuna)-7B-v3, [URA-LLaMa](https://huggingface.co/ura-hcmut/ura-llama-7b)-7B and URA-LLaMa-13B. The [Vicuna question benchmark](https://github.com/lm-sys/FastChat/blob/main/fastchat/llm_judge/data/vicuna_bench/question.jsonl) is manually translated into Vietnamese to create 80 evaluation questions from 8 different categories.  Each question is fed into the 6 experimental models to generate responses, which are then anonymously shuffled. In this experiment, we utilize the greedy search decoding method, which is [more suitable for LLM comparison](https://aclanthology.org/2023.nlp4convai-1.5.pdf). Each generated response is then independently  assessed by 3 annotators on a scale from 1 - Bad (e.g. wrong answers), 2 - Poor (e.g. partially answering the question), 3 - Fair, 4 - Good, to 5 - Excellent. We host  a discussion session with the annotators to resolve annotation conflicts.

<img width="1000" alt="Human evaluation results on the Vietnamese-translated Vicuna instructions" src="https://github.com/VinAIResearch/PhoGPT/assets/2412555/a81be09b-4edc-49bc-af56-28c4d9aa8f43">

As shown in the result figure above, our PhoGPT-7B5-Instruct is strongly competitive compared to ChatGPT for "generic", "knowledge", "common-sense", and "writing" questions. Notably, PhoGPT-7B5-Instruct substantially outperforms previous open-source instruction-following baselines for Vietnamese, except in the "coding & math" category where Vietcuna-7B-v3 and URA-LLaMa-13B perform better than PhoGPT-7B5-Instruct. Furthermore, in the "femi" category, all open-source models perform badly. For PhoGPT-7B5-Instruct, these results are anticipated due to the lack of "coding & math" and "femi"-type data in our pre-training Vietnamese corpus. Note that some "good" responses from Vietcuna-7B-v3 and URA-LLaMa-13B for "coding & math" questions share identical text with those from ChatGPT. This suggests that these question-response pairs may coincidentally appear in the instruction-following datasets used for fine-tuning Vietcuna and URA-LLaMa. All generated responses are available  [`HERE`](https://docs.google.com/spreadsheets/d/122ldeXuBmLSFFqaFbflj82VyYTKL-Qc2hZiTI9csc-Q/edit?usp=sharing) for readers' self-evaluation.

## Model download <a name="download"></a>

Model | Download 
---|---
`vinai/PhoGPT-7B5` | https://huggingface.co/vinai/PhoGPT-7B5
`vinai/PhoGPT-7B5-Instruct` | https://huggingface.co/vinai/PhoGPT-7B5-Instruct


## Run the model <a name="inference"></a>

### with `transformers`

```python
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer  
  
model_path = "vinai/PhoGPT-7B5-Instruct"  
  
config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)  
config.init_device = "cuda"
# config.attn_config['attn_impl'] = 'triton' # Enable if "triton" installed!
  
model = AutoModelForCausalLM.from_pretrained(  
    model_path, config=config, torch_dtype=torch.bfloat16, trust_remote_code=True  
)
# If your GPU does not support bfloat16:
# model = AutoModelForCausalLM.from_pretrained(model_path, config=config, torch_dtype=torch.float16, trust_remote_code=True)
model.eval()  
  
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)  
  
PROMPT = "### Câu hỏi:\n{instruction}\n\n### Trả lời:"  
  
input_prompt = PROMPT.format_map(  
    {"instruction": "Làm thế nào để cải thiện kỹ năng quản lý thời gian?"}  
)  
  
input_ids = tokenizer(input_prompt, return_tensors="pt")  
  
outputs = model.generate(  
    inputs=input_ids["input_ids"].to("cuda"),  
    attention_mask=input_ids["attention_mask"].to("cuda"),  
    do_sample=True,  
    temperature=1.0,  
    top_k=50,  
    top_p=0.9,  
    max_new_tokens=1024,  
    eos_token_id=tokenizer.eos_token_id,  
    pad_token_id=tokenizer.pad_token_id  
)  
  
response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]  
response = response.split("### Trả lời:")[1]
```

