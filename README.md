# CodeNexus: Autonomous Multi-Agent Repository Workspace

CodeNexus is an interactive, visual AI engineering cockpit built to autonomously comprehend, modify, and audit local software repositories. By leveraging a local vector knowledge layer alongside an isolated dual-agent evaluation loop, the system can safely reason over entire codebases, apply precise software fixes, and validate its actions against absolute system constraints.

## 🏗️ System Architecture

The application is built on three core pillars: An ingestion/memory pipeline, a multi-sensory UI cockpit, and an agentic execution handshake layer.

```mermaid
graph TD
    User([User Command]) --> UI[Streamlit UI Dashboard]
    UI --> Ingestion[Local Repository Code Files]
    Ingestion --> Slicer[Regex Structural Code Slicer]
    Slicer --> DB[(ChromaDB Vector Store)]
    
    UI --> Architect[Lead Architect Agent]
    Architect --> Tools{Available Toolset}
    Tools --> |ask_memory| DB
    Tools --> |capture_screen| Vision[PyAutoGUI Sight Engine]
    Tools --> |apply_code_fix| Handshake{Dual-Agent Handshake}
    
    Handshake --> |Fetch Security Rules| DB
    Handshake --> Reviewer[Senior Reviewer Agent]
    Reviewer --> |Validate Change| Verdict{LGTM / Reject}
    Verdict --> |Approved| Disk[Write Changes to Disk]
    Verdict --> |Rejected| UI