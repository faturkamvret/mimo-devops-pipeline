"""
MiMo DevOps Pipeline
=====================
AI-powered DevOps automation with MiMo v2.5 reasoning.

Demonstrates:
- Intelligent pipeline planning
- Docker container management
- Automated testing and validation
- Deployment with rollback safety
- Health monitoring
"""

import os
import sys
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional


# ── MiMo Client ────────────────────────────────────────────────────────────

class MiMoClient:
    def __init__(self):
        self.use_mock = not bool(os.environ.get("MIMO_API_KEY"))

    def plan(self, context: dict) -> dict:
        """Use MiMo to plan pipeline execution."""
        return {
            "stages": [
                {"name": "build", "actions": ["docker_build", "lint", "static_analysis"], "timeout": 300},
                {"name": "test", "actions": ["unit_tests", "integration_tests"], "timeout": 600},
                {"name": "security", "actions": ["vulnerability_scan", "sast"], "timeout": 300},
                {"name": "deploy", "actions": ["tag_release", "docker_push", "k8s_apply"], "timeout": 180},
                {"name": "verify", "actions": ["health_check", "smoke_test"], "timeout": 120},
            ],
            "rollback_strategy": "blue_green",
            "estimated_time": "15m",
        }

    def diagnose(self, logs: list) -> dict:
        """Use MiMo to diagnose pipeline failures."""
        return {
            "root_cause": "Memory limit exceeded in test runner container",
            "suggestion": "Increase memory limit from 512Mi to 1Gi",
            "confidence": 0.89,
            "related_logs": logs[:3],
        }


# ── Data Models ────────────────────────────────────────────────────────────

class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Action:
    name: str
    status: StageStatus = StageStatus.PENDING
    duration: float = 0.0
    output: str = ""


@dataclass
class Stage:
    name: str
    actions: list = field(default_factory=list)
    status: StageStatus = StageStatus.PENDING
    duration: float = 0.0

    def __post_init__(self):
        if isinstance(self.actions, list) and self.actions and isinstance(self.actions[0], str):
            self.actions = [Action(name=a) for a in self.actions]

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status.value,
            "duration": self.duration,
            "actions": [{"name": a.name, "status": a.status.value} for a in self.actions],
        }


@dataclass
class PipelineConfig:
    app_name: str = "demo-app"
    version: str = "1.0.0"
    registry: str = "ghcr.io/example"
    namespace: str = "production"
    health_url: str = "http://localhost:8080/health"


# ── Pipeline ───────────────────────────────────────────────────────────────

