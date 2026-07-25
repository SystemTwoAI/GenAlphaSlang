<h1 align="center">GenAlphaSlang</h1>

<p align="center">
  <b>Does AI actually understand how kids talk online? A benchmark for Gen Alpha slang comprehension — and what the gaps mean for youth safety.</b>
</p>

<p align="center">
  <a href="https://arxiv.org/abs/2505.10588"><img src="https://img.shields.io/badge/arXiv-2505.10588-b31b1b.svg" alt="arXiv"></a>
  <a href="https://dl.acm.org/doi/10.1145/3715275.3732184"><img src="https://img.shields.io/badge/ACM%20FAccT-2025-0085CA.svg" alt="FAccT 2025"></a>
  <a href="https://systemtwoai.github.io/GenAlphaSlang/"><img src="https://img.shields.io/badge/🎮%20Live%20Quiz-Are%20You%20Cooked%3F-ff2e88.svg" alt="Live Quiz"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPL--3.0-green.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/Status-Active-orange.svg" alt="Status">
</p>

<p align="center">
  <img src="docs/share-card.png" alt="Gen Alpha Slang Check — Are You Cooked?" width="720">
</p>

---

## 🧪 GenAlphaSlang-Bench — *Can frontier models read the room?*

**[📄 Paper](https://arxiv.org/abs/2505.10588)** • **[💻 Model prompt & code](model_evaluation_prompt.md)** • **[⚖️ Judge prompt & code](judge_evaluation_prompt.md)**

A benchmark of **239 Gen Alpha expressions** drawn from gaming, social media, and video platforms, each annotated with a risk category:

| Code | Category | What it captures |
|------|----------|------------------|
| R0 | Neutral | No inherent capacity for harm |
| R1 | Direct Harm | Explicit threats or unambiguous harmful meaning |
| R2 | Masked Negativity | Reads friendly, can cut deep |
| R3 | Evolution-based | Meaning has drifted across generations |
| R4 | Highly Context-Dependent | Genuine or mocking depending on context |
| R5 | Regional/Cultural | Dialect- and community-specific (e.g. AAVE) |

**15 models** — Claude (Opus, Sonnet, Haiku), OpenAI (GPT-4.1, GPT-4o, o3, o4-mini), and Gemini (2.5 Pro/Flash, 2.0 Flash) families — are asked to explain each expression, flag safety concerns, and rate five harm dimensions (violence, targeting of marginalized communities, harassment, grooming, bullying) on a 0–5 scale. A unified **GPT-5.5 judge** scores all 15 responses per expression in a single call for consistent grading.

## 🎮 Gen Alpha Slang Check — *Are You Cooked?*

**[🕹️ Play it live](https://systemtwoai.github.io/GenAlphaSlang/)** • **[💻 Source](docs/index.html)**

The human side of the benchmark: a web quiz that serves **10 random Gen Alpha expressions with 4 plausible meanings each**. Sign in and find out whether you're a *Certified Rizzler* or a *Certified NPC* 💀 — and help us compare human comprehension across demographics against the models.

---

## 📰 News

- **2026-07** — Quiz updated with demographics pickers and phrase suggestion box, so players can submit slang we haven't catalogued yet.
- **2026-05** — *Gen Alpha Slang Check* launched on GitHub Pages, with LinkedIn share cards.
- **2025-06** — Paper presented at **ACM FAccT 2025** in Athens. Coverage in [Fast Company](https://www.fastcompany.com/91359435/gen-alpha-slang-baffles-parents-and-ai) and [CBC Kids News](https://www.cbc.ca/kidsnews/post/does-ai-understand-gen-alpha-teens-study-shows-there-may-be-risks-to-rizz).
- **2025-05** — Benchmark and paper released: [arXiv:2505.10588](https://arxiv.org/abs/2505.10588).

## 🚀 Quick Start

**Try the quiz (no install):** [systemtwoai.github.io/GenAlphaSlang](https://systemtwoai.github.io/GenAlphaSlang/)

**Reproduce the evaluation:**

```bash
git clone https://github.com/SystemTwoAI/GenAlphaSlang.git
cd GenAlphaSlang
pip install pandas openai anthropic google-generativeai

export OPENAI_API_KEY=...   # plus ANTHROPIC_API_KEY / GOOGLE_API_KEY as needed

# 1. Run models over an expression range (see model_evaluation_prompt.md)
python3 scripts/evaluate_all_ranges_openai.py

# 2. Judge all 15 models per expression with GPT-5.5 (see judge_evaluation_prompt.md)
python3 scripts/judge_gpt55_all_models.py 1-100
```

Expression ranges are processed in three batches: `1-100`, `101-181`, `182-239`.

## 📂 Repository Layout

```
├── model_evaluation_prompt.md   # Prompt + scripts for evaluating each model
├── judge_evaluation_prompt.md   # GPT-5.5 unified judge prompt + scripts
├── docs/
│   ├── index.html               # "Are You Cooked?" quiz (GitHub Pages)
│   └── share-card.png           # Social share card
└── LICENSE                      # GPL-3.0
```

## 📖 Citation

```bibtex
@inproceedings{mehta2025genalpha,
  title     = {Understanding Gen Alpha Digital Language: Evaluation of LLM Safety Systems for Content Moderation},
  author    = {Mehta, Manisha and Giunchiglia, Fausto},
  booktitle = {Proceedings of the 2025 ACM Conference on Fairness, Accountability, and Transparency (FAccT '25)},
  year      = {2025},
  doi       = {10.1145/3715275.3732184},
  url       = {https://arxiv.org/abs/2505.10588}
}
```

## 🤝 Get Involved

Spotted slang we're missing? Use the suggestion box in the quiz, open an issue, or reach out at **manisha.mehta@system2ai.com**. We're especially interested in collaborations with researchers, educators, clinicians, and trust & safety teams.

<p align="center"><sub>© 2025–2026 SystemTwoAI • Built to keep AI honest about how young people actually talk.</sub></p>
