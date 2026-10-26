# ProteinMPNN training runtime

[Download the self-contained source package](proteinmpnn-training-runtime.tar.gz). It includes pristine upstream training and data code, the exact previously measured candidate, pinned dependencies, a full-data 150-epoch recipe, seed controls, exclusive GPU locking, owned-process cleanup, and a completed-run audit.

```bash
tar -xzf proteinmpnn-training-runtime.tar.gz
cd proteinmpnn-runtime
# Read README.md before choosing data, GPU and runtime bounds.
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

**GPU startup validated (2026-10-26):** fixed a multiprocessing pickling error in the launcher by keeping worker callbacks in an importable module. Both original and candidate completed the same one-epoch startup fixture (64-example loading cap, five updates), with 472 finite checkpoint tensors each and clean owned-process cleanup. Process times were 37.46 s and 143.01 s respectively; cold compilation makes this small run slower. This is not a speedup result, numerical-equivalence verdict or full-training certification.

The archive includes GPU_STARTUP_CHECKS.json. Model and native training sources are unchanged by this fix. A separate six-epoch real-configuration reference/candidate/reference comparison is in progress; no results are claimed yet.
