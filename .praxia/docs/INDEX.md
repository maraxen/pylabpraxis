# praxis Internal Docs

## Daily
- [260825_p22_verify_harness_landed](daily/260825_p22_verify_harness_landed.md)

## Handoffs
- [260131_e2e-autonomous-handoff](handoffs/260131_e2e-autonomous-handoff.md)
- [260131_ship-coordination-handoff](handoffs/260131_ship-coordination-handoff.md)
- [260129_praxis-handoff](handoffs/260129_praxis-handoff.md)
- [260128_e2e-database-seeding-handoff](handoffs/260128_e2e-database-seeding-handoff.md)
- [260128_e2e-stabilization-handoff](handoffs/260128_e2e-stabilization-handoff.md) — E2E Test Suite Stabilization - Session Handoff
- [260122_v01alpha-debug-handoff-20260121](handoffs/260122_v01alpha-debug-handoff-20260121.md)
- [260122_v01alpha-orchestrator-handoff-20260121-1845](handoffs/260122_v01alpha-orchestrator-handoff-20260121-1845.md)
- [260121_final-merge-handoff](handoffs/260121_final-merge-handoff.md)

## Plans
- [260902_plr-sema-oracle-harness](plans/260902_plr-sema-oracle-harness.md) — Design for catching plr-sema bugs by comparing static verdicts against PLR's chatterbox simulator (STRICT + tip/volume tracking) as ground-truth oracle: four input tiers (corpus replay, source-rendered corpus, mutation/metamorphic, wire-format fuzz), the soundness contract each verdict must satisfy, metrics, and phasing.
- [260824_repl-autocomplete-scope](plans/260824_repl-autocomplete-scope.md) — Scope and outcome for as-you-type completion in the JupyterLite PLR REPL; the planned jedi preload proved unnecessary
- [260824_w2_dispatch_draft](plans/260824_w2_dispatch_draft.md)
- [260824_w3_dispatch_draft](plans/260824_w3_dispatch_draft.md)
- [260824_w4_dispatch_draft](plans/260824_w4_dispatch_draft.md)
- [260824_w5_dispatch_draft](plans/260824_w5_dispatch_draft.md)
- [260817_praxis-repl-refocus-execution-plan](plans/260817_praxis-repl-refocus-execution-plan.md) — Dependency-ordered 8-phase execution plan composed from three adversarially-reviewed specs and five executed spikes, with per-phase gates, audit strategy, rollback, and an unproven-assumptions ledger.
- [260210_final-protocol-execution-fix-plan](plans/260210_final-protocol-execution-fix-plan.md)
- [260210_protocol-playground-fix-plan](plans/260210_protocol-playground-fix-plan.md)
- [260131_ship-work-plan](plans/260131_ship-work-plan.md)
- [260128_e2e-test-suite-hardening-plan](plans/260128_e2e-test-suite-hardening-plan.md)
- [260122_web-hid-shim](plans/260122_web-hid-shim.md)
- [260121_final-merge-plan](plans/260121_final-merge-plan.md)
- [260121_jules-integration-plan](plans/260121_jules-integration-plan.md)
- [260115_test-plan-v1](plans/260115_test-plan-v1.md)
- [telemetry](plans/.praxia/telemetry.jsonl)
- [telemetry.jsonl](plans/.praxia/telemetry.jsonl.lock) ⚠️ non-standard extension

