# ProteinMPNN training runtime

[Download the self-contained source package](proteinmpnn-training-runtime.tar.gz). It includes pristine upstream training and data code, the exact previously measured candidate, pinned dependencies, a full-data 150-epoch recipe, seed controls, exclusive GPU locking, owned-process cleanup, and a completed-run audit.

```bash
tar -xzf proteinmpnn-training-runtime.tar.gz
cd proteinmpnn-runtime
# Read README.md before choosing data, GPU and runtime bounds.
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

**Prepared, not GPU-validated:** the new launcher passed source identity, syntax, data-layout and rejected-override checks. No new GPU run, full-data convergence or four-gate certification is claimed. Follow the package README for the remaining validation steps. The complete-data recipe is larger than the earlier benchmark and may OOM; do not silently shrink it and report the result as the original workload.

Both assigned two-GPU hosts were occupied when this package was prepared, so no competing GPU job was started.
