"""
Type definitions for Promptfoo integration.

This module defines all the types, enums, and data structures used throughout
the Promptfoo integration.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class PluginCategory(str, Enum):
    """Categories of red team plugins."""
    BRAND = "brand"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    TRUST_SAFETY = "trust_safety"
    DATASET = "dataset"
    CUSTOM = "custom"


class PluginType(str, Enum):
    """Available red team plugins."""
    # Security & Access Control
    SQL_INJECTION = "sql-injection"
    SHELL_INJECTION = "shell-injection"
    PROMPT_INJECTION = "prompt-injection"
    SSRF = "ssrf"
    BROKEN_ACCESS_CONTROL = "broken-access-control"
    DEBUG_ACCESS = "debug-access"
    RBAC = "rbac"

    # Brand
    COMPETITORS = "competitors"
    HALLUCINATION = "hallucination"
    MISINFORMATION = "misinformation"
    POLITICS = "politics"

    # Trust & Safety
    HARMFUL_CONTENT = "harmful-content"
    HARMFUL_PRIVACY = "harmful-privacy"
    HARMFUL_HATE = "harmful-hate"
    HARMFUL_VIOLENT_CRIME = "harmful-violent-crime"
    HARMFUL_SPECIALIZED_ADVICE = "harmful-specialized-advice"

    # Compliance & Legal
    CONTRACTS = "contracts"
    EXCESSIVE_AGENCY = "excessive-agency"
    IMITATION = "imitation"
    INTELLECTUAL_PROPERTY = "intellectual-property"

    # Dataset
    PII = "pii"
    OVERRELIANCE = "overreliance"


class StrategyType(str, Enum):
    """Available red team attack strategies."""
    JAILBREAK = "jailbreak"
    PROMPT_INJECTION = "prompt-injection"
    ROT13 = "rot13"
    BASE64 = "base64"
    LEETSPEAK = "leetspeak"
    CRESCENDO = "crescendo"
    MULTILINGUAL = "multilingual"
    MATH_PROMPT = "math-prompt"
    CITATION = "citation"


class CompliancePreset(str, Enum):
    """Pre-configured compliance frameworks."""
    OWASP_LLM_TOP_10 = "owasp-llm-top-10"
    OWASP_API_TOP_10 = "owasp-api-top-10"
    NIST_AI_RMF = "nist-ai-rmf"
    MITRE_ATLAS = "mitre-atlas"
    EU_AI_ACT = "eu-ai-act"


class SeverityLevel(str, Enum):
    """Severity levels for test results."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class TestStatus(str, Enum):
    """Status of a test case."""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestCase(BaseModel):
    """Represents a single test case."""
    id: str = Field(description="Unique identifier for the test case")
    plugin: str = Field(description="Plugin that generated this test")
    strategy: Optional[str] = Field(None, description="Strategy used to deliver the test")
    input: str = Field(description="Input prompt/payload for the test")
    expected_behavior: str = Field(description="Expected safe behavior")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TestResult(BaseModel):
    """Result of a single test execution."""
    test_case_id: str
    status: TestStatus
    actual_output: str
    is_vulnerable: bool
    severity: SeverityLevel
    explanation: str
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RedTeamResult(BaseModel):
    """Aggregated results from a red team assessment."""
    run_id: str
    target_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    vulnerabilities_found: int = 0
    attack_success_rate: float = 0.0
    test_results: List[TestResult] = Field(default_factory=list)
    plugins_used: List[str] = Field(default_factory=list)
    strategies_used: List[str] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)

    def calculate_metrics(self):
        """Calculate summary metrics from test results."""
        self.total_tests = len(self.test_results)
        self.passed_tests = sum(1 for r in self.test_results if r.status == TestStatus.PASSED)
        self.failed_tests = sum(1 for r in self.test_results if r.status == TestStatus.FAILED)
        self.error_tests = sum(1 for r in self.test_results if r.status == TestStatus.ERROR)
        self.vulnerabilities_found = sum(1 for r in self.test_results if r.is_vulnerable)

        if self.total_tests > 0:
            self.attack_success_rate = (self.vulnerabilities_found / self.total_tests) * 100


class TargetConfig(BaseModel):
    """Configuration for a target LLM application."""
    name: str = Field(description="Name of the target")
    type: str = Field(description="Type of target (e.g., 'api', 'langchain', 'custom')")
    endpoint: Optional[str] = Field(None, description="API endpoint if applicable")
    model: Optional[str] = Field(None, description="Model name if applicable")
    config: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration")


class PluginConfig(BaseModel):
    """Configuration for a specific plugin."""
    plugin: Union[PluginType, str]
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)


class StrategyConfig(BaseModel):
    """Configuration for a specific strategy."""
    strategy: Union[StrategyType, str]
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
