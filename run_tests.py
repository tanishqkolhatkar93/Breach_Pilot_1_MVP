"""
AgentShield AI - Fast Test Runner
Executes all unit and integration tests cleanly and outputs test results immediately.
"""

import sys
import os
import traceback

# Force unbuffered output and test mode
os.environ["PYTHONUNBUFFERED"] = "1"
os.environ["AGENTSHIELD_TEST_MODE"] = "1"

def run_all_tests():
    print("=" * 60, flush=True)
    print("AgentShield AI - Executing Test Suite", flush=True)
    print("=" * 60, flush=True)

    test_modules = [
        "tests.test_attacks",
        "tests.test_scoring",
        "tests.test_publishing",
        "tests.test_agent_loop",
        "tests.test_n8n_parser"
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for mod_name in test_modules:
        print(f"\n--- Running tests in {mod_name} ---", flush=True)
        try:
            __import__(mod_name)
            mod = sys.modules[mod_name]
            for attr_name in sorted(dir(mod)):
                if attr_name.startswith("test_"):
                    fn = getattr(mod, attr_name)
                    if callable(fn):
                        total_tests += 1
                        try:
                            fn()
                            print(f"  [PASS] {attr_name}", flush=True)
                            passed_tests += 1
                        except Exception as e:
                            print(f"  [FAIL] {attr_name}: {str(e)}", flush=True)
                            traceback.print_exc()
                            failed_tests += 1
        except Exception as e:
            print(f"  [ERROR] Failed to load module {mod_name}: {str(e)}", flush=True)
            traceback.print_exc()
            failed_tests += 1

    print("\n" + "=" * 60, flush=True)
    print(f"TEST RESULTS: Total: {total_tests} | Passed: {passed_tests} | Failed: {failed_tests}", flush=True)
    print("=" * 60, flush=True)

    if failed_tests > 0:
        sys.exit(1)
    else:
        print("ALL TESTS PASSED SUCCESSFULLY!", flush=True)
        sys.exit(0)

if __name__ == "__main__":
    run_all_tests()
