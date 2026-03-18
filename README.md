# GW2 Command Center

![Status](https://img.shields.io/badge/status-alpha-orange)
![Version](https://img.shields.io/badge/version-0.0.1--alpha-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![GitHub last commit](https://img.shields.io/github/last-commit/MisterWalky/gw2-command-center)

GW2 Command Center is a personal project focused on building a structured analysis environment around the official Guild Wars 2 API.

The goal is to progressively develop a toolbox capable of collecting, storing, tracking and exploiting game data for account analysis, historical monitoring, economic research and future dashboard workflows.

The project is currently in an **early alpha stage**, but its technical foundations are already being structured for long-term growth.

---

## Table of Contents

- [Overview](#overview)
- [Current Status](#current-status)
- [Current Foundations](#current-foundations)
- [Planned Scope](#planned-scope)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Project Architecture](#project-architecture)
- [Internationalization](#internationalization)
- [Development Tooling](#development-tooling)
- [Design Principles](#design-principles)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

GW2 Command Center is designed as a long-term toolkit for working with Guild Wars 2 data outside the game itself.

The project aims to support workflows such as:

- account data analysis
- inventory and state tracking
- before / after comparisons
- Trading Post monitoring
- historical data storage
- data extraction for Excel / Power Query
- dashboard-oriented workflows
- economic research and experimentation

The architecture is being built progressively so the project can scale cleanly as new endpoints and analysis modules are added.

---

## Current Status

Current version: **0.0.1-alpha**

This repository is currently in **early active development**.

What that means in practice:

- the architecture is being built and refined
- several scripts are still experimental
- some modules are foundations rather than finished features
- breaking changes may occur during the alpha phase

Even so, the repository already contains the first real building blocks of the project and is no longer just an empty placeholder.

---

## Current Foundations

The following elements are already present in the project:

- project structure and base folders
- environment-based configuration through `.env`
- centralized Python configuration system
- support for application language selection
- support for Guild Wars 2 API language selection
- centralized endpoint definitions
- SQLite-based local storage approach
- batch and Python orchestration groundwork
- development tooling configuration (`black`, `ruff`, `pytest`)
- repository hygiene files (`.editorconfig`, `.gitignore`)
- initial i18n consistency tooling

These foundations are important because they define how future features will be added and maintained.

---

## Planned Scope

The long-term scope of the project may include:

- account snapshot collection
- inventory tracking over time
- endpoint synchronization pipelines
- Trading Post price history collection
- reusable SQLite datasets
- reporting and dashboard preparation
- Excel / Power Query integration
- historical analysis tooling
- economic experimentation modules

Some advanced analysis features may remain partially private depending on their strategic value and future direction of the project.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/MisterWalky/gw2-command-center.git
cd gw2-command-center
```

### 2. Create your local environment file

#### Windows

```bash
copy .env.example .env
```

#### Linux / macOS

```bash
cp .env.example .env
```

### 3. Edit `.env`

Fill in at least your API key and basic language settings:

```env
GW2_API_KEY=YOUR_API_KEY_HERE
GW2_API_USER=your-name
APP_LANG=en
GW2_API_LANGS=en
```

### 4. Generate your Guild Wars 2 API key

You can create an API key from your ArenaNet account page:

`https://account.arena.net/applications`

### 5. Run the project tools

At this stage, available entry points and workflows are still evolving.
The repository should currently be considered an alpha workspace with usable foundations rather than a fully packaged end-user application.

---

## Configuration

The project uses environment variables stored in a local `.env` file.

The `.env` file is ignored by Git and must never be committed.

### Main variables

| Variable | Role |
|---|---|
| `GW2_API_KEY` | Guild Wars 2 API key |
| `GW2_API_USER` | Custom identifier included in the HTTP `User-Agent` |
| `APP_LANG` | Language used by the application interface |
| `GW2_API_LANGS` | One or more languages requested from the Guild Wars 2 API |

---

### Application language

`APP_LANG` defines the language used by the application interface:

- console messages
- diagnostics
- menus
- internal tool outputs

If the value is missing or invalid, the application falls back to:

```text
en
```

Supported application language codes:

| Code | Language |
|---|---|
| `en` | English |
| `fr` | French |
| `de` | German |
| `es` | Spanish |
| `it` | Italian |
| `pt` | Portuguese |
| `pl` | Polish |
| `ru` | Russian |
| `ja` | Japanese |
| `ko` | Korean |

---

### API languages

`GW2_API_LANGS` controls which languages are requested from the Guild Wars 2 API.

Supported API languages at the moment:

| Code | Language |
|---|---|
| `en` | English |
| `fr` | French |
| `de` | German |
| `es` | Spanish |

Rules:

- values are comma-separated
- spaces are ignored during normalization
- duplicates are ignored
- unsupported values are ignored
- order is preserved
- if empty or invalid, fallback is `en`
- special value `all` enables all supported API languages

Examples:

```env
GW2_API_LANGS=en
GW2_API_LANGS=fr
GW2_API_LANGS=fr,en
GW2_API_LANGS=fr,en,de
GW2_API_LANGS=all
```

Reference date for supported API languages: **2026-03**

Official Guild Wars 2 API documentation:

`https://wiki.guildwars2.com/wiki/API:Main`

---

## Project Architecture

Current repository structure:

```text
gw2-command-center/
├─ config/
├─ dashboard/
├─ databases/
├─ exports/
├─ logs/
├─ modules/
├─ scripts/
│  ├─ bat/
│  └─ python/
├─ snapshots/
├─ sql/
├─ temp/
├─ .editorconfig
├─ .env.example
├─ .gitignore
├─ CHANGELOG
├─ LICENSE
├─ pyproject.toml
├─ README.md
└─ VERSION
```

Notes:

- local `.env` files are not versioned
- SQLite runtime files are not versioned
- the architecture is still evolving during alpha development

---

## Internationalization

The project includes an i18n approach for application messages and diagnostics.

Current principles:

- application language is controlled through `APP_LANG`
- language files are stored as JSON files
- English acts as the reference fallback language
- partial language files are supported through merge fallback logic
- missing or invalid language requests automatically fall back to English

A dedicated validation script is also planned to help verify consistency between language files.

---

## Development Tooling

The repository already includes configuration for:

- **Black** for formatting
- **Ruff** for linting and import organization
- **Pytest** for future test workflows
- **EditorConfig** for cross-editor consistency

Recommended environment:

- **Python 3.11+**
- **Visual Studio Code**
- **Git**

Recommended VS Code extensions:

- Python
- Pylance
- Black Formatter
- Ruff

---

## Design Principles

Several principles guide the project structure and future development:

- **modularity** — separate responsibilities cleanly
- **data persistence** — retain useful historical data
- **reproducibility** — make analyses repeatable
- **clarity** — keep transformations understandable
- **scalability** — prepare for additional endpoints and modules
- **experimentation** — allow room for testing and iteration

---

## Roadmap

The roadmap is indicative and may evolve.

### Phase 1 — Foundations
- establish repository structure
- finalize configuration patterns
- stabilize endpoint definitions
- strengthen i18n support
- improve runtime workflow

### Phase 2 — Data Acquisition
- implement endpoint synchronization
- retrieve structured account data
- support inventory-oriented snapshots
- collect Trading Post price data

### Phase 3 — Data Processing
- compare stored states
- normalize reusable datasets
- build analysis-ready tables
- prepare economic calculations

### Phase 4 — Data Exploitation
- integrate Excel / Power Query workflows
- prepare dashboard datasets
- support historical analysis
- expand reporting capabilities

---

## Contributing

The project is still early, but constructive feedback is welcome.

Useful contributions may include:

- bug reports
- architectural feedback
- code quality suggestions
- endpoint modelling discussions
- documentation improvements

Please keep discussions respectful, useful and focused on improving the project.

---

## License

This project is released under the **MIT License**.

Copyright (c) 2026 William CROCHOT (MisterWalky)

See the `LICENSE` file for details.