## Specs
- [260902_plr-sema-tip-typestate-increment](specs/260902_plr-sema-tip-typestate-increment.md) — First post-corpus increment to the plr-sema pre-corpus specification. Narrows deferred item (a) (abstract domain) to a three-element per-channel tip typestate lattice and deferred item (c) (predicate language) to three atom productions over that lattice, so that the tip-loading / tip-requiring / tip-dropping method families produce real SAFE and WILL_FAIL findings instead of UNKNOWN. Every method family, every tracker class, every state field, every effect and every channel-arity default is DERIVED by AST inspection of PLR source and of the shipped contract table -- no hand-written method contract, and no hand-typed exception-class name (the two tip-state exception names come from plr_exception_taxonomy.json's own tip_state category, narrowed by that artifact's own module field). Adds one REASON_VOCABULARY member (7 -> 8 of 12), two check/graph.py mirror fields, one registry row (HM-24, the front end's six syntactic patterns), and no wire-format change. Gated by the oracle harness (#4879 corpus replay, #4881 mutants), not by a threshold. Revised after adversarial round 1 -- see the remediation changelog at the end.
- [260901_plr-sema-pre-corpus-spec](specs/260901_plr-sema-pre-corpus-spec.md) — Buildable-today specification for plr-sema: a self-contained package providing preflight (pre-execution) sound static validation of PyLabRobot execution graphs. Covers the eight corpus-INDEPENDENT sections (package seam + AST import boundary, provenance cherry-pick, tri-valued verdict data contract, telemetry error model, fork-drift tests, extractor/checker split, contract-derivation mechanics, differential harness) and defers all abstract-interpretation semantics to a literature corpus in compilation. Carries a mandatory hand-maintained/derived classification on every piece of logic, plus a hand-maintained surface budget and ratchet. spec_version 7 (T11) decouples derivation coverage from SUPPORTED_TOOLS: plr-sema now analyzes the whole PyLabRobot surface (4,770 methods) rather than 10 LiquidHandler tools. spec_version 8 (260901, task 260901_plr-jit-resolve-three-decisions) resolves all three §Open decisions items via an independent outside analysis (Fable), spot-verified by the orchestrator: no `UNREACHABLE` member now (reserve the string, add an unrecognized-verdict-string consumer rule instead); volume tracking is already in the verdict path (PLR put it there), the real question — whether the predicate evaluator interprets numeric atoms — is deferred through v1 and the first increment; the shipped join table is NOT inverted, its ordering is the correct obligation-conjunction order, distinct from the (unrelated) information order that governs pre-emission state merging. No schema_version bump; no new machinery.
- [260827_coxswain-corpus-ingestion-increment-1](specs/260827_coxswain-corpus-ingestion-increment-1.md) — Implementable spec for the FIRST of four sequenced increments of LEDGERED THREE-AXIS INGESTION: training/ingest/ with sources.py (21-row committed SourceRegistry), licenses.py (mechanical SPDX->tier verification), recipes.py (recipes.yml parser), eval_split.py (committed holdout index + leak gate), audit.py (BLOCKING canonical-table drift detector), gap.py (PRE-REGISTERED coverage-gap gate). Facts-only, tier-0, fully offline, teacher-independent.
- [260827_coxswain-corpus-ingestion-strategy-turni](specs/260827_coxswain-corpus-ingestion-strategy-turni.md)
- [260825_copilot-pipeline-challenger](specs/260825_copilot-pipeline-challenger.md) — CHALLENGER-role findings against 260825_coxswain-phase-2-functiongemma-copilot-p.md. All file:line claims in the spec were re-verified against the tree on repl-fresh-boot; findings are ranked blocker/major/minor with cites and concrete fixes. No wholesale rewrite proposed.
- [260825_copilot-pipeline-defender](specs/260825_copilot-pipeline-defender.md) — DEFENDER counter-role review of 260825_coxswain-phase-2-functiongemma-copilot-p.md: steelman of D1-D10, robustness audit of load-bearing-but-fragile claims, critical-path feasibility re-verified against the tree, and resilience judgment of §8 counters. All repo cites re-verified 260825 on branch repl-fresh-boot.
- [260825_coxswain-phase-2-functiongemma-copilot-p](specs/260825_coxswain-phase-2-functiongemma-copilot-p.md) — Spec for the synthetic-data pipeline, functiongemma-270m-it fine-tune, browser serving via Transformers.js/WebGPU behind --with-coxswain, and ParseSource integration. REV 2: reconciled from challenger (2 blockers, 7 majors, 8 minors) and defender (11 robustness findings) reviews of 260825.
- [260825_p25_provisional_thresholds](specs/260825_p25_provisional_thresholds.md) — Numeric anchor proposal for the P2.6 three-number promotion gate (D8), derived from the P2.1 recorded-artifact baseline spread and the assembled P2.5 eval slice sizes. PROVISIONAL PER D8: exactly ONE revision permitted at P2.6 fine-tune eval, with recorded justification.
- [260825_p25_slice_gate](specs/260825_p25_slice_gate.md) — Blocking gate doc (backlog 480), rev 260901: full-scale corpus (812 rows) + live baseline on the whole 228-row eval split; verdict CONDITIONAL GO for P2.6 spend under three recipe/measurement conditions.
- [260824_coxswain-mvp-ux-spec](specs/260824_coxswain-mvp-ux-spec.md) — Implementable specification for the Coxswain propose/confirm, clarification, FFT-gate-extension and audit-trail surfaces: formalizes the eight negotiable UX axes (N1-N8) resolved in brainstorm session 48789b43 against the locked architecture (F1-F10), with fixer-ready work-item decomposition, correlation-ID contract, structural safety constraints mandated by the pre-mortem, and a risk table. Revised 260824 to close the adversarial review cycle (audits 260824_coxswain_spec_challenge / _defense) — see the Revision Log.
- [260824_coxswain-ux-open-design-axes-task-id-260](specs/260824_coxswain-ux-open-design-axes-task-id-260.md)
- [260817_spec-visualizer-transport-shim](specs/260817_spec-visualizer-transport-shim.md) — Adversarially-reviewed spec for the praxis REPL refocus (visualizer); converged=True after 1 round(s), verdict REVISE.
- [260817_spec-web-repl-extraction](specs/260817_spec-web-repl-extraction.md) — Adversarially-reviewed spec for the praxis REPL refocus (web-repl); converged=True after 1 round(s), verdict REVISE.
- [260817_spec-wheel-build-plr-upgrade](specs/260817_spec-wheel-build-plr-upgrade.md) — Adversarially-reviewed spec for the praxis REPL refocus (build-pipeline); converged=True after 2 round(s), verdict ACCEPT.
- [260122_inventory-wizard-design-spec](specs/260122_inventory-wizard-design-spec.md)
- [telemetry](specs/.praxia/telemetry.jsonl)
- [telemetry.jsonl](specs/.praxia/telemetry.jsonl.lock) ⚠️ non-standard extension

## Actuation Surfaces

## Audits
- [260902_plr-sema-tip-typestate-round1-challenger](audits/260902_plr-sema-tip-typestate-round1-challenger.md) — Challenger report on .praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md (spec_version 9 draft): 3 BLOCKER (A-COMMIT false via clear_head_state/update_head_state commit=False; conflicting depth-0 bridges unruled; tip_state taxonomy category has 5 members not 2), 2 MAJOR, 4 MINOR; verdict not_ready.
- [260902_plr-sema-tip-typestate-round1-defender](audits/260902_plr-sema-tip-typestate-round1-defender.md) — Defender adjudication of the round-1 challenger report on the spec_version 9 tip-typestate increment: O1 PARTIAL (counterexample does not reproduce under depth semantics; A-COMMIT text must narrow), O2 CONCEDE sharpened (conflicting depth-0 bridges must WIDEN — "no effect" is unsound), O3 CONCEDE (module filter on the taxonomy artifact), O4/O5 CONCEDE, O6–O9 trivial; 2 blockers survive, all text-only; verdict needs_revision, design intact.
- [260901_p26-promotion](audits/260901_p26-promotion.md) — Mechanical application of the pre-registered P2.6 promotion rule to arms A/B/C: all eligible, all marginal, A selected, NOT PROMOTED. Failure breakdown separates two scorer artifacts and one gold-set defect from genuine misses; the single D8 revision is proposed AGAINST spending now.
- [260206_hardware-discovery-audit](audits/260206_hardware-discovery-audit.md)
- [260206_python-worker-audit](audits/260206_python-worker-audit.md)
- [260131_comprehensive-logic-audit](audits/260131_comprehensive-logic-audit.md)
- [260129_code-smells-audit](audits/260129_code-smells-audit.md)
- [260129_complexity-audit](audits/260129_complexity-audit.md)
- [260129_dead-code-audit](audits/260129_dead-code-audit.md)
- [260129_e2e-coverage-audit](audits/260129_e2e-coverage-audit.md)
- [260129_e2e-failures-audit-260129](audits/260129_e2e-failures-audit-260129.md)
- [260129_e2e-file-audits](audits/260129_e2e-file-audits.md)
- [260129_feature-architecture-audit](audits/260129_feature-architecture-audit.md)
- [260129_service-layer-audit](audits/260129_service-layer-audit.md)
- [260125_audit-01-run-protocol](audits/260125_audit-01-run-protocol.md)
- [260125_audit-03-protocol-execution](audits/260125_audit-03-protocol-execution.md)
- [260125_audit-06-persistence](audits/260125_audit-06-persistence.md)
- [260125_audit-07-jupyterlite](audits/260125_audit-07-jupyterlite.md)
- [260125_audit-08-ghpages-config](audits/260125_audit-08-ghpages-config.md)
- [260125_audit-09-direct-control](audits/260125_audit-09-direct-control.md)
- [260125_build-errors](audits/260125_build-errors.md)
- [260125_index](audits/260125_index.md)
- [260125_plan-for-remediation](audits/260125_plan-for-remediation.md)
- [260123_jupyterlite-ghpages-audit](audits/260123_jupyterlite-ghpages-audit.md)
- [260123_opfs-pyodide-audit](audits/260123_opfs-pyodide-audit.md)
- [260123_visual-audit-data-playground](audits/260123_visual-audit-data-playground.md)
- [260123_visual-audit-run-protocol](audits/260123_visual-audit-run-protocol.md)
- [260123_visual-audit-settings-workcell](audits/260123_visual-audit-settings-workcell.md)
- [260122_css-theming-audit](audits/260122_css-theming-audit.md)
- [260122_io-transport-audit](audits/260122_io-transport-audit.md)
- [260121_component-audit-assets](audits/260121_component-audit-assets.md)
- [260121_component-audit-playground](audits/260121_component-audit-playground.md)
- [260121_dependency-audit](audits/260121_dependency-audit.md)
- [260121_extracted-plr-audit](audits/260121_extracted-plr-audit.md)
- [260115_machine-sim-audit](audits/260115_machine-sim-audit.md)
- [260115_protocol-asset-audit](audits/260115_protocol-asset-audit.md)
- [260115_styling-audit-report](audits/260115_styling-audit-report.md)
- [260115_workcell-ui-audit](audits/260115_workcell-ui-audit.md)
- [251222_pyodide-integration-audit](audits/251222_pyodide-integration-audit.md)

## Research
- [260901_nonlegacy-gap-ledger-reading](research/260901_nonlegacy-gap-ledger-reading.md) — Gap-ledger reading for the upstream_nonlegacy PLR surface (driver layer, no orchestration): guard-dense families, closure termination, unresolved frontier, dropped-receiver worklist, and the self-containment hypothesis measured directly.
- [260901_plr-sema-research-a-d](research/260901_plr-sema-research-a-d.md) — Research subagent output (260901) adjudicating deferred semantic questions (a) and (d) against the abstract-interpretation/typestate corpus; R3 (join grouped by operation_id) was later found to be wrong and is recorded as must-not-implement in the spec.
- [260901_plr-sema-research-b-f](research/260901_plr-sema-research-b-f.md) — Research subagent output (260901) on deferred semantic questions (b) and (f) from the abstract-interpretation/typestate corpus (NLM notebook + web).
- [260901_plr-sema-research-c-e](research/260901_plr-sema-research-c-e.md) — Research subagent output (260901) on deferred semantic questions (c) and (e); claims tagged by source (notebook / web / our code / measured), survey pin dd79c4c89.
- [260827_real-world-pylabrobot-dependent-repos-as-corpus-derivation-candidates](research/260827_real-world-pylabrobot-dependent-repos-as-corpus-derivation-candidates.md) — Survey of GitHub's dependency graph, plain code search, and filename-scoped dependency-file search (pyproject.toml/requirements.txt/lockfiles -- the highest-precision method found) for public repos using pylabrobot, to find real task/protocol corpora beyond the plr-cookbook for Coxswain out-of-surface and task-type coverage.
- [260825_copilot-pipeline-recon](research/260825_copilot-pipeline-recon.md) — Verification of the 260824 scoping doc claims against current code, filling gaps for the next phase spec: tool-schema extraction seams, Chatterbox execution verification, protocol fixtures, PLR docs corpus, web-repl serving substrate, parse-source seam, and artifact-size constraints.
- [260825_functiongemma-footprint](research/260825_functiongemma-footprint.md) — Measured delivery + serving footprint of onnx-community/functiongemma-270m-it-ONNX q4f16 beside a live Pyodide kernel: download bytes, peak RSS coexistence, prefill TTFT at realistic preamble length, decode tok/s, Cache-API retention across reloads and process restarts, WebGPU availability on the dev machine (WSL2 + AMD 890M iGPU), single-dtype recommendation (D4) and the running Pages storage ledger.
- [260825_functiongemma-training-serving-research](research/260825_functiongemma-training-serving-research.md) — Fine-tuning and browser-serving google/functiongemma-270m-it for a PyLabRobot lab-automation copilot
- [260825_gemma-license-deployment-gate](research/260825_gemma-license-deployment-gate.md) — Terms-of-use and prohibited-use-policy read-through (P2.0, backlog 4475); redistribution constraints for serving a functiongemma-270m-it fine-tune from a GitHub Pages origin; audience options + recommendation pending orchestrator/user sign-off.
- [260824_gemma-finetuned-plr-voice-text-copilot-scoping](research/260824_gemma-finetuned-plr-voice-text-copilot-scoping.md) — Scoping assessment for a Gemma model fine-tuned to translate voice/text lab instructions into validated PyLabRobot calls inside the JupyterLite Playground rebase: training-data sourcing, browser deployment feasibility, clarification UX, and build-location recommendation.
- [260817_g2-spike-battery-verdict](research/260817_g2-spike-battery-verdict.md) — Adjudication of the five G2 criteria from spikes S-A/S-B/S-C/S-D/S-E/S-F, with independent spot-check output; overall PARTIAL-GO.
- [260817_spike-evidence-repl-refocus](research/260817_spike-evidence-repl-refocus.md) — Five executed browser/CPython spikes grounding the refocus specs; every finding tagged ran/read with verbatim commands and output.
- [260817_standalone-web-repl-extraction-shell-and-brainstorm](research/260817_standalone-web-repl-extraction-shell-and-brainstorm.md)
- [260817_visualizer-transport-shim-and-augmentati-2-brainstorm](research/260817_visualizer-transport-shim-and-augmentati-2-brainstorm.md)
- [260817_visualizer-transport-shim-and-augmentati-brainstorm](research/260817_visualizer-transport-shim-and-augmentati-brainstorm.md)
- [260817_wheel-build-plr-upgrade-and-version-cohe-2-brainstorm](research/260817_wheel-build-plr-upgrade-and-version-cohe-2-brainstorm.md)
- [260817_wheel-build-plr-upgrade-and-version-cohe-brainstorm](research/260817_wheel-build-plr-upgrade-and-version-cohe-brainstorm.md)
- [260131_asset-wizard-filtering-logic-recon](research/260131_asset-wizard-filtering-logic-recon.md)
- [260131_simulated-machine-instantiation-recon](research/260131_simulated-machine-instantiation-recon.md)
- [260122_inventory-wizard-recon](research/260122_inventory-wizard-recon.md)
- [260122_jules-dispatch-recon-20260122](research/260122_jules-dispatch-recon-20260122.md)
- [260122_recon-asset-wizard-visual](research/260122_recon-asset-wizard-visual.md)
- [260122_recon-changelog-setup](research/260122_recon-changelog-setup.md)
- [260122_recon-documentation](research/260122_recon-documentation.md)
- [260122_recon-e2e-coverage](research/260122_recon-e2e-coverage.md)
- [260122_recon-e2e-infrastructure](research/260122_recon-e2e-infrastructure.md)
- [260122_recon-gitignore](research/260122_recon-gitignore.md)
- [260122_recon-global-shimming-status](research/260122_recon-global-shimming-status.md)
- [260122_recon-guided-setup-states](research/260122_recon-guided-setup-states.md)
- [260122_recon-hid-shim-status](research/260122_recon-hid-shim-status.md)
- [260122_recon-logo-branding](research/260122_recon-logo-branding.md)
- [260122_recon-playwright-jules](research/260122_recon-playwright-jules.md)
- [260122_recon-protocol-runner-visual](research/260122_recon-protocol-runner-visual.md)
- [260122_recon-repo-cleanup](research/260122_recon-repo-cleanup.md)
- [260122_recon-root-markdown](research/260122_recon-root-markdown.md)
- [260122_recon-socket-shim-status](research/260122_recon-socket-shim-status.md)
- [260122_recon-theme-variables](research/260122_recon-theme-variables.md)
- [260122_recon-versioning-strategy](research/260122_recon-versioning-strategy.md)
- [260122_relative-paths-recon-20260122](research/260122_relative-paths-recon-20260122.md)
- [260122_research-infinite-consumables](research/260122_research-infinite-consumables.md)

## Decisions
- [260827_teacher-backend-gemini-3-7-flash-for-full-scale-floor_gen-overlay_gen-pass](decisions/260827_teacher-backend-gemini-3-7-flash-for-full-scale-floor_gen-overlay_gen-pass.md) — Resolves the 260827 full-scale-generation backend blocker: Gemini 3.7 Flash chosen over titanix-vllm-primary, shelled via the local agy CLI (no API key) with batched, guided-decoding-enforced teacher calls. Covers PLR task-type/contract coverage strategy (incl. the chory-lab/plr-cookbook 91-recipe source), batching rationale (measured), version-brittleness mitigations, and empirical guided-decoding null-handling caveats.
- [260817_repl-layout-and-delivery-mechanism](decisions/260817_repl-layout-and-delivery-mechanism.md) — ADR resolving the path collision between the three refocus specs by deciding what ships as a wheel and what ships as loose fetched files; includes the single-class-object invariant, the three-detector drift design, and the per-spec re-scope tables that Phase 3's gate checks.

## Preregistration
- [260902_p26-rescore-amendment](preregistration/260902_p26-rescore-amendment.md) — Pre-registration amendment (backlog 4861) to the P2.6 prereg: three scoring defects are fixed (parser nested-list decoding, order-insensitive unresolved_slots comparison, assembler-derived gold gap fields) and the SAME three checkpoints plus baseline v2 are re-scored from saved generations with a row-level prediction registered before any scorer change; promotion rule and D8 anchors unchanged.
- [260902_p26b-floor-surface-prereg](preregistration/260902_p26b-floor-surface-prereg.md) — Pre-registration (task 260902_p26b_surface_data) for the floor_gen data fix: repair the 60 cardinality-excluded floor rows without moving any accepted row (synth 0.2.1, frozen seed), add a natural-phrasing lane (locations and verbs) routed to train only, assemble 0.1.4 with the pinned 228-row eval split and a probe set, retrain the arm-A recipe once and score it against baseline v2 and the existing A checkpoint under the unchanged promotion rule; row-level predictions registered before generation.
- [260901_p26-finetune-prereg](preregistration/260901_p26-finetune-prereg.md) — Pre-registration for the Coxswain P2.6 fine-tune (backlog 4848): fixed D5 recipe with one recorded deviation, three mixing arms (A raw / B 50% / C 33% negatives) after train-side dedup, the promotion rule applied mechanically against baseline v2 on the same 228-row eval split, what would count as the single D8 threshold revision, and where checkpoints live.

## Reference
- [260121_alembic-migration-guide](reference/260121_alembic-migration-guide.md)
- [260121_hardware-testing-guide](reference/260121_hardware-testing-guide.md)
- [260115_machine-sim-audit](reference/260115_machine-sim-audit.md)
- [260115_state-gap-analysis](reference/260115_state-gap-analysis.md)
- [260115_ui-guide](reference/260115_ui-guide.md)
- [260107_hardware-matrix](reference/260107_hardware-matrix.md)
- [260101_architecture](reference/260101_architecture.md)
- [251230_cli-commands](reference/251230_cli-commands.md)
- [251230_cmms-interface-design-research](reference/251230_cmms-interface-design-research.md)
- [251230_configuration](reference/251230_configuration.md)
- [251230_lims-ux-pattern-analysis](reference/251230_lims-ux-pattern-analysis.md)
- [251230_scientific-software-complexity-abstraction](reference/251230_scientific-software-complexity-abstraction.md)
- [251230_troubleshooting](reference/251230_troubleshooting.md)
- [251222_product-guidelines](reference/251222_product-guidelines.md)
- [251222_product](reference/251222_product.md)
- [251222_tech-stack](reference/251222_tech-stack.md)
- [251222_workflow](reference/251222_workflow.md)

## Roadmaps

### awesomation
- [260122_post-ship-roadmap](roadmaps/awesomation/260122_post-ship-roadmap.md)
- [251230_roadmap](roadmaps/awesomation/251230_roadmap.md)

### pre-ship-cleanup
- [260120_roadmap](roadmaps/pre-ship-cleanup/260120_roadmap.md)

## Archive

## Misc
- [260825_daily_jsonl_truncation_incident](misc/260825_daily_jsonl_truncation_incident.md)
- [260210_final-mvp-implementation-strategy](misc/260210_final-mvp-implementation-strategy.md)
- [260206_e2e-verification-feb03](misc/260206_e2e-verification-feb03.md)
- [260131_01-data-models](misc/260131_01-data-models.md)
- [260131_02-asset-wizard](misc/260131_02-asset-wizard.md)
- [260131_03-protocol-execution](misc/260131_03-protocol-execution.md)
- [260131_04-constraints](misc/260131_04-constraints.md)
- [260131_05-github-pages](misc/260131_05-github-pages.md)
- [260131_06-jupyterlite](misc/260131_06-jupyterlite.md)
- [260131_07-hardware-discovery](misc/260131_07-hardware-discovery.md)
- [260131_08-serialization](misc/260131_08-serialization.md)
- [260131_09-recommendations](misc/260131_09-recommendations.md)
- [260131_10-import-export](misc/260131_10-import-export.md)
- [260131_11-error-handling](misc/260131_11-error-handling.md)
- [260131_12-session-recovery](misc/260131_12-session-recovery.md)
- [260131_13-memory-management](misc/260131_13-memory-management.md)
- [260131_14-port-persistence](misc/260131_14-port-persistence.md)
- [260131_15-storage-quotas](misc/260131_15-storage-quotas.md)
- [260131_critical-features](misc/260131_critical-features.md)
- [260131_e2e-persistent-bugs](misc/260131_e2e-persistent-bugs.md)
- [260131_e2e-static-analysis](misc/260131_e2e-static-analysis.md)
- [260131_e2e-timeout-investigation](misc/260131_e2e-timeout-investigation.md)
- [260131_file-splitting-report](misc/260131_file-splitting-report.md)
- [260131_final-ship](misc/260131_final-ship.md)
- [260130_playwright-angular-best-practices-2026](misc/260130_playwright-angular-best-practices-2026.md)
- [260129_data-viz-e2e-investigation](misc/260129_data-viz-e2e-investigation.md)
- [260129_jules-stage1-prompts](misc/260129_jules-stage1-prompts.md)
- [260128_e2e-status](misc/260128_e2e-status.md)
- [260126_e2e-new-02](misc/260126_e2e-new-02.md)
- [260126_e2e-new-03](misc/260126_e2e-new-03.md)
- [260126_e2e-viz-01](misc/260126_e2e-viz-01.md)
- [260126_e2e-viz-02](misc/260126_e2e-viz-02.md)
- [260126_e2e-viz-03](misc/260126_e2e-viz-03.md)
- [260126_e2e-viz-04](misc/260126_e2e-viz-04.md)
- [260126_jlite-01](misc/260126_jlite-01.md)
- [260126_jlite-03](misc/260126_jlite-03.md)
- [260126_opfs-01](misc/260126_opfs-01.md)
- [260126_opfs-03](misc/260126_opfs-03.md)
- [260126_refactor-01](misc/260126_refactor-01.md)
- [260126_refactor-02](misc/260126_refactor-02.md)
- [260126_refactor-03](misc/260126_refactor-03.md)
- [260126_split-01](misc/260126_split-01.md)
- [260126_split-02](misc/260126_split-02.md)
- [260126_split-04](misc/260126_split-04.md)
- [260126_split-05](misc/260126_split-05.md)
- [260126_split-06](misc/260126_split-06.md)
- [260123_opfs-hardware-review-1](misc/260123_opfs-hardware-review-1.md)
- [260123_opfs-hardware-review](misc/260123_opfs-hardware-review.md)
- [260122_asset-selection-analysis](misc/260122_asset-selection-analysis.md)
- [260122_backend-categories-investigation](misc/260122_backend-categories-investigation.md)
- [260122_docs-404-investigation](misc/260122_docs-404-investigation.md)
- [260122_frontend-backend-type-architecture](misc/260122_frontend-backend-type-architecture.md)
- [260122_inventory-search-investigation](misc/260122_inventory-search-investigation.md)
- [260122_investigation-selective-transfer-params](misc/260122_investigation-selective-transfer-params.md)
- [260122_machine-args-configuration-investigation](misc/260122_machine-args-configuration-investigation.md)
- [260122_machine-type-filtering-investigation](misc/260122_machine-type-filtering-investigation.md)
- [260122_on-the-fly-definitions-investigation](misc/260122_on-the-fly-definitions-investigation.md)
- [260122_oracle-asset-wizard-investigation](misc/260122_oracle-asset-wizard-investigation.md)
- [260122_post-merge-checklist](misc/260122_post-merge-checklist.md)
- [260122_post-ship](misc/260122_post-ship.md)
- [260122_resource-vs-machine-flow-investigation](misc/260122_resource-vs-machine-flow-investigation.md)
- [260122_shared-array-buffer](misc/260122_shared-array-buffer.md)
- [260122_simulation-backend-dropdown-bug](misc/260122_simulation-backend-dropdown-bug.md)
- [260122_simulation-selection-investigation](misc/260122_simulation-selection-investigation.md)
- [260121_connection-persistence-tests](misc/260121_connection-persistence-tests.md)
- [260121_extracted-browser-interrupt](misc/260121_extracted-browser-interrupt.md)
- [260121_extracted-geometry-heuristics](misc/260121_extracted-geometry-heuristics.md)
- [260121_extracted-machine-registration](misc/260121_extracted-machine-registration.md)
- [260121_jules-handover-20260121](misc/260121_jules-handover-20260121.md)
- [260121_jules-session-triage](misc/260121_jules-session-triage.md)
- [260121_orchestrator-session-summary-20260121](misc/260121_orchestrator-session-summary-20260121.md)
- [260121_summary](misc/260121_summary.md)
- [260121_v01alpha-final-review-20260121](misc/260121_v01alpha-final-review-20260121.md)
- [260121_v01alpha-status-20260121](misc/260121_v01alpha-status-20260121.md)
- [260120_orchestration](misc/260120_orchestration.md)
- [260120_verification-report](misc/260120_verification-report.md)
- [260118_frontend-polish](misc/260118_frontend-polish.md)
- [260116_runway](misc/260116_runway.md)
- [260115_qa-interaction-checklist](misc/260115_qa-interaction-checklist.md)
- [260115_resource-error-log](misc/260115_resource-error-log.md)
- [260115_state-gap-analysis](misc/260115_state-gap-analysis.md)
- [260115_suite-comprehensiveness-analysis](misc/260115_suite-comprehensiveness-analysis.md)
- [260114_compressed-archive](misc/260114_compressed-archive.md)
- [260114_installation-browser](misc/260114_installation-browser.md)
- [260114_installation-lite](misc/260114_installation-lite.md)
- [260114_installation-production](misc/260114_installation-production.md)
- [260114_update-archive](misc/260114_update-archive.md)
- [260107_notes](misc/260107_notes.md)
- [260107_technical-debt](misc/260107_technical-debt.md)
- [260105_protocol-inference-sharp-bits](misc/260105_protocol-inference-sharp-bits.md)
- [260102_browser-script](misc/260102_browser-script.md)
- [260101_development-matrix](misc/260101_development-matrix.md)
- [251230_assets](misc/251230_assets.md)
- [251230_backend](misc/251230_backend.md)
- [251230_browser-mode](misc/251230_browser-mode.md)
- [251230_code-style](misc/251230_code-style.md)
- [251230_contributing](misc/251230_contributing.md)
- [251230_data-visualization](misc/251230_data-visualization.md)
- [251230_execution-flow](misc/251230_execution-flow.md)
- [251230_frontend](misc/251230_frontend.md)
- [251230_hardware-discovery](misc/251230_hardware-discovery.md)
- [251230_installation](misc/251230_installation.md)
- [251230_overview](misc/251230_overview.md)
- [251230_protocols](misc/251230_protocols.md)
- [251230_quickstart](misc/251230_quickstart.md)
- [251230_rest-api](misc/251230_rest-api.md)
- [251230_services](misc/251230_services.md)
- [251230_state-management](misc/251230_state-management.md)
- [251230_testing](misc/251230_testing.md)
- [251230_websocket-api](misc/251230_websocket-api.md)
- [251225_technical-debt](misc/251225_technical-debt.md)
- [251222_general](misc/251222_general.md)
- [251222_html-css](misc/251222_html-css.md)
- [251222_javascript](misc/251222_javascript.md)
- [251222_python](misc/251222_python.md)
- [251222_typescript](misc/251222_typescript.md)

## Superpowers
> Skill outputs live in `.praxia/docs/superpowers/plans/` and `.praxia/docs/superpowers/specs/.
- [plans](superpowers/plans/) — brainstorming + writing-plans outputs
- [specs](superpowers/specs/) — specification outputs

