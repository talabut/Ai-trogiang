# FILE: tests/test_sandbox_enforcement.py
import unittest
import sys
import os

# 1. Simulate the application entry point logic to trigger the guard
sys.path.append(os.getcwd())
try:
    import backend.security.guard as guard
    from backend.security.guard import RuntimeSandboxError
    print("✅ Sandbox module loaded.")
except ImportError:
    print("❌ Failed to load sandbox module. Check python path.")
    sys.exit(1)

class TestRuntimeSandbox(unittest.TestCase):
    
    def test_01_eval_is_dead(self):
        """Prove that eval() is completely disabled."""
        print("\n--- 🧪 Testing eval() Block ---")
        try:
            eval("1 + 1")
            self.fail("❌ FAIL: eval() was NOT blocked! RCE is possible.")
        except RuntimeSandboxError:
            print("✅ PASS: eval() correctly raised RuntimeSandboxError.")
        except Exception as e:
            self.fail(f"❌ FAIL: Unexpected exception type: {type(e)}")

    def test_02_os_system_is_dead(self):
        """Prove that os.system() is disabled."""
        print("\n--- 🧪 Testing os.system() Block ---")
        try:
            os.system("ls")
            self.fail("❌ FAIL: os.system() was NOT blocked! RCE is possible.")
        except RuntimeSandboxError:
            print("✅ PASS: os.system() correctly raised RuntimeSandboxError.")

    def test_03_subprocess_is_dead(self):
        """Prove that subprocess execution is disabled."""
        print("\n--- 🧪 Testing subprocess Block ---")
        import subprocess
        try:
            subprocess.run(["ls"], check=True)
            self.fail("❌ FAIL: subprocess.run() was NOT blocked!")
        except RuntimeSandboxError:
            print("✅ PASS: subprocess.run() correctly raised RuntimeSandboxError.")

    def test_04_filesystem_write_isolation(self):
        """Prove that writing to unauthorized paths is blocked."""
        print("\n--- 🧪 Testing Filesystem Isolation ---")
        # Attempt to write to project root (forbidden)
        forbidden_file = "root_hack.txt"
        try:
            with open(forbidden_file, "w") as f:
                f.write("I should not be able to do this")
            
            # If we get here, cleanup and fail
            os.remove(forbidden_file)
            self.fail(f"❌ FAIL: Write to {forbidden_file} (Root) was NOT blocked!")
            
        except RuntimeSandboxError:
            print(f"✅ PASS: Write to {forbidden_file} blocked.")
        except Exception as e:
             # Depending on implementation details, it might raise RuntimeSandboxError 
             # or a standard PermissionError wrapped. Ideally RuntimeSandboxError.
             if "Runtime sandbox violation" in str(e):
                 print(f"✅ PASS: Write blocked with message: {e}")
             else:
                 self.fail(f"❌ FAIL: Unexpected error: {e}")

    def test_05_allowed_write(self):
        """Prove that writing to authorized paths (data/) works."""
        print("\n--- 🧪 Testing Allowed Write Access ---")
        # Ensure path exists as per project structure
        target_dir = os.path.abspath("backend/data")
        os.makedirs(target_dir, exist_ok=True)
        
        allowed_file = os.path.join(target_dir, "test_safe.txt")
        try:
            with open(allowed_file, "w") as f:
                f.write("Safe content")
            print(f"✅ PASS: Write to {allowed_file} allowed.")
            os.remove(allowed_file)
        except RuntimeSandboxError:
            self.fail(f"❌ FAIL: Legitimate write to {allowed_file} was BLOCKED!")

if __name__ == "__main__":
    unittest.main()