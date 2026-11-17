# GitHub Copilot Agent Series Claim Matrix

Last refreshed: 2026-11-17

## Ignite 2026 follow-through

The November pass retained the control-plane distinction and added two important
boundaries. The Copilot app's Azure DevOps integration is **public preview**, uses
Azure DevOps permissions and user-attributed records, and does not support cloud
sessions for those repositories. Microsoft Copilot SDK 2.0 is a **GA custom-agent
runtime**, not another hosted issue-to-PR integration or an automatic OS sandbox.
The app's general availability across plans must not be used to imply that every
integration or capability is GA.

The series now separates these surfaces in setup, identity, correction, and
governance guidance. Defender runtime protection for named Windows agent surfaces
is also distinct from preview Entra Agent ID discovery, Dynamic Agent Risk, and
Agent 365 MCP gateway governance. No vendor capability ranking is implied.

Current primary evidence:

- https://news.microsoft.com/events/ignite/2026/book-of-news/
- https://docs.github.com/en/copilot/how-tos/github-copilot-app/manage-azure-devops-work
- https://docs.github.com/en/copilot/concepts/copilot-surfaces/github-copilot-app
- https://commandline.microsoft.com/microsoft-copilot-sdk-2-0-github/

## Earlier series corrections

The table below records earlier corrections; its line references are historical,
not stable locations in the refreshed HTML. Product and billing terminology in
the current sources takes precedence over the historical source list.

This matrix records the accuracy pass behind the GitHub Copilot agent infographic series. It is intentionally narrow: claims are grounded in public product docs and should be rechecked before customer reuse after major Copilot, Claude, Codex, or Cursor releases.

| Page / current line | Claim audited | Verdict | Replacement text now used | Primary sources |
| --- | --- | --- | --- | --- |
| `github-copilot/ai-coding-agent-landscape.html:181` | Agent choice framed as Copilot vs third-party vendors. | Updated | Reframed as agent control planes: GitHub-native Copilot, GitHub-hosted third-party agents, standalone vendor integrations, and Cursor Cloud Agents. Watch-outs replace "worst fit." | GitHub third-party agents, Copilot cloud agent, Cursor Cloud Agents |
| `github-copilot/ai-agent-setup-cost.html:333` | "Only Copilot has zero repo files." | Updated | GitHub-hosted agents can be enabled without repo workflow YAML after policy enablement; standalone Claude Code Action remains the workflow-file path. | GitHub third-party agents, Claude Code GitHub Actions |
| `github-copilot/agent-governance-surface.html:202` | Third-party options always distribute governance outside GitHub. | Updated | GitHub-hosted Claude/Codex inherit GitHub agent surfaces; standalone integrations still introduce vendor dashboards, secrets, account settings, or mixed audit surfaces. | GitHub third-party agents, OpenAI Codex GitHub integration, Cursor pricing/security notes |
| `github-copilot/agent-commit-identity.html:206` | First-party vs third-party App is the only useful identity split. | Updated | Identity is now shown as four patterns: Copilot cloud agent, GitHub-hosted Claude/Codex, Claude Code Action, and standalone Codex/Cursor. | GitHub third-party agents, Copilot cloud agent, Claude Code GitHub Actions |
| `github-copilot/agent-correction-loop.html:302` | Codex always pushes correction state into ChatGPT and non-Copilot loops are inherently split. | Updated | GitHub-hosted agents keep routine feedback closest to GitHub; standalone integrations can still post back to PRs but may add Actions logs, API/token cost, or vendor workspace state. | GitHub third-party agents, OpenAI Codex GitHub integration, Claude Code GitHub Actions, Cursor Cloud Agents |
| `github-copilot/copilot-learn-mcp-dogfood.html:218` | Scheduled workflow guarantees Copilot PRs and fully automatic accuracy maintenance. | Updated | Workflow creates review issues; Copilot assignment depends on `COPILOT_ASSIGN_TOKEN` and agent availability; PR creation is intended but not guaranteed; human review remains required. | Local workflow files, Copilot cloud agent docs, Microsoft Learn MCP docs |

## Source Set

- GitHub Copilot cloud agent: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent
- GitHub third-party agents: https://docs.github.com/en/copilot/concepts/agents/about-third-party-agents
- GitHub Copilot premium requests: https://docs.github.com/en/billing/concepts/product-billing/github-copilot-premium-requests
- OpenAI Codex GitHub integration: https://developers.openai.com/codex/integrations/github
- Claude Code GitHub Actions: https://code.claude.com/docs/en/github-actions
- Cursor Cloud Agents: https://cursor.com/blog/cloud-agents
- Cursor pricing and governance signals: https://cursor.com/pricing
- Microsoft Learn MCP: https://learn.microsoft.com/en-us/training/support/mcp
