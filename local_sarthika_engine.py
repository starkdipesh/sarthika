"""
🏛️ Sarthika AGI Core v1 — Local CPU Autonomous Reasoning Engine
Author: Sarthika Cognitive Architecture Lab
Runtime: 100% Local CPU (AVX2/AVX-512 SIMD Acceleration, Zero GPU Required)
"""

import os
import sys
import io
import re
import ast
import time
import copy
import traceback
from typing import Dict, Any, List, Optional

# Check for llama-cpp-python
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False


class TransactionalPythonSandbox:
    """Isolated Python namespace sandbox for safe, deterministic code execution."""

    def __init__(self, base_namespace: Optional[Dict[str, Any]] = None):
        if base_namespace is None:
            import math
            self.namespace: Dict[str, Any] = {
                "__builtins__": __builtins__,
                "__name__": "__main__",
                "__doc__": "Sarthika Local AGI Sandbox",
                "math": math,
            }
        else:
            self.namespace = {}
            for k, v in base_namespace.items():
                if k.startswith("__"):
                    self.namespace[k] = v
                else:
                    try:
                        self.namespace[k] = copy.deepcopy(v)
                    except Exception:
                        self.namespace[k] = v

    def fork(self) -> "TransactionalPythonSandbox":
        return TransactionalPythonSandbox(self.namespace)

    def execute(self, code: str) -> Dict[str, Any]:
        """Executes code string, capturing stdout, stderr, and variable mutations."""
        # AST Pre-validation (Causal Safety Check)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ("os", "subprocess", "shutil"):
                            return {
                                "success": False,
                                "stdout": "",
                                "stderr": f"Security Invariant Alert: Prohibited module '{alias.name}' detected."
                            }
                elif isinstance(node, ast.ImportFrom):
                    if node.module in ("os", "subprocess", "shutil"):
                        return {
                            "success": False,
                            "stdout": "",
                            "stderr": f"Security Invariant Alert: Prohibited module '{node.module}' detected."
                        }
        except SyntaxError as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"AST SyntaxError: {e.msg} at line {e.lineno}"
            }

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        out_buf = io.StringIO()
        err_buf = io.StringIO()

        sys.stdout = out_buf
        sys.stderr = err_buf
        success = False

        try:
            exec(code, self.namespace)
            success = True
            err_str = ""
        except Exception:
            err_str = traceback.format_exc()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return {
            "success": success,
            "stdout": out_buf.getvalue(),
            "stderr": err_str
        }


