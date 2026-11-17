# Ignite 2026: library-wide adversarial content review

Review date: **November 17, 2026 (UTC)**.

## Outcome and boundaries

Reviewed all **41 HTML/HTM files**: 34 categorized infographics, the existing
root Ignite guide, the library index, two utilities, and three redirect/archive
pages. Implemented substantive corrections across all 34 categorized
infographics and the existing Ignite guide. Utilities, navigation, contributor
guidance, and the library entry point were also reviewed and corrected where
needed. The guide was already present as an untracked user file when this work
began; it was preserved and edited, not replaced or relocated.

The review challenged production-readiness implications, mixed availability
labels, stale lifecycle advice, unsupported prices and quotations, privacy and
authorization absolutes, impossible recovery promises, and misleading
comparisons. Corrections extend through body text, tables, diagrams, FAQs,
recommendations, and interactive results, rather than only adding news banners.
Practical decision cues and pilot evidence replace unsupported sales promises.

**This is an editorial and source-grounded factual review, not certification of
every sentence, number, commercial term, region, model, customer outcome, or
deployment.** No production Azure deployment, licensing audit, penetration test,
legal review, or exhaustive accessibility audit was performed. An updated
accuracy date records this review; it is not proof of factual correctness.

## Source policy

The primary announcement baseline is the complete first-party
[Microsoft Ignite 2026 Book of News](https://news.microsoft.com/events/ignite/2026/book-of-news/).
Individual announcement details take precedence over broad summaries. Its
AI-generated instant summaries explicitly warn that they may be incorrect;
they were not treated as authoritative evidence.

- GA applies to the named feature, not every integration, dependent service,
  region, tenant, SKU, or identity type.
- Preview includes private preview where stated. Frontier eligibility and
  future rollout dates remain explicit.
- Where a newer explicit announcement conflicts with older documentation
  wording, the scoped announcement status is identified; adjacent features are
  not silently promoted.
- Historical Build and retired event pages remain historical. Their original
  announcement-time availability is not rewritten as today's availability.
- Benchmarks need attribution and workload context. Unsupported precise prices,
  customer quotations, percentages, and guaranteed outcomes were removed or
  recast as explicitly illustrative decision/measurement guidance.

## Highest-impact corrections

| Risk challenged | Implemented correction |
| --- | --- |
| Umbrella GA mistaken for universal GA | Microsoft IQ is the umbrella; its Work, Fabric, Foundry, and Web capabilities have feature-specific status. Foundry evaluation/insights/optimizer GA is separated from preview annotation/training. |
| Similar product names mistaken for identical offerings | Azure HorizonDB GA is distinguished from Fabric HorizonDB preview; Database Hub GA from operational database agents preview; Rayfin/Fabric apps GA from preview integrations/backends. |
| Governance mistaken for automatic authorization | Domains, labels, schemas, gateways, MCP tools, profiles, and grounding do not automatically enforce every engine's permissions. Revocation, source synchronization, identity support, and negative access tests are explicit. |
| Broad privacy promises across different model operators | Foundry privacy, residency, monitoring, encryption, and training statements are scoped to the exact offer and provider; modified abuse monitoring is not universal zero retention. |
| Quotas or alerts mistaken for hard spending limits | Gateway overshoot/counter scope, dispatched work, application reservations, actual reconciliation, and non-token costs are acknowledged. Commit units are not runtime Copilot Credits. |
| Recovery targets mistaken for guarantees | SQL recovery guidance distinguishes typical figures, SLAs, application recovery, asynchronous data loss, and measured drills. Impossible wizard requirements now show a visible design gap. |
| Expired or retiring services still sold as current | SQL Server 2016 is post-support with conditional paid ESUs; ACS is channel-by-channel transition guidance; Functions, Arc SCVMM, and Windows Server lifecycle details are qualified. |
| Security headlines mistaken for universal protection | ISOC core GA is separated from preview SIEM/retention. Local agent protection is limited to named supported Windows surfaces and licensing. Audit is distinguished from Block. |
| GitHub and Azure DevOps treated as one control plane | Azure DevOps app integration remains public preview with its own identity, audit, access, and cloud-session limitations. SDK 2.0 custom hosting is not the GitHub coding-agent service. |
| Unsupported persuasive claims | Removed or qualified fixed savings, performance multipliers, cross-vendor CVE comparisons, universal compliance claims, unverified quotations, and repeatable customer ROI promises. |

## Complete page coverage

Each categorized page below received implemented body-level corrections.

| File | Main correction or decision cue |
| --- | --- |
| `foundry/00-microsoft-stack-overview.html` | IQ architecture, feature lifecycle, identity, billing, and illustrative execution path. |
| `foundry/ai-agent-anatomy.html` | Workload-dependent concerns, approval/rollback, evidence, and scoped improvement/voice features. |
| `foundry/ai-gateway-apim.html` | Routed-traffic scope, token overshoot, cache isolation, tool authorization, and preview integrations. |
| `foundry/ai-landing-zones.html` | Reference implementation remains preview; deployment, sovereignty, and production-readiness boundaries. |
| `foundry/azure-ai-billing-models.html` | Deployment-specific meters, Priority processing, P3 commitment units, total cost, and purchasing checks. |
| `foundry/azure-document-intelligence.html` | Extraction versus grounding; SharePoint source GA versus preview ACL/indexing features and permission resync. |
| `foundry/foundry-data-safety-guide.html` | Offer/operator-specific privacy, geography, retention, encryption, and contractual boundaries. |
| `foundry/frontier-firm-playbook.html` | IQ and security scope, licensing, sourced measurement lessons, editorial versus attributed claims. |
| `foundry/microsoft-ai-decision-guide.html` | Overlapping platform entry points, scoped model/tool capabilities, pricing and status distinctions. |
| `foundry/microsoft-iq-platforms-guide.html` | Microsoft IQ umbrella, Web IQ, source-specific authorization, retrieval API scope, and actual data movement. |
| `foundry/tokenops-ai-roi-infographic.html` | Actual executed-call summation, cached tokens, other costs, concurrency-safe application budget requirements. |
| `fabric/microsoft-fabric-interactive.html` | IQ and database feature status, Rayfin, realistic OneLake/Direct Lake/governance boundaries. |
| `fabric/fabric-data-agent-best-practices.html` | DAX guidance versus authorization, verified-answer behavior, indexing preview, adversarial evaluation. |
| `fabric/fabric-governance-infographic.html` | Workspace/RLS boundaries, labels/DLP coverage, capacity throttling meaning, deployment verification. |
| `fabric/fabric-mcp-isv-scale-infographic.html` | Dedicated identities versus profiles, separate API planes, delegated/read-only IQ MCP, unified Power BI Report skill. |
| `fabric/medallion-architecture-infographic.html` | Table ACID versus pipelines, shortcuts versus backup, materialized-view constraints, retention and permissions. |
| `azure-databases/azure-sql-comparison.html` | Scoped MI GA capabilities, preview local container, backups, serverless, storage scopes, migration fit. |
| `azure-databases/azure-sql-db-bcdr.html` | Realistic RTO/RPO, immutability status, asynchronous regional recovery, explicit wizard design gaps. |
| `azure-databases/sql-2016-eol-customer-guide.html` | Past-tense end of support, conditional ESUs, savings-plan terms, Arc limitations, pilot proof points. |
| `app-platform-services/azure-apim-v2-networking-guide.html` | Correct tier/subnet delegation, gateway versus portal scope, private ingress versus egress, SKU comparison. |
| `app-platform-services/apim-logic-apps-functions-decision-guide.html` | Tier-specific policy support, preview model connections, runtime/hosting lifecycle, composed-system prerequisites. |
| `app-platform-services/azure-app-modernization-decision-map.html` | Catalyst GA, scoped modernization previews, target compatibility, behavioral/cutover/rollback gates. |
| `app-platform-services/azure-communication-services-guide.html` | Retained versus retiring channels, October restrictions, September 2028 retirement, identity and licensing. |
| `infrastructure/azure-arc.html` | Separate security licensing, ESU/SCVMM lifecycle, Hotpatch baselines, illustrative pricing and scoped previews. |
| `avd/healthcare-vdi-strategyguide.html` | Windows 365/AVD distinctions, supported sizes, clinical/peripheral validation, preview versus GA and recovery limits. |
| `defender-for-cloud/defender-for-cloud-unified-security.html` | CNAPP versus SOC/endpoint scope, plan prerequisites, scanner caps, AI coverage, ISOC and Perception status. |
| `github-copilot/agent-commit-identity.html` | Model/runtime/actor distinction and Azure DevOps user-attributed records. |
| `github-copilot/agent-correction-loop.html` | Review and acceptance evidence, authorized test accounts, Azure DevOps PR workflow limits. |
| `github-copilot/agent-governance-surface.html` | Separate evidence/control paths, qualified runtime protections and previews, narrow ruleset exceptions. |
| `github-copilot/ai-agent-setup-cost.html` | Zero workflow files is not zero governance work; SDK hosting responsibilities. |
| `github-copilot/ai-coding-agent-landscape.html` | Azure DevOps preview path, SDK versus assistant/service, feature-specific availability. |
| `github-copilot/copilot-learn-mcp-dogfood.html` | Metadata freshness is not fact verification; deployed schedules, token availability, and runs require evidence. |
| `others/build-2026-announcements-infographic.html` | Historical Build framing with a distinct current Ignite follow-through, not retroactive GA badges. |
| `others/innovation-hub-phases-guide.html` | Four publicly documented offerings, realistic engagement expectations, four-result selector and pilot preparation. |

The remaining seven files were also included:

| File | Disposition |
| --- | --- |
| `Ignite-2026-Book-of-News-Guide.html` | Reviewed 59 grouped summaries and corrected high-risk claims, source links, overlapping status presentation, headline promises, licensing and scope. Role filters and index retained. |
| `index.html` | Featured the current Ignite guide; retained generated category/catalog behavior. |
| `link-builder.html` | Reviewed utility behavior; repaired generated back navigation through its owning script. |
| `redirect.htm` | Reviewed allowlist and bounded tracking/navigation behavior; preserved utility, unchanged. |
| `azure-sql/index.html` | Fixed redirect/fallback destination to the actual library rather than a directory without an index. |
| `azure-sql/sql-2016-eol-customer-guide.html` | Confirmed target page exists; preserved valid redirect, unchanged. |
| `events/azure-events-may-2026.html` | Preserved existing retirement redirect; made fallback content explicitly archival and replaced expired registration calls with event details. |

## Selected verification sources beyond the Book of News

- Foundry: [model privacy](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy),
  [Claude hosting boundaries](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models-hosting-comparison),
  [deployment types](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types),
  [IQ sources](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/foundry-iq-faq),
  [landing-zone implementation](https://github.com/Azure/AI-Landing-Zones),
  [P3 terms](https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/copilot-credit-p3).
- Fabric: [data-agent modeling](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices),
  [IQ MCP](https://learn.microsoft.com/en-us/fabric/iq/connectors/fabric-iq-mcp),
  [multitenancy](https://learn.microsoft.com/en-us/power-bi/guidance/develop-scalable-multitenancy-apps-with-powerbi-embedding),
  [RLS](https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security),
  [materialized views](https://learn.microsoft.com/en-us/fabric/data-engineering/materialized-lake-views/overview-materialized-lake-view),
  [Power BI Report skill](https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-report-skill-overview).
- SQL: [continuity and recovery](https://learn.microsoft.com/en-us/azure/azure-sql/database/business-continuity-high-availability-disaster-recover-hadr-overview),
  [immutability](https://learn.microsoft.com/en-us/azure/azure-sql/database/backup-immutability),
  [ESU eligibility](https://learn.microsoft.com/en-us/sql/sql-server/end-of-support/extended-security-updates-frequently-asked-questions),
  [MI Next-gen GP](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/service-tiers-next-gen-general-purpose-use).
- Platform: [ACS transition](https://learn.microsoft.com/en-us/azure/communication-services/acs-retirement-and-breaking-changes-guide),
  [APIM feature matrix](https://learn.microsoft.com/en-us/azure/api-management/api-management-features),
  [Premium v2 networking](https://learn.microsoft.com/en-us/azure/api-management/inject-vnet-v2),
  [agent workflows](https://learn.microsoft.com/en-us/azure/logic-apps/agent-workflows-concepts),
  [SCVMM transition](https://learn.microsoft.com/en-us/azure/azure-arc/system-center-virtual-machine-manager/transition-guidance),
  [Windows 365 Flex](https://learn.microsoft.com/en-us/windows-365/enterprise/introduction-windows-365-flex),
  [AI threat protection](https://learn.microsoft.com/en-us/azure/defender-for-cloud/ai-threat-protection).
- GitHub: [Azure DevOps app integration](https://docs.github.com/en/copilot/how-tos/github-copilot-app/manage-azure-devops-work).
- Innovation Hub: [published offerings](https://www.microsoft.com/en-us/hub/offerings).

## Verification and release caveats

- Repository inventory reports **34 categorized pages**; supplemental whole-site
  parsing covers **all 41 HTML/HTM files**, including utilities and redirects.
- Whole-site checks find no duplicate IDs, missing local targets, or unresolved
  local fragments. All **31 nonempty inline JavaScript blocks** pass syntax
  checks.
- Guide assertions confirm **59 cards**, matching index entries, and overlapping
  status counts: **38 GA, 41 preview, 9 Frontier, 9 coming soon**. These are not
  mutually exclusive slices of 59; the misleading share-of-total chart was
  removed. Browser role filters return 17 business, 32 IT, 30 developer/data,
  and 16 security cards without cross-role leakage.
- The SQL BCDR wizard was exercised over **324 answer combinations**. Targeted
  post-EOS countdown, 24 platform tab selections, six AVD recommendation
  branches, and Defender quiz/restart checks passed. Innovation Hub native
  change events were exercised across all **80 answer combinations**, producing
  only the four documented offerings with matching visual selections.
- All **37 live pages** render at desktop 1280px and mobile 390px with zero page
  JavaScript errors and no root horizontal overflow. Small responsive fixes
  constrain Fabric flow labels, contain AVD reveal overflow, and stack ACS
  summary cards on narrow screens. This is representative responsive QA, not
  an exhaustive device/browser or assistive-technology matrix.
- The repository's terminology checker reports zero non-exempt matches
  (one intentional exemption). Its accessibility heuristics report zero
  issues. Neither result establishes complete accessibility or factual accuracy.
- The back-button producer now computes site-root destinations for root,
  category, and deeper pages, repairs incorrect marked links, and remains
  idempotent and read-only in check mode. Focused root/nested/repair/skip
  regression cases pass. The Innovation Hub's broken framework anchor is fixed.
- Existing tracked pages retain their automated chrome. Review dates are
  applied to **35 reviewed tracked pages** only through `stamp-accuracy-date.py`,
  and catalog generation remains owned by `generate-manifest.py`.
  The new-to-repository root guide intentionally
  does **not** prepopulate chrome; repository automation must add it on the PR
  or post-merge, per the contributor convention. Consequently whole-tree chrome
  checks identify that guide as the sole expected missing-chrome page.
- External-link crawl: **285/290 URLs** return success. Two Fabric references
  return HTTP 403 to automated fetching: the official
  `https://aka.ms/FabricApps-Ignite26` alias and its linked
  `community.fabric.microsoft.com/.../5422989` article. Three GitHub HTML links
  return HTTP 503; their corresponding raw Power BI README and two workflow
  files were retrieved successfully. These are access/transient-checker
  limitations, not grounds to invent replacement sources or declare every
  destination healthy.
- Arc's remaining displayed server prices are explicitly illustrative USD
  estimates, not verified quotes. Region, agreement, licensing, eligibility,
  preview admission, clinical certification, latency, savings, and recovery
  still require deployment-specific validation.
- Two existing external Google Fonts requests were blocked during browser QA;
  fallback fonts rendered. This review did not introduce external assets or
  rearchitect legacy font loading.

No commits, pushes, cloud deployments, or dependency installations were made.
The fork, web-upload, and pull-request contributor path remains unchanged.
