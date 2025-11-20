"""
Configuration management for Promptfoo integration.

This module handles all configuration aspects including loading from files,
environment variables, and programmatic configuration.
"""

import os
import json
import yaml
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field, field_validator

from promptfoo_integration.core.types import (
    PluginType,
    StrategyType,
    CompliancePreset,
    TargetConfig,
    PluginConfig,
    StrategyConfig,
)


class PromptfooConfig(BaseModel):
    """
    Main configuration class for Promptfoo integration.

    This class provides a flexible configuration system that can be loaded from:
    - YAML/JSON files
    - Environment variables
    - Programmatic Python dictionaries

    Attributes:
        purpose: Description of the system's purpose for guiding red team tests
        target: Configuration for the target LLM application
        plugins: List of plugins to use for testing
        strategies: List of strategies to apply
        compliance_preset: Optional compliance framework preset
        num_tests: Number of test cases to generate per plugin
        grader_model: Model to use for grading responses (default: gpt-4.1-2025-04-14)
        api_key: API key for the grader model
        output_dir: Directory for test results and reports
        custom_config: Additional custom configuration
    """

    purpose: str = Field(
        description="System purpose to guide test generation",
        default="A RAG-based question answering system"
    )
    target: TargetConfig = Field(description="Target application configuration")
    plugins: List[Union[PluginType, str, PluginConfig]] = Field(
        default_factory=list,
        description="Plugins to use for red team testing"
    )
    strategies: List[Union[StrategyType, str, StrategyConfig]] = Field(
        default_factory=list,
        description="Strategies to apply during testing"
    )
    compliance_preset: Optional[CompliancePreset] = Field(
        None,
        description="Pre-configured compliance framework"
    )
    num_tests: int = Field(
        default=10,
        description="Number of test cases per plugin",
        ge=1
    )
    grader_model: str = Field(
        default="gpt-4",
        description="Model for grading responses"
    )
    api_key: Optional[str] = Field(
        None,
        description="API key for grader model"
    )
    base_url: Optional[str] = Field(
        None,
        description="Base URL for API if using custom endpoint"
    )
    output_dir: str = Field(
        default="./promptfoo_results",
        description="Output directory for results"
    )
    custom_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom configuration"
    )

    @field_validator('api_key', mode='before')
    @classmethod
    def get_api_key_from_env(cls, v):
        """Get API key from environment if not provided."""
        if v is None:
            return os.getenv("OPENAI_API_KEY") or os.getenv("RAG_OPENAI_API_KEY")
        return v

    @classmethod
    def from_yaml(cls, file_path: Union[str, Path]) -> "PromptfooConfig":
        """
        Load configuration from a YAML file.

        Args:
            file_path: Path to YAML configuration file

        Returns:
            PromptfooConfig instance

        Example:
            >>> config = PromptfooConfig.from_yaml("config.yaml")
        """
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_json(cls, file_path: Union[str, Path]) -> "PromptfooConfig":
        """
        Load configuration from a JSON file.

        Args:
            file_path: Path to JSON configuration file

        Returns:
            PromptfooConfig instance

        Example:
            >>> config = PromptfooConfig.from_json("config.json")
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptfooConfig":
        """
        Create configuration from a dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            PromptfooConfig instance

        Example:
            >>> config = PromptfooConfig.from_dict({
            ...     "purpose": "Testing RAG system",
            ...     "target": {...},
            ...     "plugins": [...]
            ... })
        """
        return cls(**data)

    @classmethod
    def with_compliance_preset(
        cls,
        preset: CompliancePreset,
        target: TargetConfig,
        **kwargs
    ) -> "PromptfooConfig":
        """
        Create configuration using a compliance preset.

        Args:
            preset: Compliance framework preset
            target: Target configuration
            **kwargs: Additional configuration options

        Returns:
            PromptfooConfig with preset plugins and strategies

        Example:
            >>> config = PromptfooConfig.with_compliance_preset(
            ...     CompliancePreset.OWASP_LLM_TOP_10,
            ...     target=my_target
            ... )
        """
        plugins = cls._get_preset_plugins(preset)
        strategies = cls._get_preset_strategies(preset)

        return cls(
            target=target,
            plugins=plugins,
            strategies=strategies,
            compliance_preset=preset,
            **kwargs
        )

    @staticmethod
    def _get_preset_plugins(preset: CompliancePreset) -> List[PluginType]:
        """Get plugins for a specific compliance preset."""
        preset_mappings = {
            CompliancePreset.OWASP_LLM_TOP_10: [
                PluginType.PROMPT_INJECTION,
                PluginType.BROKEN_ACCESS_CONTROL,
                PluginType.PII,
                PluginType.OVERRELIANCE,
                PluginType.EXCESSIVE_AGENCY,
                PluginType.HALLUCINATION,
            ],
            CompliancePreset.OWASP_API_TOP_10: [
                PluginType.BROKEN_ACCESS_CONTROL,
                PluginType.SQL_INJECTION,
                PluginType.SSRF,
                PluginType.RBAC,
            ],
            CompliancePreset.NIST_AI_RMF: [
                PluginType.HARMFUL_CONTENT,
                PluginType.MISINFORMATION,
                PluginType.PII,
                PluginType.HALLUCINATION,
            ],
            CompliancePreset.MITRE_ATLAS: [
                PluginType.PROMPT_INJECTION,
                PluginType.DEBUG_ACCESS,
                PluginType.HARMFUL_CONTENT,
            ],
            CompliancePreset.EU_AI_ACT: [
                PluginType.HARMFUL_CONTENT,
                PluginType.PII,
                PluginType.MISINFORMATION,
                PluginType.HARMFUL_HATE,
            ],
        }
        return preset_mappings.get(preset, [])

    @staticmethod
    def _get_preset_strategies(preset: CompliancePreset) -> List[StrategyType]:
        """Get strategies for a specific compliance preset."""
        # Common strategies for most presets
        return [
            StrategyType.JAILBREAK,
            StrategyType.PROMPT_INJECTION,
            StrategyType.BASE64,
        ]

    def to_yaml(self, file_path: Union[str, Path]) -> None:
        """
        Save configuration to a YAML file.

        Args:
            file_path: Path to save YAML file

        Example:
            >>> config.to_yaml("my_config.yaml")
        """
        with open(file_path, 'w') as f:
            yaml.dump(self.model_dump(mode='json'), f, default_flow_style=False)

    def to_json(self, file_path: Union[str, Path]) -> None:
        """
        Save configuration to a JSON file.

        Args:
            file_path: Path to save JSON file

        Example:
            >>> config.to_json("my_config.json")
        """
        with open(file_path, 'w') as f:
            json.dump(self.model_dump(mode='json'), f, indent=2)

    def ensure_output_dir(self) -> Path:
        """Ensure output directory exists and return Path object."""
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path

    def get_enabled_plugins(self) -> List[str]:
        """Get list of enabled plugin names."""
        enabled = []
        for plugin in self.plugins:
            if isinstance(plugin, PluginConfig):
                if plugin.enabled:
                    enabled.append(plugin.plugin)
            else:
                enabled.append(str(plugin))
        return enabled

    def get_enabled_strategies(self) -> List[str]:
        """Get list of enabled strategy names."""
        enabled = []
        for strategy in self.strategies:
            if isinstance(strategy, StrategyConfig):
                if strategy.enabled:
                    enabled.append(strategy.strategy)
            else:
                enabled.append(str(strategy))
        return enabled