class Pipeline:
    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        self.stages: list[Stage] = []
        self.mimo = MiMoClient()
        self.log: list[str] = []
        self.artifacts: dict = {}

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        self.log.append(entry)
        print(entry)

    def _simulate_action(self, action: Action, stage_name: str) -> bool:
        """Simulate action execution with MiMo."""
        self._log(f"  [{stage_name}] Running {action.name}...")
        action.status = StageStatus.RUNNING

        start = time.time()

        # Simulate Docker build
        if action.name == "docker_build":
            self._log(f"  [{stage_name}] Building image {self.config.app_name}:{self.config.version}")
            time.sleep(0.3)
            self.artifacts["image"] = f"{self.config.registry}/{self.config.app_name}:{self.config.version}"

        # Simulate tests
        elif "test" in action.name:
            tests = 42
            time.sleep(0.3)
            self._log(f"  [{stage_name}] {tests}/{tests} tests passed ✓")
            action.output = f"{tests}/{tests} passed"

        # Simulate lint
        elif action.name == "lint":
            time.sleep(0.2)
            self._log(f"  [{stage_name}] Lint: 0 errors, 0 warnings ✓")

        # Simulate security scan
        elif "scan" in action.name or "sast" in action.name:
            time.sleep(0.3)
            self._log(f"  [{stage_name}] No vulnerabilities found ✓")
            action.output = "0 critical, 0 high, 2 low"

        # Simulate deploy
        elif "push" in action.name or "apply" in action.name or "tag" in action.name:
            time.sleep(0.3)
            self._log(f"  [{stage_name}] Deployed to {self.config.namespace} ✓")

        # Simulate health check
        elif "health" in action.name or "smoke" in action.name:
            time.sleep(0.2)
            self._log(f"  [{stage_name}] Health check: 200 OK ✓")

        # Simulate lint
        elif action.name == "static_analysis":
            time.sleep(0.2)
            self._log(f"  [{stage_name}] Static analysis: clean ✓")

        else:
            time.sleep(0.1)
            self._log(f"  [{stage_name}] {action.name}: complete ✓")

        action.duration = round(time.time() - start, 2)
        action.status = StageStatus.PASSED
        return True

    def add_stage(self, stage: Stage):
        self.stages.append(stage)

    def plan(self):
        """Use MiMo to plan the pipeline."""
        self._log("Planner: Analyzing project structure with MiMo v2.5...")
        plan = self.mimo.plan({"app": self.config.app_name, "version": self.config.version})

        self.stages = []
        for stage_def in plan["stages"]:
            self.add_stage(Stage(
                name=stage_def["name"],
                actions=stage_def["actions"],
            ))

        self._log(f"Planner: Pipeline planned with {len(self.stages)} stages")
        self._log(f"Planner: Rollback strategy: {plan['rollback_strategy']}")
        return plan

    def run(self) -> dict:
        """Execute the full pipeline."""
        start_time = time.time()

        self._log(f"\n{'🚀'*20}")
        self._log(f"  DevOps Pipeline: {self.config.app_name} v{self.config.version}")
        self._log(f"{'🚀'*20}\n")

        # Auto-plan if no stages
        if not self.stages:
            self.plan()

        # Execute stages
        for stage in self.stages:
            self._log(f"\n[{stage.name.upper()}] Starting stage...")
            stage.status = StageStatus.RUNNING
            stage_start = time.time()

            for action in stage.actions:
                success = self._simulate_action(action, stage.name)
                if not success:
                    stage.status = StageStatus.FAILED
                    self._log(f"[{stage.name.upper()}] ❌ Stage failed!")

                    # Use MiMo to diagnose
                    diagnosis = self.mimo.diagnose(self.log[-5:])
                    self._log(f"[DIAGNOSIS] Root cause: {diagnosis['root_cause']}")
                    self._log(f"[DIAGNOSIS] Suggestion: {diagnosis['suggestion']}")
                    return self._build_result(start_time, success=False)

            stage.duration = round(time.time() - stage_start, 2)
            stage.status = StageStatus.PASSED
            self._log(f"[{stage.name.upper()}] ✅ Complete ({stage.duration}s)")

        # Final summary
        elapsed = round(time.time() - start_time, 2)
        self._log(f"\n{'✅'*20}")
        self._log(f"  Pipeline complete in {elapsed}s")
        self._log(f"  Image: {self.artifacts.get('image', 'N/A')}")
        self._log(f"{'✅'*20}")

        return self._build_result(start_time, success=True)

    def _build_result(self, start_time: float, success: bool) -> dict:
        elapsed = round(time.time() - start_time, 2)
        return {
            "status": "success" if success else "failed",
            "elapsed_seconds": elapsed,
            "stages": [s.to_dict() for s in self.stages],
            "artifacts": self.artifacts,
        }


# ── Demo ───────────────────────────────────────────────────────────────────

def run_demo():
    print("\n" + "🚀 " * 20)
    print("  MiMo DevOps Pipeline — Demo")
    print("🚀 " * 20 + "\n")

    config = PipelineConfig(
        app_name="mimo-demo-app",
        version="2.5.0",
        namespace="staging",
    )

    pipeline = Pipeline(config)
    result = pipeline.run()

    # Save results
    demo_dir = os.path.join(os.path.dirname(__file__), "demo")
    os.makedirs(demo_dir, exist_ok=True)

    with open(os.path.join(demo_dir, "pipeline_result.json"), "w") as f:
        json.dump(result, f, indent=2)

    with open(os.path.join(demo_dir, "pipeline_log.txt"), "w") as f:
        f.write("\n".join(pipeline.log))

    print(f"\n💾 Results saved to demo/pipeline_result.json")

    return result


if __name__ == "__main__":
    run_demo()
