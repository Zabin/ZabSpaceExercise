# Design Corpus — Index

[↑ Docs index](../INDEX.md)

Architecture & design documents — the **how**. These elaborate the Build Spec's architecture and
data sections; on any conflict the [build spec](../build-spec/INDEX.md) wins.

| Doc | Topic |
|---|---|
| [01-architecture-overview](01-architecture-overview.md) | Architecture overview — layers, the engine/session/UI seam, invariants. |
| [02-tech-stack-recommendation](02-tech-stack-recommendation.md) | Tech stack recommendation + suggested project layout. |
| [03-simulation-engine](03-simulation-engine.md) | Simulation engine — time, orbits, access windows, event loop. |
| [04-data-model](04-data-model.md) | Data model — entities, assets, actions, schemas. |
| [05-cell-interfaces](05-cell-interfaces.md) | Cell interfaces — Red / Blue / White UX and permitted actions. |
| [05-interface-control-document](05-interface-control-document.md) | Interface Control Document — contracts between components, derived from the approved GDS-01–04 + ADR baseline. |
| [06-white-cell-controls](06-white-cell-controls.md) | White Cell controls — vignette selection, time travel, injects. |
| [07-api-and-networking](07-api-and-networking.md) | API & networking — client contract and the multiplayer seam. |
| [09-gui-principles](09-gui-principles.md) | GUI principles & UX for space operators. |
| [10-sda-3d-viewer](10-sda-3d-viewer.md) | SDA-derived 3D viewer. |
| [11-command-planning-and-tasking](11-command-planning-and-tasking.md) | Command planning & sensor tasking. |
| [12-safe-mode-loop](12-safe-mode-loop.md) | Safe-mode: attack, detection & recovery loop. |
| [13-operator-command-catalog](13-operator-command-catalog.md) | Operator command catalog — bus & payload commands by mission. |
| [14-delta-v-economy](14-delta-v-economy.md) | Delta-V economy — fuel as the operator's hardest constraint. |
| [15-worked-asset-templates](15-worked-asset-templates.md) | Worked example: asset template library. |

> Numbering preserves the original series (08 was never used). `05-interface-control-document.md`
> shares the `05` prefix with `05-cell-interfaces.md` by request — it was not assigned the next free
> number in the series. The implemented operator console is specified in
> [`../build-spec/07-operator-console.md`](../build-spec/07-operator-console.md).
