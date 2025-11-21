#!/usr/bin/env python3
"""
Guardrails Middleware for LLM Applications

This middleware provides runtime protection for LLM applications by:
1. Filtering malicious inputs (prompt injection, jailbreaks)
2. Detecting PII in inputs and outputs
3. Blocking harmful content
4. Logging all guardrail events

Usage:
    from guardrails.middleware.guardrails_middleware import GuardrailsMiddleware

    guardrails = GuardrailsMiddleware()

    # Check input before sending to LLM
    result = guardrails.check_input(user_input)
    if result.blocked:
        return result.message

    # Check output before returning to user
    result = guardrails.check_output(llm_response)
    if result.blocked:
        return result.safe_response
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import os


class GuardrailType(Enum):
    """Types of guardrails available"""
    PII_DETECTION = "pii_detection"
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK_DETECTION = "jailbreak_detection"
    TOXIC_CONTENT = "toxic_content"
    COMPETITOR_MENTION = "competitor_mention"
    CONFIDENTIAL_INFO = "confidential_info"
    SQL_INJECTION = "sql_injection"
    CODE_INJECTION = "code_injection"


class Action(Enum):
    """Actions to take when guardrail triggers"""
    BLOCK = "block"
    WARN = "warn"
    LOG = "log"
    REDACT = "redact"
    ALLOW = "allow"


@dataclass
class GuardrailResult:
    """Result of a guardrail check"""
    passed: bool
    blocked: bool
    guardrail_type: Optional[str] = None
    action: str = "allow"
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    safe_response: Optional[str] = None
    original_input: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class GuardrailConfig:
    """Configuration for guardrails"""
    enabled: bool = True
    pii_detection: bool = True
    prompt_injection: bool = True
    jailbreak_detection: bool = True
    toxic_content: bool = True
    competitor_mention: bool = False
    confidential_info: bool = True
    sql_injection: bool = True
    code_injection: bool = True
    action_on_trigger: Action = Action.BLOCK
    log_events: bool = True
    log_path: str = "./guardrails/logs/guardrails.log"
    competitors: List[str] = field(default_factory=list)
    confidential_patterns: List[str] = field(default_factory=list)


class GuardrailsMiddleware:
    """
    Main guardrails middleware class.

    Provides input/output filtering for LLM applications.
    """

    def __init__(self, config: Optional[GuardrailConfig] = None):
        """Initialize guardrails with configuration"""
        self.config = config or GuardrailConfig()
        self._setup_logging()
        self._compile_patterns()

    def _setup_logging(self):
        """Setup logging for guardrail events"""
        if self.config.log_events:
            os.makedirs(os.path.dirname(self.config.log_path), exist_ok=True)
            logging.basicConfig(
                filename=self.config.log_path,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger("guardrails")
        else:
            self.logger = None

    def _compile_patterns(self):
        """Compile regex patterns for detection"""

        # PII Patterns
        self.pii_patterns = {
            "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            "ssn": r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "api_key": r"\b(?:api[_-]?key|apikey|token)[=:\s]+['\"]?[\w-]{20,}['\"]?\b",
        }

        # Prompt Injection Patterns
        self.injection_patterns = [
            r"ignore\s+(?:all\s+)?(?:previous|above|prior)\s+instructions?",
            r"disregard\s+(?:all\s+)?(?:previous|above|prior)\s+instructions?",
            r"forget\s+(?:all\s+)?(?:previous|above|prior)\s+instructions?",
            r"you\s+are\s+now\s+(?:a|an|in)\s+(?:new|different)",
            r"new\s+instructions?[:\s]",
            r"system\s*:\s*you\s+are",
            r"<\s*system\s*>",
            r"\[\s*system\s*\]",
            r"act\s+as\s+(?:if\s+)?(?:you\s+(?:are|were)|a)",
            r"pretend\s+(?:to\s+be|you\s+are)",
            r"roleplay\s+as",
            r"switch\s+to\s+(?:a\s+)?(?:new\s+)?(?:role|mode|persona)",
        ]

        # Jailbreak Patterns
        self.jailbreak_patterns = [
            r"DAN\s+mode",
            r"Developer\s+Mode",
            r"jailbreak",
            r"bypass\s+(?:your\s+)?(?:safety|security|restrictions?|filters?)",
            r"ignore\s+(?:your\s+)?(?:safety|security|ethical)\s+(?:guidelines?|rules?)",
            r"hypothetically",
            r"for\s+educational\s+purposes?",
            r"in\s+a\s+(?:fictional|hypothetical)\s+(?:scenario|world)",
            r"pretend\s+there\s+are\s+no\s+(?:rules?|restrictions?)",
            r"without\s+(?:any\s+)?(?:moral|ethical)\s+(?:constraints?|limits?)",
        ]

        # Toxic Content Patterns
        self.toxic_patterns = [
            r"\b(?:kill|murder|harm|hurt|attack)\s+(?:yourself|himself|herself|themselves|someone|people)\b",
            r"\b(?:bomb|explosive|weapon)\s+(?:making|instructions?|how\s+to)\b",
            r"\bhow\s+to\s+(?:hack|steal|exploit)\b",
        ]

        # SQL Injection Patterns
        self.sql_patterns = [
            r"(?:--|#|/\*)\s*$",
            r"\b(?:UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b.*\b(?:FROM|INTO|TABLE|DATABASE)\b",
            r"'\s*(?:OR|AND)\s*'?\d*'?\s*=\s*'?\d*",
            r";\s*(?:DROP|DELETE|UPDATE|INSERT)",
        ]

        # Code Injection Patterns
        self.code_patterns = [
            r"(?:exec|eval|system|os\.system|subprocess|__import__)\s*\(",
            r"<\s*script[^>]*>",
            r"\$\{.*\}",
            r"`[^`]+`",
        ]

    def check_input(self, text: str) -> GuardrailResult:
        """
        Check user input against all enabled guardrails.

        Args:
            text: User input text

        Returns:
            GuardrailResult with pass/block decision
        """
        if not self.config.enabled:
            return GuardrailResult(passed=True, blocked=False, action="allow")

        checks = []

        # Run all enabled checks
        if self.config.pii_detection:
            checks.append(self._check_pii(text, "input"))

        if self.config.prompt_injection:
            checks.append(self._check_prompt_injection(text))

        if self.config.jailbreak_detection:
            checks.append(self._check_jailbreak(text))

        if self.config.toxic_content:
            checks.append(self._check_toxic_content(text))

        if self.config.sql_injection:
            checks.append(self._check_sql_injection(text))

        if self.config.code_injection:
            checks.append(self._check_code_injection(text))

        if self.config.competitor_mention and self.config.competitors:
            checks.append(self._check_competitor_mention(text))

        # Aggregate results
        for result in checks:
            if result.blocked:
                result.original_input = text
                self._log_event(result)
                return result

        return GuardrailResult(
            passed=True,
            blocked=False,
            action="allow",
            message="Input passed all guardrails"
        )

    def check_output(self, text: str) -> GuardrailResult:
        """
        Check LLM output against output guardrails.

        Args:
            text: LLM output text

        Returns:
            GuardrailResult with pass/block/redact decision
        """
        if not self.config.enabled:
            return GuardrailResult(passed=True, blocked=False, action="allow")

        checks = []

        # Check for PII in output
        if self.config.pii_detection:
            checks.append(self._check_pii(text, "output"))

        # Check for toxic content in output
        if self.config.toxic_content:
            checks.append(self._check_toxic_content(text))

        # Check for confidential info
        if self.config.confidential_info:
            checks.append(self._check_confidential_info(text))

        # Check for competitor mentions
        if self.config.competitor_mention and self.config.competitors:
            checks.append(self._check_competitor_mention(text))

        # Aggregate results
        for result in checks:
            if result.blocked:
                result.original_input = text
                result.safe_response = self._generate_safe_response(result)
                self._log_event(result)
                return result

        return GuardrailResult(
            passed=True,
            blocked=False,
            action="allow",
            message="Output passed all guardrails"
        )

    def _check_pii(self, text: str, direction: str) -> GuardrailResult:
        """Check for PII in text"""
        detected_pii = {}

        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected_pii[pii_type] = matches

        if detected_pii:
            return GuardrailResult(
                passed=False,
                blocked=self.config.action_on_trigger == Action.BLOCK,
                guardrail_type=GuardrailType.PII_DETECTION.value,
                action=self.config.action_on_trigger.value,
                message=f"PII detected in {direction}: {list(detected_pii.keys())}",
                details={"pii_types": list(detected_pii.keys()), "direction": direction}
            )

        return GuardrailResult(passed=True, blocked=False)

    def _check_prompt_injection(self, text: str) -> GuardrailResult:
        """Check for prompt injection attempts"""
        text_lower = text.lower()

        for pattern in self.injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    blocked=self.config.action_on_trigger == Action.BLOCK,
                    guardrail_type=GuardrailType.PROMPT_INJECTION.value,
                    action=self.config.action_on_trigger.value,
                    message="Potential prompt injection detected",
                    details={"pattern_matched": pattern}
                )

        return GuardrailResult(passed=True, blocked=False)

    def _check_jailbreak(self, text: str) -> GuardrailResult:
        """Check for jailbreak attempts"""
        text_lower = text.lower()

        for pattern in self.jailbreak_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    blocked=self.config.action_on_trigger == Action.BLOCK,
                    guardrail_type=GuardrailType.JAILBREAK_DETECTION.value,
                    action=self.config.action_on_trigger.value,
                    message="Potential jailbreak attempt detected",
                    details={"pattern_matched": pattern}
                )

        return GuardrailResult(passed=True, blocked=False)

    def _check_toxic_content(self, text: str) -> GuardrailResult:
        """Check for toxic/harmful content"""
        text_lower = text.lower()

        for pattern in self.toxic_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    blocked=self.config.action_on_trigger == Action.BLOCK,
                    guardrail_type=GuardrailType.TOXIC_CONTENT.value,
                    action=self.config.action_on_trigger.value,
                    message="Potentially harmful content detected",
                    details={"pattern_matched": pattern}
                )

        return GuardrailResult(passed=True, blocked=False)

    def _check_sql_injection(self, text: str) -> GuardrailResult:
        """Check for SQL injection attempts"""
        for pattern in self.sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    blocked=self.config.action_on_trigger == Action.BLOCK,
                    guardrail_type=GuardrailType.SQL_INJECTION.value,
                    action=self.config.action_on_trigger.value,
                    message="Potential SQL injection detected",
                    details={"pattern_matched": pattern}
                )

        return GuardrailResult(passed=True, blocked=False)

    def _check_code_injection(self, text: str) -> GuardrailResult:
        """Check for code injection attempts"""
        for pattern in self.code_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    blocked=self.config.action_on_trigger == Action.BLOCK,
                    guardrail_type=GuardrailType.CODE_INJECTION.value,
                    action=self.config.action_on_trigger.value,
                    message="Potential code injection detected",
                    details={"pattern_matched": pattern}
                )

        return GuardrailResult(passed=True, blocked=False)

    def _check_competitor_mention(self, text: str) -> GuardrailResult:
        """Check for competitor mentions"""
        text_lower = text.lower()
        mentioned = []

        for competitor in self.config.competitors:
            if competitor.lower() in text_lower:
                mentioned.append(competitor)

        if mentioned:
            return GuardrailResult(
                passed=False,
                blocked=self.config.action_on_trigger == Action.BLOCK,
                guardrail_type=GuardrailType.COMPETITOR_MENTION.value,
                action=self.config.action_on_trigger.value,
                message=f"Competitor mention detected: {mentioned}",
                details={"competitors_mentioned": mentioned}
            )

        return GuardrailResult(passed=True, blocked=False)

    def _check_confidential_info(self, text: str) -> GuardrailResult:
        """Check for confidential information patterns"""
        for pattern in self.config.confidential_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    blocked=self.config.action_on_trigger == Action.BLOCK,
                    guardrail_type=GuardrailType.CONFIDENTIAL_INFO.value,
                    action=self.config.action_on_trigger.value,
                    message="Confidential information pattern detected",
                    details={"pattern_matched": pattern}
                )

        return GuardrailResult(passed=True, blocked=False)

    def _generate_safe_response(self, result: GuardrailResult) -> str:
        """Generate a safe response when output is blocked"""
        responses = {
            GuardrailType.PII_DETECTION.value: "I cannot share personal information. Please ask about something else.",
            GuardrailType.TOXIC_CONTENT.value: "I cannot provide that type of content. Please ask about something else.",
            GuardrailType.COMPETITOR_MENTION.value: "I cannot provide information about competitors.",
            GuardrailType.CONFIDENTIAL_INFO.value: "I cannot share confidential information.",
        }
        return responses.get(result.guardrail_type, "I cannot provide that information.")

    def _log_event(self, result: GuardrailResult):
        """Log guardrail event"""
        if self.logger:
            self.logger.warning(
                f"GUARDRAIL_TRIGGERED | Type: {result.guardrail_type} | "
                f"Action: {result.action} | Message: {result.message} | "
                f"Details: {json.dumps(result.details)}"
            )

    def redact_pii(self, text: str) -> str:
        """Redact PII from text"""
        redacted = text
        for pii_type, pattern in self.pii_patterns.items():
            redacted = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", redacted, flags=re.IGNORECASE)
        return redacted


# Convenience function for quick usage
def create_guardrails(config_path: Optional[str] = None) -> GuardrailsMiddleware:
    """
    Create guardrails middleware from config file or defaults.

    Args:
        config_path: Path to YAML config file (optional)

    Returns:
        GuardrailsMiddleware instance
    """
    if config_path:
        import yaml
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)

        config = GuardrailConfig(
            enabled=config_dict.get('enabled', True),
            pii_detection=config_dict.get('pii_detection', True),
            prompt_injection=config_dict.get('prompt_injection', True),
            jailbreak_detection=config_dict.get('jailbreak_detection', True),
            toxic_content=config_dict.get('toxic_content', True),
            competitor_mention=config_dict.get('competitor_mention', False),
            confidential_info=config_dict.get('confidential_info', True),
            sql_injection=config_dict.get('sql_injection', True),
            code_injection=config_dict.get('code_injection', True),
            action_on_trigger=Action(config_dict.get('action_on_trigger', 'block')),
            log_events=config_dict.get('log_events', True),
            log_path=config_dict.get('log_path', './guardrails/logs/guardrails.log'),
            competitors=config_dict.get('competitors', []),
            confidential_patterns=config_dict.get('confidential_patterns', []),
        )
        return GuardrailsMiddleware(config)

    return GuardrailsMiddleware()
