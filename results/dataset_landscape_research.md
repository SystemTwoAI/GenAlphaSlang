# Mental Health Therapy Dataset & Benchmark Landscape

**Research Date:** November 2025
**Purpose:** Identify similar datasets, benchmarks, and leaderboards for therapy conversation evaluation

---

## Similar Therapy Conversation Datasets

### 1. **MentalChat16K** (2024-2025)
- **Size:** 16,113 question-answer pairs
- **Composition:**
  - 9.7K GPT-generated counseling conversations
  - 6.3K real-world transcripts from PISCES clinical trial
- **Coverage:** Depression, anxiety, grief, palliative care
- **Availability:** HuggingFace (ShenLab/MentalChat16K)
- **Evaluation:** 200-question benchmark with 7 clinically grounded metrics
- **Models Tested:** Samantha v1.11/v1.2, ChatPsychiatrist, various fine-tuned models
- **Key Finding:** Fine-tuned models consistently outperform baselines

### 2. **CounseLLMe** (January 2025)
- **Size:** 400 simulated mental health counseling dialogues
- **Models Used:** GPT-3.5, Claude-3 Haiku (English), LLaMAntino (Italian)
- **Purpose:** Comparing LLM-generated therapy vs human therapists
- **Key Finding:** LLMs can reproduce conflict/pessimism but lack anger/frustration

### 3. **ConvCounsel** (November 2024)
- **Focus:** Student counseling dialogue system
- **Modality:** Both speech and text data
- **Strategy:** Active listening techniques

### 4. **MDD-5k** (August 2024)
- **Focus:** Mental disorder diagnosis conversations
- **Language:** Chinese
- **Approach:** Synthesized via neuro-symbolic LLM agents
- **Supervision:** Reviewed by professional psychiatrists

### 5. **Amod/mental_health_counseling_conversations** (HuggingFace)
- **Content:** Real counseling Q&A pairs from public mental health platforms
- **Downloads:** 77,000+ (as of Aug 2025)
- **Use Case:** Training empathetic, safety-aware language models

### 6. **Stanford SNAP Counseling Dataset**
- **Type:** Text-message-based counseling conversations
- **URL:** http://snap.stanford.edu/counseling
- **Analysis:** Large-scale quantitative studies on counseling discourse

### 7. **Counsel Chat**
- **Source:** Real therapist-patient Q&A from online platform
- **Quality:** Limited but reasonably high-quality therapist responses

---

## Benchmarks for Therapy AI Evaluation

### **CBT-Bench** (October 2024)
- **Focus:** Cognitive Behavioral Therapy assistance
- **Three-Level Task Structure:**
  - **Level I:** Basic CBT knowledge (multiple choice)
  - **Level II:** Cognitive model understanding
    - Cognitive distortion classification (10 categories)
    - Primary core belief classification
    - Fine-grained core belief classification (19 subtypes)
  - **Level III:** Therapeutic response generation
- **Key Finding:** LLMs excel at knowledge recitation but struggle with cognitive analysis and response generation
- **Availability:** HuggingFace (Psychotherapy-LLM/CBT-Bench)

### **Other Evaluation Benchmarks**
- **BOLT:** Evaluates LLM-generated therapist behaviors in general counseling
- **SimPsyDial:** Benchmarks synthetic data using Working Alliance Inventory
- **PE Therapy Fidelity Framework:** Evaluates Prolonged Exposure therapy conversations

---

## Leaderboard Status

### Key Finding: **No Standardized Public Leaderboard Exists**

Unlike general LLMs (e.g., Chatbot Arena), there is **no unified public leaderboard** for mental health chatbots.

### Why No Leaderboard?
1. **Evaluation is non-standardized** - Most studies use ad-hoc scales
2. **Limited clinical validation** - Only 16% of LLM-based chatbot studies undergo clinical efficacy testing
3. **Transparency concerns** - Heavy reliance on proprietary models limits reproducibility

