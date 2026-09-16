Title: "🧪 Add test coverage for unificar_v10._free_port_5173"
Description:
🎯 **What:** This PR addresses a testing gap by adding unit tests for the `_free_port_5173` function in `unificar_v10.py`, which had no previous test coverage.
📊 **Coverage:** The new tests in `tests/test_unificar_v10.py` cover three core scenarios: MacOS (Darwin), Linux, and Windows (NT). We successfully mock `sys.platform`, `os.name`, and `subprocess.run` to ensure the correct bash and powershell commands are constructed and executed respectively across these platforms without side effects.
✨ **Result:** Test coverage improved by ensuring regressions in the port termination logic can be caught natively.
