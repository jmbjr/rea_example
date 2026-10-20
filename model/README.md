# Flag slice model inputs

`flag-rules.dodge.json` is the authored reusable rules/composition source, not the assembled six-scenario candidate. It has no authored fixture boards. `evidence-lock.json` pins the historical native observations; changing these observations requires an explicit authority decision.

`tools/assemble_flags.py` derives six scene/scenario setups from the retained native fixtures and fills exact source hashes. `tools/build_flags.py` validates that actual assembled candidate and resolves it. Do not treat the source template alone as a G1–G4 result.

The two cell invocations bind their target explicitly. Their referenced actions select branch procedures. Every success branch sets the cell, adjusts the scenario counter, and sets an output result; rejection sets only the result. The result binding is an execution output, not recovered persistent native game state.

The [Python executor](../docs/PYTHON_FLAGS.md) consumes the validated resolved model. Optional `synthetic-setup.json` supplies a separately labeled authority perturbation; it does not replace the six immutable native fixtures.