### Proposed Evaluation Framework
**Three-Tier Validation** (from systematic review):
1. **Foundational bench testing** - Technical validation
2. **Pilot feasibility testing** - User engagement
3. **Clinical efficacy testing** - Symptom reduction

**Current Status:** 77% of studies still in early validation phase

---

## Leading Commercial Mental Health Chatbots

### **Woebot**
- **Evidence:** Remarkable reductions in depression and anxiety
- **Engagement:** High user engagement
- **FDA Status:** Breakthrough Device designation for postpartum depression
- **Clinical Trial:** 2023 RCT showed non-inferiority to clinician-led therapy for teen depression

### **Wysa**
- **Evidence:** Improvements especially for chronic pain and maternal mental health
- **FDA Status:** Breakthrough Device status (2025)

### **Youper**
- **Evidence:** 48% decrease in depression, 43% decrease in anxiety

---

## Model Performance Insights

### MentalChat16K Evaluation Results
- Fine-tuned models outperform baselines on 7 therapeutic metrics
- Human evaluators prefer fine-tuned responses
- GPT-4 Turbo and Gemini Pro used as evaluators

### Mental-LLM Comparison
Models tested: Alpaca, Alpaca-LoRA, FLAN-T5, GPT-3.5, GPT-4

**Key Finding:** Instruction fine-tuning boosts performance significantly
- Mental-Alpaca and Mental-FLAN-T5 outperformed GPT-3.5's best prompt by 10.9% on balanced accuracy

### MentalCLOUDS Summary Benchmark
11 LLMs tested for therapy conversation summarization

**Winners:** MentalLlama and MentalBART consistently outperformed others

---

## Key Evaluation Metrics

### MentalChat16K's 7 Clinical Metrics
1. Empathy and emotional support
2. Active listening and reflection
3. Guidance and psychoeducation
4. Validation and normalization
5. Question asking and exploration
6. Collaborative approach
7. Cultural sensitivity

### ChatThero's 5 Dimensions
1. Responsiveness
2. Empathy
3. Persuasive Strategy Appropriateness
4. Clinical Relevance
5. Behavioral Realism

---

## Market Context

### Growth Trajectory
- **Market Size:** $1.3B (2023) → $2.2B (2033)
- **CAGR:** 5.6%
- **Research Trends:** Studies quadrupled from 14 (2020) to 56 (2024)
- **Architecture Shift:** LLM-based chatbots surged to 45% of new studies in 2024

### Challenges Identified
1. Synthetic dialogues match structural features but miss key fidelity markers
2. Inadequate distress monitoring in synthetic conversations
3. Lack of nuance for high-stakes therapeutic contexts

---

## Relevance to Our GenAlpha Therapy Project

### Alignment Opportunities
1. **MentalChat16K:** We could evaluate our dataset against their 7 clinical metrics
2. **CBT-Bench:** Could assess LLM responses to GenAlpha-converted vs standard conversations
3. **Realism Evaluation:** Our realism analysis framework aligns with emerging standards

### Differentiation
- **Unique angle:** GenAlpha language conversion for therapy evaluation
- **Research gap:** No existing benchmark tests therapy model robustness to informal/slang patient language
- **Potential contribution:** Dataset showing how therapy models handle Gen Z/Gen Alpha communication styles

### Suggested Next Steps
1. Evaluate our benchmark against MentalChat16K's 7 metrics
2. Consider submitting to CBT-Bench for comparative evaluation
3. Propose a "Therapy Robustness to Informal Language" benchmark
4. Collaborate with MentalChat16K or CBT-Bench researchers

---

## Conclusion

While no standardized leaderboard exists, there are active research benchmarks (MentalChat16K, CBT-Bench) that we can align with. Our GenAlpha conversion approach fills a unique gap: evaluating therapy model robustness to modern informal communication styles used by younger patients.

**Recommendation:** Position our work as a **complementary evaluation dimension** focusing on linguistic diversity and youth-focused communication, rather than competing with existing clinical efficacy benchmarks.
