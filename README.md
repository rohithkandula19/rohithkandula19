> **⚠️ All Rights Reserved.** This repository is published for viewing and portfolio purposes only. The code is **not** open source — reuse, redistribution, modification, or derivative works are not permitted without written permission. See [LICENSE](./LICENSE).
<div align="center">

<!-- UNIVERSE MOVING BACKGROUND -->
<img width="100%" src="Git.svg"/>

<!-- TYPING ANIMATION — ALL 6 PROJECTS -->
<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=700&size=17&pause=1200&color=00D9FF&center=true&vCenter=true&width=800&height=60&lines=AI%2FML+Engineer+based+in+Charlotte%2C+NC;Ronin+--+Provider-Agnostic+AI+Coding+Agent+%28Claude-Code-style%2C+MIT%29;RO+MedRAG+--+Agentic+RAG+for+Medical+Literature+on+GCP;BullshiftDetector+--+Claude-powered+LinkedIn+Cringe+Detector;RO+AI+Recommendation+Engine+--+Netflix-style+Two-Tower+ML;ROVA+AI+Forecasting+--+PyTorch+NN+%2B+LSTM+Platform+on+GCP;RO+Fraud+Detection+--+Enterprise+LangGraph+AI+on+AWS;MR+Buses+--+AI-Powered+Bus+Booking+Platform+on+GCP;Open+to+AI+Engineer+%7C+GenAI+%7C+LLM+%7C+MLOps+Roles" alt="Typing SVG" />

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/rohith-kandula19/)
[![Ronin](https://img.shields.io/badge/Ronin-Open_Source_Agent-7b2fff?style=for-the-badge&logo=github&logoColor=white)](https://github.com/rohithkandula19/Ronin)
[![RO MedRAG](https://img.shields.io/badge/RO_MedRAG-Live-00D9FF?style=for-the-badge&logo=googlechrome&logoColor=white)](https://romedrag.me)
[![BullshiftDetector](https://img.shields.io/badge/BullshiftDetector-Live-FF4444?style=for-the-badge&logo=googlechrome&logoColor=white)](https://bullshiftdetector.web.app)
[![MR Buses](https://img.shields.io/badge/MR_Buses-Live-00FF88?style=for-the-badge&logo=googlechrome&logoColor=white)](https://mrbusportal.com)
[![Fraud Detection](https://img.shields.io/badge/RO_Fraud_Detection-Live-FFD700?style=for-the-badge&logo=googlechrome&logoColor=black)](https://rover-ai.duckdns.org)
[![Open To Work](https://img.shields.io/badge/Open_To_Work-AI_Engineer-7b2fff?style=for-the-badge&logo=checkmarx&logoColor=white)](#)
[![Ask My AI](https://img.shields.io/badge/🤖_Ask_My_AI-the_site_talks_back-FF6B9D?style=for-the-badge)](https://www.rohithkandula.com)

<br/>


</div>

---

<div align="center"><h2>🌌 WHO AM I</h2></div>

I'm an AI/ML Engineer who gets a kick out of taking ideas from zero to production. Not the kind who fine-tunes a model in a notebook and calls it a day -- I mean actually shipping things: APIs, cloud deployments, real users, real data.

I've spent the last 4+ years obsessing over the full stack of AI -- from training PyTorch models and building RAG pipelines to wiring up Kafka event streams and deploying on GCP and AWS. If it involves LLMs, agents, or real-time ML, I've probably broken it three times and shipped it on the fourth.

Right now I'm building toward roles at companies that actually push the frontier -- Anthropic, OpenAI, Google DeepMind. Not because of the hype, but because I genuinely care about where this technology goes.

```python
rohith = {
    "location"  : "Charlotte, NC",
    "education" : "MS Information Technology -- University of Cincinnati (GPA: 3.89)",
    "cert"      : "AWS Solutions Architect Associate",
    "currently" : "Building production AI systems. Shipping. Repeating.",
    "targeting" : ["Anthropic", "OpenAI", "Google DeepMind", "Meta AI"],
    "status"    : "Open to AI Engineer | GenAI | LLM | MLOps -- US",
}
```

---

<div align="center"><h2>🗡️ OPEN SOURCE — RONIN</h2></div>

### [Ronin — a masterless, provider-agnostic AI coding agent](https://github.com/rohithkandula19/Ronin)

[![GitHub](https://img.shields.io/badge/GitHub-Ronin-181717?style=flat-square&logo=github)](https://github.com/rohithkandula19/Ronin)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)
![Tests](https://img.shields.io/badge/tests-1%2C376_passing-brightgreen?style=flat-square)
![Runs on](https://img.shields.io/badge/runs_on-Claude_or_free_models-d4a373?style=flat-square)

A Claude-Code-style terminal agent that reads, edits, and runs your code -- every write behind a diff you approve. Built on a **provider-agnostic** framework, so the same agent runs on Claude for top quality or **free** on Gemini / Cerebras / Groq / Ollama (`--offline` strips every network tool for air-gapped coding). The multi-provider design unlocks things a single-vendor agent structurally can't:

- **Consensus** -- run a task across several models in parallel; a judge synthesizes one cross-checked answer
- **Dojo** -- rival models each attempt the same change in isolated git worktrees; a judge picks the best diff
- **Kaizen** -- the agent finds a weakness in its *own* source, fixes it in a worktree, and keeps the diff only if the test suite passes

```
Python  ->  7-package monorepo  ->  1,376 offline tests  ->  MCP + 200 plugins
```

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_API-D97757?style=flat-square&logo=anthropic&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-1C3C3C?style=flat-square)

---

<div align="center">
<h2>🚀 THINGS I'VE BUILT AND SHIPPED</h2>
<p><i>6 production systems. All live. All mine.</i></p>
</div>

<table>
<tr>
<td width="50%" valign="top">

### 🧠 [RO MedRAG](https://romedrag.me)
[![Live](https://img.shields.io/badge/LIVE-romedrag.me-00D9FF?style=flat-square)](https://romedrag.me)

Medical research is buried in millions of papers. I built an agentic RAG system that searches PubMed in real-time, pulls the right papers, and synthesizes clinical answers using Claude Sonnet -- all streamed live to the user.

```
LangGraph -> FAISS -> PubMed API -> Claude Sonnet
FastAPI -> GCP Cloud Run -> PostgreSQL -> SSE
```
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square)
![FAISS](https://img.shields.io/badge/FAISS-00599C?style=flat-square)
![GCP](https://img.shields.io/badge/GCP-4285F4?style=flat-square&logo=googlecloud&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_API-D97757?style=flat-square)

</td>
<td width="50%" valign="top">

### 🎯 [RO AI Recommendation Engine](https://github.com/rohithkandula19/ro-ai-recommendation-engine)
[![Repo](https://img.shields.io/badge/GitHub-Repo-181717?style=flat-square&logo=github)](https://github.com/rohithkandula19/ro-ai-recommendation-engine)

I got curious about how Netflix actually works under the hood -- so I built it. A proper two-tower PyTorch model with BPR loss, 4-source candidate generation, LightGBM reranking, and a Kafka event pipeline on Kubernetes.

```
PyTorch BPR -> FAISS IVFPQ -> LightGBM LTR -> MMR
Kafka -> ClickHouse -> Kubernetes HPA -> Terraform EKS
```
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![Kafka](https://img.shields.io/badge/Kafka-231F20?style=flat-square&logo=apachekafka&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white)

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 💩 [BullshiftDetector](https://bullshiftdetector.web.app)
[![Live](https://img.shields.io/badge/LIVE-bullshiftdetector.web.app-FF4444?style=flat-square)](https://bullshiftdetector.web.app)

I got tired of seeing "Humbled and excited to announce" for the 50th time. So I built a Claude-powered detector that scores LinkedIn posts for corporate cringe (0-100), generates a one-line roast, and rewrites it like a normal human. Because someone had to.

```
Claude API -> FastAPI -> Next.js 14
GCP Cloud Run -> Firebase Hosting
```
![Claude](https://img.shields.io/badge/Claude_API-D97757?style=flat-square)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat-square&logo=firebase&logoColor=black)

</td>
<td width="50%" valign="top">

### 📊 [ROVA AI Forecasting](https://github.com/rohithkandula19/rova-ai-forecasting)
[![Repo](https://img.shields.io/badge/GitHub-Repo-181717?style=flat-square&logo=github)](https://github.com/rohithkandula19/rova-ai-forecasting)

A full ML forecasting platform with a proper pipeline -- PyTorch NN + LSTM ensemble, 128-dimensional feature engineering, SHAP attributions for explainability, and KL-divergence drift detection that auto-retrains when the distribution shifts. 14 screens on GCP.

```
PyTorch NN + LSTM -> MLflow -> Celery + Redis
Prometheus + Grafana -> GCP Cloud Run
```
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=flat-square&logo=mlflow&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana&logoColor=white)

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🔍 [RO Fraud Detection](https://rover-ai.duckdns.org)
[![Live](https://img.shields.io/badge/LIVE-rover--ai.duckdns.org-00FF88?style=flat-square)](https://rover-ai.duckdns.org)

Enterprise fraud detection with LangGraph agents doing the heavy lifting -- real-time risk scoring, multi-step reasoning on each transaction, full audit trail on every decision. Deployed on AWS EC2 with Nginx and SSL. Actually production-grade.

```
LangGraph Agents -> FastAPI -> SQLAlchemy
AWS EC2 -> Docker -> Nginx -> Let's Encrypt
```
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonaws&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

</td>
<td width="50%" valign="top">

### 🚌 [MR Buses](https://mrbusportal.com)
[![Live](https://img.shields.io/badge/LIVE-mrbusportal.com-00D9FF?style=flat-square)](https://mrbusportal.com)

A full interstate bus booking platform with an AI chatbot that actually knows the routes, schedules, and can help you book -- not just answer FAQs. Google OAuth, real-time seat booking, admin dashboard. Live on GCP.

```
LangChain RAG -> FastAPI -> GCP Cloud Run
Cloud SQL PostgreSQL -> Firebase Hosting
```
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square)
![GCP](https://img.shields.io/badge/GCP-4285F4?style=flat-square&logo=googlecloud&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)

</td>
</tr>
</table>

---

<div align="center"><h2>🛰️ LIVE STATUS</h2>
<p><i>"All live" isn't a slogan — a GitHub Action pings every deployment and rewrites this table. Receipts, not vibes.</i></p></div>

<div align="center">

<!-- STATUS:START -->
| System | Status | Response |
|---|---|---|
| [RO MedRAG](https://romedrag.me) | 🟢 LIVE | 118 ms |
| [BullshiftDetector](https://bullshiftdetector.web.app) | 🟢 LIVE | 187 ms |
| [MR Buses](https://mrbusportal.com) | 🟢 LIVE | 124 ms |
| [RO Fraud Detection](https://rover-ai.duckdns.org) | 🟡 SLOW | 3746 ms |

<sub>🤖 Checked automatically every 6 hours by GitHub Actions — last run 2026-06-10 16:42 UTC</sub>
<!-- STATUS:END -->

</div>

<div align="center"><h3>⚡ Recently shipped</h3></div>

<!-- SHIPPED:START -->
- **[Ronin](https://github.com/rohithkandula19/Ronin)** · pushed 2026-06-10 — Masterless, terminal-native coding agent (Claude Code-style: reads, edits, runs code) f…
- **[Ro-MedRag](https://github.com/rohithkandula19/Ro-MedRag)** · pushed 2026-06-10 — Production agentic RAG system for medical literature analysis. LangGraph + Claude Sonne…
- **[ro-ai-recommendation-engine](https://github.com/rohithkandula19/ro-ai-recommendation-engine)** · pushed 2026-06-04
- **[mr-bus-portal](https://github.com/rohithkandula19/mr-bus-portal)** · pushed 2026-06-04
- **[Ro-Cortex](https://github.com/rohithkandula19/Ro-Cortex)** · pushed 2026-06-04
<!-- SHIPPED:END -->

---

<div align="center"><h2>🛠️ STACK</h2></div>

```mermaid
flowchart LR
    subgraph Data["📥 Data & Retrieval"]
        PubMed[PubMed API] --> FAISS[(FAISS / BM25)]
        Docs[Docs & Events] --> Kafka[Kafka] --> CH[(ClickHouse)]
    end
    subgraph Brain["🧠 Agents & Models"]
        FAISS --> LG[LangGraph Agents]
        LG <--> Claude[Claude API]
        PT[PyTorch Two-Tower / LSTM] --> LGB[LightGBM Rerank]
    end
    subgraph Serve["🚀 Serving"]
        LG --> API[FastAPI + SSE]
        LGB --> API
        API --> UI[Next.js / React]
    end
    subgraph Ops["☁️ Cloud & MLOps"]
        API --> Run[GCP Cloud Run / AWS EC2]
        Run --> K8s[Kubernetes + Terraform]
        K8s --> Obs[MLflow · Prometheus · Grafana]
    end
```

<div align="center">

**AI / ML**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_API-D97757?style=for-the-badge&logo=anthropic&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)

**Backend / Data**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Kafka](https://img.shields.io/badge/Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6B35?style=for-the-badge)

**Cloud / MLOps**

![GCP](https://img.shields.io/badge/GCP-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)

**Frontend**

![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Tailwind](https://img.shields.io/badge/Tailwind-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

</div>

---

<div align="center"><h2>📊 GITHUB STATS</h2></div>

<div align="center">

<img height="180em" src="https://github-readme-stats.vercel.app/api?username=rohithkandula19&show_icons=true&theme=tokyonight&include_all_commits=true&count_private=true&hide_border=true&bg_color=0D1117&title_color=7b2fff&icon_color=00D9FF&text_color=FFFFFF"/>
<img height="180em" src="https://github-readme-stats.vercel.app/api/top-langs/?username=rohithkandula19&layout=compact&theme=tokyonight&hide_border=true&bg_color=0D1117&title_color=7b2fff&text_color=FFFFFF&langs_count=8"/>

<img src="https://github-readme-streak-stats.herokuapp.com/?user=rohithkandula19&theme=tokyonight&hide_border=true&background=0D1117&ring=7b2fff&fire=00D9FF&currStreakLabel=7b2fff&sideLabels=FFFFFF&dates=AAAAAA"/>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=rohithkandula19&theme=tokyo-night&bg_color=0D1117&color=7b2fff&line=00D9FF&point=c8a2ff&area=true&hide_border=true" width="100%"/>

<img src="profile-3d-contrib/profile-night-rainbow.svg" width="100%" alt="3D contribution graph — regenerated daily by GitHub Actions"/>

</div>

---

<div align="center"><h2>🕹️ THE ARCADE</h2>
<p><i>This profile is playable. Yes, really.</i></p></div>

<!-- CHESS:START -->
<div align="center">

**♟️ Play chess against my profile.** You (the internet) are **White**; a Stockfish bot is **Black**.
Click a move → a pre-filled GitHub issue opens → press *Create* → a GitHub Action plays it, gets Stockfish's reply, and re-renders this board.

<img src="games/chess/board.svg" width="420" alt="chess board"/>



**Your move:** [`Ba6`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CBa6&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Bb5`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CBb5&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Bc4`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CBc4&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Bd3`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CBd3&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Be2`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CBe2&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Ke2`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CKe2&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Na3`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CNa3&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Nc3`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CNc3&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Ne2`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CNe2&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Nf3`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CNf3&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Nh3`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CNh3&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Qe2`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CQe2&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Qf3`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CQf3&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Qg4`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CQg4&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`Qh5`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7CQh5&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`a3`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7Ca3&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`a4`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7Ca4&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`b3`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7Cb3&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`b4`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7Cb4&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`c3`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7Cc3&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`c4`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7Cc4&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`d3`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7Cd3&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`d4`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7Cd4&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.) · [`e5`](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cmove%7Ce5&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.)

<details><summary>Recent moves</summary>

<sub>⚪ e4 — @rohithkandula19</sub>  
<sub>⚫ Nf6 — Stockfish</sub>

</details>

<sub>Any legal move works: open an issue titled <code>chess|move|&lt;SAN&gt;</code> (e.g. <code>chess|move|Nf3</code>) · [Start a new game](https://github.com/rohithkandula19/rohithkandula19/issues/new?title=chess%7Cnew&body=Just%20press%20%27Create%27%20%E2%80%94%20the%20bot%20does%20the%20rest.)</sub>

</div>
<!-- CHESS:END -->

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="dist/pacman-contribution-graph-dark.svg">
  <img src="dist/pacman-contribution-graph.svg" width="100%" alt="Pac-Man eating my contribution graph — regenerated daily"/>
</picture>

<img src="dist/monkey-jungle.svg" width="100%" alt="The contribution jungle — bananas grow where the commits are, and a monkey swings across. Hand-built SVG, regenerated every 6 hours."/>

</div>

---

<div align="center"><h2>🏆 CREDENTIALS</h2></div>

<div align="center">

| Credential | Details |
|---|---|
| [Claude with Google Cloud's Vertex AI](https://verify.skilljar.com/c/6nrrh5xfejxq) | Anthropic Education -- May 2026 |
| [Claude 101](https://verify.skilljar.com/c/jqz4es75zbxm) | Anthropic -- Apr 2026 |
| [AI Fluency: Framework & Foundations](https://verify.skilljar.com/c/2f42572kjdgg) | Anthropic -- Apr 2026 |
| AWS Certified Solutions Architect -- Associate | Amazon Web Services -- May 2025 (exp. May 2028) |
| MS, Information Technology | University of Cincinnati -- GPA 3.89 -- Dec 2024 |
| Deep Learning Specialization | Andrew Ng / DeepLearning.AI -- 2024 |
| LangChain & LLM Agents for Production | DeepLearning.AI -- 2024 |

</div>

---

<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=venom&color=0:000000,50:130533,100:000000&height=150&section=footer&animation=fadeIn"/>

[![LinkedIn](https://img.shields.io/badge/Connect_on_LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/rohith-kandula19)
[![Portfolio](https://img.shields.io/badge/Portfolio-rohithkandula.com-00D9FF?style=for-the-badge&logo=googlechrome&logoColor=white)](https://www.rohithkandula.com)

<sub>🤖 The portfolio has an AI narrator and an "Ask Rohith" chat — and it rewrites itself depending on whether you're a recruiter, an engineer, or just curious. Go say hi.</sub>

</div>