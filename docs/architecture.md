# Architecture Documentation

See the implementation plan artifact for the full architecture documentation,
including the directory tree, module responsibilities, build system, and
dependency flow.

## Quick Reference

### Layered Architecture

```
Layer 4: Dash UI        (dashboard/)   — Visualization & user interaction
Layer 3: Python Analytics (quantiv/)   — Pricer facade, analytics, data
Layer 2: pybind11 Bridge  (bindings/)  — Type translation C++ ↔ Python
Layer 1: C++ Engine       (engine/)    — All pricing math (pure C++)
```

### Rules

1. Each layer only imports from the layer directly below it.
2. The Dash UI never imports `_quantiv_engine` directly.
3. The C++ engine has zero Python dependencies.
4. All input validation happens in Python (Layer 3) before calling C++.
