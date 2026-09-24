<a href="https://fahadshaikh.net">
  <img src="assets/header.svg" width="100%" alt="Fahad Nafees. Electrical and Computer Engineering, University of Toronto. 3D vision, point clouds, perception, AI agents, signal processing.">
</a>

<p align="center">
  <a href="https://fahadshaikh.net"><img src="https://img.shields.io/badge/website-fahadshaikh.net-5EEAD4?style=for-the-badge&labelColor=0A0E16" alt="Website"></a>
  <a href="https://www.linkedin.com/in/fahad-nafees-b73517248"><img src="https://img.shields.io/badge/linkedin-connect-38BDF8?style=for-the-badge&labelColor=0A0E16" alt="LinkedIn"></a>
  <a href="mailto:fahadnafeessheikh@gmail.com"><img src="https://img.shields.io/badge/email-say%20hi-A78BFA?style=for-the-badge&labelColor=0A0E16" alt="Email"></a>
  <img src="https://komarev.com/ghpvc/?username=FahadNafeesAhmed&label=profile%20views&color=F472B6&style=for-the-badge&labelColor=0A0E16" alt="Profile views">
</p>

<img src="assets/about.svg" width="100%" alt="whoami: Fahad Nafees, Electrical and Computer Engineering at the University of Toronto. Focus: 3D vision, point clouds, signal processing, AI agents, FPGA and digital hardware. Motto: I like to build.">

<img src="assets/experience.svg" width="100%" alt="Experience: UTAT aerospace team (2025), aUToronto self-driving team computer vision (2025 to now), AKW Consultants ML research intern (early 2026), Aortem AI/ML engineer intern (2026 to now).">

## Featured builds

<p align="center">
  <a href="https://github.com/FahadNafeesAhmed/adaptive-neural-facial-deformer"><img src="assets/cards/deformer.svg" width="49%" alt="Neural Facial Deformer: raw 3D face scans to 53 blendshapes and a USD rig. 0.76 mm error, 5.7x more accurate and 17x faster than ICP."></a>
  <a href="https://github.com/FahadNafeesAhmed/periscope"><img src="assets/cards/periscope.svg" width="49%" alt="Periscope: competitor intelligence on Steel cloud browsers. Found 63 of 65 hidden facts versus 22 for a frontier model with fetch."></a>
  <a href="https://github.com/FahadNafeesAhmed/Crucible"><img src="assets/cards/crucible.svg" width="49%" alt="Crucible: a self-improving fake-review detector built from three Gemini agents and Arize Phoenix."></a>
  <a href="https://github.com/FahadNafeesAhmed/redcell"><img src="assets/cards/redcell.svg" width="49%" alt="Redcell: turns risky code paths in a Python repo into verified CTF challenges."></a>
  <a href="https://github.com/FahadNafeesAhmed/-FIAB-Failure-Injection-Agent-Benchmark-"><img src="assets/cards/fiab.svg" width="49%" alt="FIAB: a benchmark for LLM fault diagnosis on a simulated 8-GPU node."></a>
  <a href="https://github.com/FahadNafeesAhmed/sentinel-kyc-research"><img src="assets/cards/sentinel.svg" width="49%" alt="Sentinel KYC: multi-modal liveness and anti-spoofing research."></a>
</p>

<details>
<summary><b>How Crucible teaches itself</b></summary>
<br>

```mermaid
flowchart LR
    F["Forger · Gemini"] -->|adversarial fakes| D["Detector · Gemini"]
    B[("Ott benchmark · 1,600 reviews")] --> D
    D -->|every call traced| P[("Arize Phoenix · traces + rules")]
    P -->|failure traces over MCP| R["Reflector · Google ADK"]
    R -->|one new rule| P
    P -.->|rules read before every verdict| D
```

</details>

## Inside the flagship

<img src="assets/pipeline.svg" width="100%" alt="Pipeline: raw scan, patchify with farthest-point sampling and k-NN, a 6-layer point transformer, prediction heads for 53 weights, pose and identity, GPU non-rigid ICP refinement, and an OpenUSD rig.">

<img src="assets/benchmark.svg" width="100%" alt="Benchmark on 256 noisy scans. Surface error: hybrid 0.76 mm, neural 1.32 mm, ICP with true pose 1.08 mm, tuned ICP 4.35 mm. Time per scan: neural 1.9 ms, hybrid 75.8 ms, ICP with true pose 296 ms, tuned ICP 1,298 ms.">

## Stack

<img src="assets/stack.svg" width="100%" alt="Stack. Languages: Python, TypeScript, JavaScript, C++, C, Dart, Bash, MATLAB. ML and vision: PyTorch, CUDA, OpenCV, NumPy, SciPy, MediaPipe, YOLO, Hugging Face, Jupyter, Blender, OpenUSD. Agents: Claude, Gemini, MCP, Playwright, Pydantic, Google ADK. Web: React, Next.js, Node.js, Tailwind, Vite, Astro, Flutter, FastAPI, Flask, Streamlit. Infra: Docker, Google Cloud, Vercel, Firebase, Cloudflare, SQLite, PostgreSQL, Qdrant, Prometheus, GitHub Actions, Git, uv, pnpm, pytest. Hardware: Verilog, Quartus, DE1-SoC FPGA, LTspice, SolidWorks.">

## Activity

<p align="center">
  <img src="assets/generated/stats.svg" width="49%" alt="Contributions, streaks and active days over the last 12 months">
  <img src="assets/generated/languages.svg" width="49%" alt="Languages across my projects">
</p>

<img src="assets/generated/activity.svg" width="100%" alt="Contribution skyline for the last year">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/FahadNafeesAhmed/FahadNafeesAhmed/output/snake-dark.svg">
  <img src="https://raw.githubusercontent.com/FahadNafeesAhmed/FahadNafeesAhmed/output/snake.svg" width="100%" alt="A snake eating my contribution graph">
</picture>

## More builds

| Project | What it does | Built with |
|---|---|---|
| [NeuralPilot](https://github.com/FahadNafeesAhmed/NeuralPilot) | Computer-use agent: Gemini plans each step, LocateAnything-3B finds the exact pixel to click | Python · Gemini · PyAutoGUI |
| [Aran](https://github.com/FahadNafeesAhmed/waltwise) | Drop in a transformer datasheet PDF, get an NEC 450.3 audit and a live wiring schematic | Next.js · Claude · React Flow |
| [Pain-point miner](https://github.com/FahadNafeesAhmed/redditextractor) | Evidence-first research: a problem counts only after 3 authors in 2 threads report it | Python · local LLM |
| [Coin Catcher](https://github.com/FahadNafeesAhmed/fintech-budget-splitter) | Full-stack Dart game and budget splitter on DartStream, with a [live demo](https://sample-app-fahad-ahmed.web.app) | Dart · Flutter · Firebase |
| [SmartHedge](https://github.com/FahadNafeesAhmed/smarthedge-app) | Hedge calculator and basis monitor for refined oil products | React · Vite |
| [HotoDog Detection](https://github.com/FahadNafeesAhmed/HotoDog-Detection) | Hot dog / not hot dog, done properly: a YOLO detector trained end to end | PyTorch · Ultralytics · OpenCV |

<a href="https://fahadshaikh.net"><img src="assets/footer.svg" width="100%" alt="Thanks for stopping by."></a>

<sub>Stats and the skyline refresh daily through GitHub Actions ([`scripts/build_stats.py`](scripts/build_stats.py)).</sub>
