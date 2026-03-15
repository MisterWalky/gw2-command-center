# GW2 Command Center

![Status](https://img.shields.io/badge/status-alpha-orange)
![Version](https://img.shields.io/badge/version-0.0.1--alpha-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![GitHub last commit](https://img.shields.io/github/last-commit/MisterWalky/gw2-command-center)

GW2 Command Center is a personal project aimed at building a toolbox around the official Guild Wars 2 API in order to analyse, track and exploit game data.

The long-term goal is to create a flexible environment capable of analysing different aspects of a Guild Wars 2 account as well as the in-game economy.

This repository currently represents the foundation of the project, and most features are not yet implemented.

---

# Table of Contents

- Project Status
- Overview
- Future Scope
- Technologies
- Project Architecture
- Configuration
- Development Environment
- Development Notes
- Design Principles
- Roadmap
- Contributing
- License

---

# Project Status

Current version: 0.0.1-alpha

The project is currently in very early development and undergoing major architectural work.

At this stage:

- most functionality is not implemented
- many scripts are experimental
- the internal structure is still evolving
- breaking changes may occur at any time

Because of this:

- the project is not usable yet
- no support will be provided for running the project in its current state

The repository currently serves mainly as a development and architecture workspace.

---

# Overview

GW2 Command Center aims to provide tools capable of analysing and exploiting Guild Wars 2 data in ways that are difficult or impossible directly in-game.

Potential capabilities include:

- analysing Guild Wars 2 account data
- tracking inventory changes
- comparing account states (before / after)
- calculating hourly profitability
- analysing Trading Post market behaviour
- storing historical economic data
- feeding Excel / Power Query
- building data dashboards
- supporting economic research and experimentation

Not all future capabilities are documented yet.

Some ideas are still evolving and new features may appear during development.

---

# Future Scope

The project may eventually include advanced tools related to Trading Post analysis and economic modelling.

However, the most advanced trading-related tools may not necessarily be released publicly.

This aspect of the project is still under consideration.

---

# Technologies

The project currently relies on the following technologies:

- Batch scripting (.bat) for orchestration and console tools
- Python for API interaction and data processing
- SQLite for local data storage
- JSON for configuration and language files
- Guild Wars 2 Official API

Additional technologies may be integrated later depending on the evolution of the project.

---

# Project Architecture

Current repository structure:

gw2-command-center
│
├ dashboard
│  ├ core
│  └ i18n
│
├ scripts
│  ├ bat
│  └ python
│
├ modules
├ config
├ databases
├ logs
├ sql
│
├ README.md
├ CHANGELOG
├ VERSION
├ LICENSE
├ .gitignore
├ .env.example
└ pyproject.toml

---

# Configuration

The project uses environment variables for configuration.

Create a local configuration file by copying the example file.

Windows:

copy .env.example .env

Linux / macOS:

cp .env.example .env

Then edit `.env` and insert your Guild Wars 2 API key.

You can generate an API key here:

https://account.arena.net/applications

Example configuration:

GW2_API_KEY=YOUR_API_KEY_HERE
GW2_API_USER=YOUR_NAME

The `.env` file is ignored by Git and will never be uploaded to the repository.

---

# Development Environment

Recommended development environment:

- Visual Studio Code
- Python 3.11+
- Git

Recommended VS Code extensions:

- Python
- Ruff
- Black Formatter

---

# Development Notes

During the current development phase:

- source code comments are written in French
- comments will be translated into English later before the first stable release

This approach allows faster development while the architecture is still evolving.

Console messages and critical outputs are written in English whenever possible.

---

# Design Principles

Several principles guide the development of this project:

- modularity – components should remain independent whenever possible
- data persistence – important data should be stored and reusable
- reproducibility – analyses should be repeatable
- transparency – calculations and transformations should remain understandable
- experimentation – the project should remain a playground for exploring GW2 data

---

# Roadmap

The project roadmap is indicative and may evolve during development.

Phase 1 – Foundation

- establish project architecture
- implement language system
- build base scripting tools
- structure data storage

Phase 2 – Data Acquisition

- Guild Wars 2 API integration
- account data retrieval
- inventory tracking
- Trading Post data collection

Phase 3 – Data Processing

- data comparison tools
- economic analysis modules
- profitability calculations

Phase 4 – Data Exploitation

- Excel / Power Query integration
- dashboards and reporting
- historical economic analysis

---

# Contributing

Although the project is still experimental, constructive feedback is welcome.

Suggestions, ideas, technical discussions and encouragement are appreciated.

Please keep feedback:

- respectful
- constructive
- focused on improving the project

---

# License

This project is released under the MIT License.

Copyright (c) 2026 William CROCHOT (MisterWalky)

See the LICENSE file for details.
