# CDIE evidence bundle

This archive contains the CDIE response, KU validation answers and NPHL technical summary, plus evidence for the three deployed BactoAI models. The NPHL letter is not included.

The prediction CSVs and split files are under `validation_results/`. The package also includes the model manifest, prediction verification, label-provenance audit, genome manifests, source metadata, and the regeneration scripts.

The verified holdout AUCs are 0.9421 for meropenem (n=124), 0.8773 for ciprofloxacin (n=143), and 0.8723 for cefotaxime (n=145). All 412 test predictions retain the same label under the live adaptive-threshold rule as under a fixed 0.50 threshold.

To reproduce the predictions and verify the resulting CSVs:

```text
python scripts/regenerate_test_predictions.py --workers 8
python scripts/verify_regenerated_predictions.py
```

The 0.9871 and 0.9559 AUCs came from a non-equivalent split and are withdrawn as holdout results. The 0.9333 BV-BRC AUC is an in-corpus benchmark, not independent validation. The 0.7793 internal AUC is withdrawn because its row-level predictions are unavailable for recomputation.

The CSV verification can run without genome FASTAs. Regenerating predictions requires the matching FASTAs listed in `validation_results/all_metadata_genome_manifest.csv`; the genome files are not tracked in Git.
