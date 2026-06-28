# Plan: Declarative LogicalTypeRule registry (finding 3, on trunk) (logical-types-registry)

## Context

Code-review finding 3 (re-applied to origin/main): `src/ibis_profiling/logical_types.py` is ~1,147
lines of ~37 rule classes, most copy-pasting the identical pattern: reject non-string, aggregate
`has_non_null`, aggregate `all_match` (`(col.re_search(REGEX) | col.isnull()).all()`), evaluate both
booleans. Display labels live in a separate map in `report/model/summary.py`.

Replace the copy-pasted regex/allowed-value rule classes with **declarative `LogicalTypeRule`
instances** evaluated by one generic implementation; move display labels into the registry. Keep
dedicated strategy classes for the genuinely-different rules. **Behavior-preserving** — every
column infers the same logical type.

Keep as strategy classes: `String`, `Boolean`, `Count`, `Integer`, `Decimal`, `DateTime`,
`Complex`, `Age`, `Ordinal`, `Categorical`. Migrate to `LogicalTypeRule` (the regex/all_match
pattern): `Email`, `URL`, `IPAddress`, `PhoneNumber`, `CreditCard`, `SSN`, `JSON`, `CUID`, `NanoID`,
`MACAddress`, `CountryCode`, `FilePath`, `Geometry`, `Currency`, `IBAN`, `SWIFT`, `TaxID`, `ISIN`,
`StockTicker`, `Gender`, `LanguageCode`, `Passport`, `USState`, `USTerritory`, `USMilitaryMail`,
`USZipCode`, `UUID`, and any other class with the reject-non-string + `re_search`/`isin` + all_match
shape.

Relevant files: `src/ibis_profiling/logical_types.py` (rules + `IbisLogicalTypeSystem` registry +
`get_fallback_type`); `src/ibis_profiling/report/model/summary.py` (display-label map). Safety net
(must stay green): `tests/test_logical_types.py` + the `tests/test_*_logical_types.py` files + the
regression gate (per-column `logical_type`).

**Slug used throughout this plan:** `logical-types-registry`

---

## Orchestration Contract

**Slug:** `logical-types-registry`

**Plan file:**

```text
docs/plans/2026-06-21_logical-types-registry.md
```

**Implementation branch:**

```text
feat/logical-types-registry
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/logical-types-registry_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/logical-types-registry_finalized
```

**Review notes:**

```text
docs/review/logical-types-registry-review-*.md
```

Each review note ends with exactly one status trailer:

```text
STATUS: CHANGES_REQUESTED
```

or:

```text
STATUS: APPROVED
```

---

## Required Agent Protocol

1. Use the **implementer** skill.
2. Work from the repository root.
3. Branch from `refactor/findings-on-trunk`.
4. Commit this plan as the first commit on the implementation branch.
5. Follow TDD where behavior changes are testable.
6. Run quality gates before marking any round complete.
7. Do not write your own review.
8. Do not create files under `docs/review/`.
9. Do not delete files under `docs/review/`.
10. Review notes are durable audit records and must be committed.
11. Resolving a review note means:
    - implement the requested changes;
    - run quality gates;
    - commit the code/docs changes;
    - commit the review note itself if it is not already committed;
    - recreate the round-complete marker.
12. After finalization, stop polling and exit cleanly.

---

## Setup

Start from `refactor/findings-on-trunk`:

```bash
git checkout refactor/findings-on-trunk
# ORCH_LOCAL_ONLY: local trial branch, skipping origin pull
git checkout -b feat/logical-types-registry
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_logical-types-registry.md
git commit -m "docs(plan): add logical-types-registry implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. The regression gate (per-column `logical_type`) and the
`*_logical_types.py` test files are the oracle for byte-identity — they verify each migrated rule.

1. Baseline: `./run.sh uv run pytest -q tests/test_logical_types.py tests/test_*_logical_types.py`.
2. Add `@dataclass(frozen=True) LogicalTypeRule` (`name`, `display_label`, `regex: str | None`,
   `allowed_values: frozenset[str] | None`, `accepted_physical_types: tuple = (dt.String,)`) + a
   generic evaluator exposing the SAME interface the registry loop uses (`name`,
   `get_check_exprs(col)`, `evaluate(results)`): reject non-accepted types -> has_non_null False;
   else `has_non_null = col.notnull().any()`, `all_match = (col.re_search(regex) | col.isnull()).all()`
   (for allowed_values use `(col.isin(list(values)) | col.isnull()).all()`); evaluate = both true.
   Match the existing key-prefixing so batched aggregation still works. Give the kept strategy
   classes the same interface (`name`, `display_label`).
3. Replace each migrate-listed class with a `LogicalTypeRule(...)` transcribing its regex (or
   allowed-value set), accepted types, and registry ORDER EXACTLY. Delete the migrated classes.
4. Build the ordered `IbisLogicalTypeSystem` registry from rules + strategy objects, preserving the
   exact current order, each with a `display_label`.
5. Replace the hardcoded `ltype_display_map` in `report/model/summary.py` with a lookup of the
   matched type's `display_label` (rendered labels unchanged).
6. Keep `get_fallback_type` + inference execution working; do not change which type wins for any
   input. Run the safety-net tests continuously — same pass count + gate 0 differences. If any
   logical_type changes, a transcription is wrong; fix the rule, never the baseline.

---

## Quality Gates

Run before marking any round complete:

```bash
scripts/orchestration/run-quality-gates
scripts/orchestration/check-review-notes-not-deleted
git status --short
```

The round is not complete unless:

1. all requested implementation work is done;
2. all relevant tests pass;
3. build/typecheck gates pass;
4. review notes have not been deleted;
5. the working tree is clean;
6. all code/docs changes are committed.

---

## Verification

1. `scripts/orchestration/run-quality-gates` passes — regression gate 0 differences (every column's
   `logical_type` unchanged) and all `*_logical_types.py` files at the same pass count.
2. `logical_types.py` is substantially smaller (hundreds of lines deleted).
3. Migrated classes are now `LogicalTypeRule` instances; strategy classes remain; `summary.py` no
   longer hardcodes the label map. `ty check src/` + `ruff` clean.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished logical-types-registry
```

This writes:

```text
/tmp/ibis-profiling/logical-types-registry_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer logical-types-registry`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/logical-types-registry-review-*.md
```

When a review note exists or a new review note appears:

1. Read the full review note.
2. If the note ends with:

   ```text
   STATUS: CHANGES_REQUESTED
   ```

   then resume work.

3. Clear the round-complete marker:

   ```bash
   scripts/orchestration/clear-finished logical-types-registry
   ```

4. Address every requested change.
5. Run quality gates:

   ```bash
   scripts/orchestration/run-quality-gates
   scripts/orchestration/check-review-notes-not-deleted
   ```

6. Commit code/docs fixes.
7. Commit the review-note file itself if it is not already committed:

   ```bash
   git add docs/review/logical-types-registry-review-*.md
   git commit -m "docs(review): record logical-types-registry review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished logical-types-registry
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer logical-types-registry` after the next review note is created.

---

## Approval Handling

If the latest review note ends with:

```text
STATUS: APPROVED
```

then:

1. Confirm every previous review item has been addressed.
2. Confirm all review notes are committed:

   ```bash
   scripts/orchestration/check-review-notes-committed logical-types-registry
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize logical-types-registry
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/logical-types-registry_finalized
   ```

6. Stop polling and exit cleanly.

---

## Review Rules

Do not write your own review.

Do not create files under:

```text
docs/review/
```

Do not delete files under:

```text
docs/review/
```

Only the orchestrator writes review notes. Your job is to read them, resolve them, commit them as audit records, and continue the loop.

---

## Finalization Rules

Only finalize after a review note with:

```text
STATUS: APPROVED
```

Finalization is performed with:

```bash
scripts/orchestration/finalize logical-types-registry
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/logical-types-registry_finished
/tmp/ibis-profiling/logical-types-registry_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
