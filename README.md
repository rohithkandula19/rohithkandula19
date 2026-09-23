<div align="center">

<!-- UNIVERSE MOVING BACKGROUND -->
<img width="100%" src="Git.svg"/>

<!-- TYPING ANIMATION · RONIN FIRST -->
<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=700&size=17&pause=1200&color=00D9FF&center=true&vCenter=true&width=800&height=60&lines=Building+Ronin+%C2%B7+a+provider-agnostic+coding+agent;Claude-Code-style+in+the+terminal+%C2%B7+MIT;Consensus+%C2%B7+Dojo+%C2%B7+Kaizen+across+models;Also+ships+production+RAG%2C+agents%2C+and+ML;Charlotte%2C+NC+%C2%B7+AI%2FML+Engineer" alt="Typing SVG" />

<br/>

[![Ronin](https://img.shields.io/badge/Ronin-Open_Source_Agent-7b2fff?style=for-the-badge&logo=github&logoColor=white)](https://github.com/rohithkandula19/Ronin)
[![Star](https://img.shields.io/github/stars/rohithkandula19/Ronin?style=for-the-badge&logo=github&label=Stars)](https://github.com/rohithkandula19/Ronin)
[![Portfolio](https://img.shields.io/badge/Portfolio-rohithkandula.com-00D9FF?style=for-the-badge&logo=googlechrome&logoColor=white)](https://www.rohithkandula.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/rohith-kandula19/)

</div>

---

<div align="center"><h2>🗡️ RONIN</h2>
<p><i>The thing I want you to look at first.</i></p>
</div>

### [A masterless, provider-agnostic AI coding agent](https://github.com/rohithkandula19/Ronin)

[![GitHub](https://img.shields.io/badge/GitHub-Ronin-181717?style=flat-square&logo=github)](https://github.com/rohithkandula19/Ronin)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)
![Tests](https://img.shields.io/badge/tests-1%2C376_passing-brightgreen?style=flat-square)
![Runs on](https://img.shields.io/badge/runs_on-Claude_or_free_models-d4a373?style=flat-square)

Ronin is a Claude-Code-style terminal agent: it reads, edits, and runs your code, and every write sits behind a diff you approve. The stack is **provider-agnostic**, so the same agent runs on Claude when you want quality, or free on Gemini / Cerebras / Groq / Ollama. `--offline` strips every network tool for air-gapped work.

Multi-provider is the point, not a toggle:

- **Consensus** — several models run the same task; a judge returns one cross-checked answer
- **Dojo** — rival models each attempt the change in isolated git worktrees; a judge keeps the best diff
- **Kaizen** — the agent finds a weakness in *its own* source, patches it in a worktree, and keeps the diff only if tests pass

```
Python  →  7-package monorepo  →  1,376 offline tests  →  MCP + 200 plugins
```

If you only click one link on this profile: **[star / clone Ronin](https://github.com/rohithkandula19/Ronin)**.

---

<div align="center"><h2>🌌 WHO AM I</h2></div>

AI/ML engineer in Charlotte. I ship agents and production ML — APIs, cloud, real users — not notebook demos.

Most of that energy now goes into **Ronin**. The other systems below are how I learned to put LLM and ML systems on the internet and keep them there.

```python
rohith = {
    "location"  : "Charlotte, NC",
    "education" : "MS Information Technology, University of Cincinnati (GPA: 3.89)",
    "cert"      : "AWS Solutions Architect Associate",
    "currently" : "Building Ronin. Shipping the rest.",
    "status"    : "Open to AI Engineer | GenAI | LLM roles (US)",
}
```

---

<div align="center">
<h2>🚀 ALSO SHIPPED</h2>
<p><i>Live systems. Useful context. Not the main plot.</i></p>
</div>

<table>
<tr>
<td width="50%" valign="top">

### 🧠 [RO MedRAG](https://romedrag.me)
[![Live](https://img.shields.io/badge/LIVE-romedrag.me-00D9FF?style=flat-square)](https://romedrag.me)

Agentic RAG over PubMed. Searches, pulls papers, synthesizes clinical answers with Claude Sonnet, streamed live.

```
LangGraph → FAISS → PubMed → Claude
FastAPI → Cloud Run → PostgreSQL → SSE
```

</td>
<td width="50%" valign="top">

### 🎯 [RO Recommendation Engine](https://github.com/rohithkandula19/ro-ai-recommendation-engine)
[![Repo](https://img.shields.io/badge/GitHub-Repo-181717?style=flat-square&logo=github)](https://github.com/rohithkandula19/ro-ai-recommendation-engine)

Two-tower PyTorch + BPR, candidate generation, LightGBM rerank, Kafka on Kubernetes.

```
PyTorch BPR → FAISS → LightGBM → MMR
Kafka → ClickHouse → EKS
```

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 💩 [BullshiftDetector](https://bullshiftdetector.web.app)
[![Live](https://img.shields.io/badge/LIVE-bullshiftdetector.web.app-FF4444?style=flat-square)](https://bullshiftdetector.web.app)

Scores LinkedIn posts for corporate cringe, roasts them, rewrites them like a human.

```
Claude API → FastAPI → Next.js
Cloud Run → Firebase Hosting
```

</td>
<td width="50%" valign="top">

### 📊 [ROVA Forecasting](https://github.com/rohithkandula19/rova-ai-forecasting)
[![Repo](https://img.shields.io/badge/GitHub-Repo-181717?style=flat-square&logo=github)](https://github.com/rohithkandula19/rova-ai-forecasting)

PyTorch NN + LSTM ensemble, SHAP, drift detection that retrains when the distribution moves.

```
PyTorch + LSTM → MLflow → Celery
Prometheus + Grafana → Cloud Run
```

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🔍 [RO Fraud Detection](https://rover-ai.duckdns.org)
[![Live](https://img.shields.io/badge/LIVE-rover--ai.duckdns.org-00FF88?style=flat-square)](https://rover-ai.duckdns.org)

LangGraph agents for real-time risk scoring and an audit trail on every decision.

```
LangGraph → FastAPI → SQLAlchemy
EC2 → Docker → Nginx
```

</td>
<td width="50%" valign="top">

### 🚌 [MR Buses](https://mrbusportal.com)
[![Live](https://img.shields.io/badge/LIVE-mrbusportal.com-00D9FF?style=flat-square)](https://mrbusportal.com)

Interstate booking plus an AI chatbot that knows routes and can help you book.

```
LangChain RAG → FastAPI → Cloud Run
Cloud SQL → Firebase Hosting
```

</td>
</tr>
</table>

---

<div align="center"><h2>🛰️ LIVE STATUS</h2>
<p><i>A GitHub Action pings the public deployments and rewrites this table.</i></p></div>

<div align="center">

<!-- STATUS:START -->
| System | Status | Response |
|---|---|---|
| [RO MedRAG](https://romedrag.me) | 🔴 DOWN | n/a |
| [BullshiftDetector](https://bullshiftdetector.web.app) | 🟢 LIVE | 122 ms |
| [MR Buses](https://mrbusportal.com) | 🟢 LIVE | 115 ms |
| [RO Fraud Detection](https://rover-ai.duckdns.org) | 🔴 DOWN | n/a |

<sub>🤖 Checked automatically every 6 hours by GitHub Actions · last run 2026-09-23 22:55 UTC</sub>
<!-- STATUS:END -->

</div>

<div align="center"><h3>⚡ Recently shipped</h3></div>

<!-- SHIPPED:START -->
- **[Ronin](https://github.com/rohithkandula19/Ronin)** · pushed 2026-09-22 · Masterless, terminal-native coding agent (Claude Code-style: reads, edits, runs code) f…
- **[RohiRo](https://github.com/rohithkandula19/RohiRo)** · pushed 2026-08-18 · ro · a personal agent operating system.
- **[Ro-Resume-Agent](https://github.com/rohithkandula19/Ro-Resume-Agent)** · pushed 2026-07-05 · AI resume builder + ATS scorer.
- **[.github](https://github.com/rohithkandula19/.github)** · pushed 2026-06-11 · Community health defaults
- **[agentfaceoff](https://github.com/rohithkandula19/agentfaceoff)** · pushed 2026-06-11 · Live LLM battle arena · same prompt to two models, token-by-token split-screen streamin…
<!-- SHIPPED:END -->

---

<div align="center"><h2>🛠️ STACK</h2></div>

```mermaid
flowchart LR
    subgraph Data["📥 Data & Retrieval"]
        Docs[Docs & APIs] --> VS[(FAISS · pgvector · hybrid search)]
        Events[Events] --> Kafka[Kafka] --> CH[(ClickHouse / BigQuery)]
    end
    subgraph Brain["🧠 Agents & Models"]
        VS --> LG[LangGraph / Ronin planner]
        LG <--> Claude[Claude · Gemini · Groq · Ollama]
        PT[PyTorch Two-Tower / LSTM] --> LGB[LightGBM Rerank]
    end
    subgraph Evals["🧪 Evals & Observability"]
        LG --> EV[golden sets · LLM-as-judge]
        EV --> LF[Langfuse: traces · cost · drift]
    end
    subgraph Serve["🚀 Serving & Infra"]
        LG --> API[FastAPI + SSE]
        LGB --> API
        API --> UI[Next.js / React]
        API --> Cloud[GCP · AWS] --> K8s[Kubernetes + Terraform]
    end
```

<div align="center">

**Core**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Claude API](https://img.shields.io/badge/Claude_API-D97757?style=for-the-badge&logo=anthropic&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-000000?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![GCP](https://img.shields.io/badge/GCP-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Next.js 14](https://img.shields.io/badge/Next.js_14-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)

</div>

---

<div align="center"><h2>📊 GITHUB STATS</h2></div>

<div align="center">

<img height="180em" src="https://github-readme-stats.vercel.app/api?username=rohithkandula19&show_icons=true&theme=tokyonight&include_all_commits=true&count_private=true&hide_border=true&bg_color=0D1117&title_color=7b2fff&icon_color=00D9FF&text_color=FFFFFF"/>
<img height="180em" src="https://github-readme-stats.vercel.app/api/top-langs/?username=rohithkandula19&layout=compact&theme=tokyonight&hide_border=true&bg_color=0D1117&title_color=7b2fff&text_color=FFFFFF&langs_count=8"/>

<img src="https://github-readme-streak-stats.herokuapp.com/?user=rohithkandula19&theme=tokyonight&hide_border=true&background=0D1117&ring=7b2fff&fire=00D9FF&currStreakLabel=7b2fff&sideLabels=FFFFFF&dates=AAAAAA"/>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=rohithkandula19&theme=tokyo-night&bg_color=0D1117&color=7b2fff&line=00D9FF&point=c8a2ff&area=true&hide_border=true" width="100%"/>

<img src="profile-3d-contrib/profile-night-rainbow.svg" width="100%" alt="3D contribution graph, regenerated daily by GitHub Actions"/>

</div>

---

<div align="center"><h2>🕹️ THE ARCADE</h2>
<p><i>This profile is playable. Yes, really.</i></p></div>

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="dist/pacman-contribution-graph-dark.svg">
  <img src="dist/pacman-contribution-graph.svg" width="100%" alt="Pac-Man eating my contribution graph, regenerated daily"/>
</picture>

</div>

---

<div align="center"><h2>🏆 CREDENTIALS</h2></div>

<div align="center">

| Credential | Details |
|---|---|
| [Claude with Google Cloud's Vertex AI](https://verify.skilljar.com/c/6nrrh5xfejxq) | Anthropic Education · May 2026 |
| [Claude 101](https://verify.skilljar.com/c/jqz4es75zbxm) | Anthropic · Apr 2026 |
| [AI Fluency: Framework & Foundations](https://verify.skilljar.com/c/2f42572kjdgg) | Anthropic · Apr 2026 |
| AWS Certified Solutions Architect – Associate | Amazon Web Services · May 2025 (exp. May 2028) |
| MS, Information Technology | University of Cincinnati · GPA 3.89 · Dec 2024 |
| Deep Learning Specialization | Andrew Ng / DeepLearning.AI · 2024 |
| LangChain & LLM Agents for Production | DeepLearning.AI · 2024 |

</div>

---

<div align="center">

[![Ronin](https://img.shields.io/badge/Start_with_Ronin-7b2fff?style=for-the-badge&logo=github&logoColor=white)](https://github.com/rohithkandula19/Ronin)
[![LinkedIn](https://img.shields.io/badge/Connect_on_LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/rohith-kandula19)
[![Portfolio](https://img.shields.io/badge/Portfolio-rohithkandula.com-00D9FF?style=for-the-badge&logo=googlechrome&logoColor=white)](https://www.rohithkandula.com)

<sub>Ronin is the open-source line. The portfolio talks back if you want the rest of the story.</sub>

</div>

<sub>⚠️ All rights reserved. Published for viewing and portfolio purposes; reuse or redistribution needs written permission. See <a href="./LICENSE">LICENSE</a>.</sub>
