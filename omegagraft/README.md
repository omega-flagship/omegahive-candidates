# OmegaGraft — L0 wiring library

Pure synthetic module-manifest validation, binding graph analysis, unplug blast
radius and swap proposals. Depends on the sibling `omegaatom` package and Python
3.9+ standard library. No install, server, network or interpreter execution.

From the folder that contains this checkout:

```sh
python -B -m unittest discover -s omegagraft/tests -v
python -B -m omegagraft.example
```

See WIRING (owner workspace record, not included) for schemas and authority
boundaries and PLUG_GUIDE (owner workspace record, not included) to integrate
a module. Every returned graph and lifecycle plan is L0, authority none.
`example.json` uses synthetic data only; its conformance atoms are fixture claims,
not actual Lab receipts. No live/runtime/usefulness qualification is implied.