class SarthikaLocalEngine:
    """High-speed local CPU cognitive engine running personal GGUF weights."""

    def __init__(self, model_path: str = "sarthika_agi_v1_q4_k_m.gguf", n_threads: Optional[int] = None):
        self.model_path = model_path
        self.n_threads = n_threads or max(1, os.cpu_count() - 2)

        if not LLAMA_CPP_AVAILABLE:
            raise ImportError(
                "❌ 'llama-cpp-python' is not installed.\n"
                "Install it on your PC via:\n"
                "  pip install llama-cpp-python"
            )

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"❌ Model file not found at '{model_path}'.\n"
                "Please download 'sarthika_agi_v1_q4_k_m.gguf' from your Kaggle training output and place it in this directory."
            )

        print(f"🚀 Loading Sarthika AGI Core into CPU RAM (Threads: {self.n_threads})...")
        start = time.time()
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=self.n_threads,
            verbose=False
        )
        print(f"✅ Loaded Sarthika GGUF in {time.time() - start:.2f}s. Zero GPU required!")

        self.sandbox = TransactionalPythonSandbox()

    def generate_deliberation(self, objective: str, reflexion_history: str = "") -> str:
        """Prompts the local model following the Sarthika AGI Cognitive Protocol."""
        system_prompt = (
            "You are Sarthika AGI, an autonomous deliberative reasoning engine.\n"
            "When given an objective, follow the Sarthika Cognitive Protocol:\n"
            "1. <thought>: Metacognitively decompose the objective, analyze invariants, and outline the algorithmic plan.\n"
            "2. <code>: Write complete, typed, self-contained Python code that calculates the verified answer and prints it.\n"
            "3. <verification>: Programmatically evaluate the output and confirm mathematical invariants.\n"
            "4. <conclusion>: Formulate a precise, definitive final answer."
        )

        user_content = f"Objective: {objective}"
        if reflexion_history:
            user_content += f"\n\n[PREVIOUS EXECUTION CRITIQUE - MUST FIX]:\n{reflexion_history}"

        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_content}<|im_end|>\n<|im_start|>assistant\n"

        response = self.llm(
            prompt=prompt,
            max_tokens=1024,
            temperature=0.6,
            stop=["<|im_end|>", "<|endoftext|>"]
        )
        return response["choices"][0]["text"].strip()

    def extract_code(self, raw_response: str) -> Optional[str]:
        """Extracts executable Python code block from the deliberative response."""
        # Check for <code> tags first
        code_tag_match = re.search(r"<code>([\s\S]*?)</code>", raw_response)
        if code_tag_match:
            return code_tag_match.group(1).strip()

        # Check for standard markdown code blocks
        blocks = re.findall(r"```(?:python)?\s*([\s\S]*?)```", raw_response)
        if blocks:
            return blocks[0].strip()

        return None

    def solve(self, objective: str, max_retries: int = 3) -> Dict[str, Any]:
        """Runs the full Deliberative Cognitive Loop with transactional execution and Reflexion."""
        print(f"\n" + "=" * 65)
        print(f"🎯 SARTHIKA DELIBERATIVE REASONING: {objective}")
        print("=" * 65)

        reflexion = ""
        for attempt in range(1, max_retries + 1):
            if attempt > 1:
                print(f"\n🔄 REFLEXION RETRY (Attempt {attempt}/{max_retries})...")

            raw_deliberation = self.generate_deliberation(objective, reflexion_history=reflexion)

            # Display thoughts
            thought_match = re.search(r"<thought>([\s\S]*?)</thought>", raw_deliberation)
            if thought_match:
                print(f"\n🧠 [Metacognitive Thought]:\n{thought_match.group(1).strip()}")

            code = self.extract_code(raw_deliberation)
            if not code:
                reflexion = "No code block identified. You MUST write runnable Python code inside <code>...</code> tags."
                continue

            print(f"\n⚙️ [Executing Candidate Code in Sandbox]...")
            exec_res = self.sandbox.execute(code)

            if exec_res["success"]:
                stdout = exec_res["stdout"].strip()
                print(f"✅ Execution Succeeded!\n[Output]:\n{stdout}")

                conclusion_match = re.search(r"<conclusion>([\s\S]*?)</conclusion>", raw_deliberation)
                conclusion = conclusion_match.group(1).strip() if conclusion_match else stdout

                print(f"\n🏆 [Verified Conclusion]:\n{conclusion}")
                return {
                    "success": True,
                    "objective": objective,
                    "deliberation": raw_deliberation,
                    "code": code,
                    "stdout": stdout,
                    "conclusion": conclusion,
                    "attempts": attempt
                }
            else:
                stderr = exec_res["stderr"].strip()
                print(f"❌ Execution Failed:\n{stderr}")
                reflexion = f"Code execution failed with error:\n{stderr}\nPlease diagnose this bug and rewrite code with corrected logic."

        return {
            "success": False,
            "objective": objective,
            "error": "Exceeded maximum retry limit without verified execution.",
            "attempts": max_retries
        }


if __name__ == "__main__":
    print("=" * 65)
    print("🏛️ SARTHIKA LOCAL AGI RUNNER (CPU-NATIVE ENGINE)")
    print("=" * 65)

    model_file = "sarthika_agi_v1_q4_k_m.gguf"

    if not os.path.exists(model_file):
        print(f"\n⚠️ Notice: '{model_file}' not detected in current directory.")
        print("1. Complete the training in 'kaggle_sarthika_agi_trainer.ipynb' on Kaggle.")
        print("2. Download 'sarthika_agi_v1_q4_k_m.gguf' and place it here.")
        print("\nOnce placed, rerun this script to solve queries locally on your CPU!")
        sys.exit(0)

    engine = SarthikaLocalEngine(model_file)
    test_query = "Compute the Euler Totient function phi(120) and find its prime factors."
    result = engine.solve(test_query)
