"""
Report generation for red team assessments.

This module provides comprehensive reporting capabilities including HTML, JSON,
and text-based reports with visualizations and analysis.
"""

import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from collections import Counter, defaultdict
from datetime import timedelta

from promptfoo_integration.core.types import RedTeamResult, SeverityLevel, TestStatus


class ReportGenerator:
    """
    Generates comprehensive reports from red team assessment results.

    Supports multiple output formats and provides detailed analysis of vulnerabilities.
    """

    def __init__(self, results: RedTeamResult):
        """
        Initialize report generator with results.

        Args:
            results: Red team assessment results

        Example:
            >>> generator = ReportGenerator(results)
            >>> generator.generate_html_report("report.html")
        """
        self.results = results

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the assessment results.

        Returns:
            Dictionary containing summary statistics

        Example:
            >>> summary = generator.generate_summary()
            >>> print(summary["vulnerabilities_by_severity"])
        """
        # Calculate statistics
        vulnerabilities_by_severity = Counter()
        vulnerabilities_by_plugin = defaultdict(int)
        vulnerabilities_by_strategy = defaultdict(int)

        for result in self.results.test_results:
            if result.is_vulnerable:
                vulnerabilities_by_severity[result.severity.value] += 1
                vulnerabilities_by_plugin[result.metadata.get("plugin", "unknown")] += 1
                if result.metadata.get("strategy"):
                    vulnerabilities_by_strategy[result.metadata["strategy"]] += 1

        duration = (
            (self.results.end_time - self.results.start_time).total_seconds()
            if self.results.end_time
            else 0
        )

        return {
            "run_id": self.results.run_id,
            "target": self.results.target_name,
            "start_time": self.results.start_time.isoformat(),
            "end_time": self.results.end_time.isoformat() if self.results.end_time else None,
            "duration_seconds": duration,
            "total_tests": self.results.total_tests,
            "passed_tests": self.results.passed_tests,
            "failed_tests": self.results.failed_tests,
            "error_tests": self.results.error_tests,
            "vulnerabilities_found": self.results.vulnerabilities_found,
            "attack_success_rate": self.results.attack_success_rate,
            "vulnerabilities_by_severity": dict(vulnerabilities_by_severity),
            "vulnerabilities_by_plugin": dict(vulnerabilities_by_plugin),
            "vulnerabilities_by_strategy": dict(vulnerabilities_by_strategy),
            "plugins_used": self.results.plugins_used,
            "strategies_used": self.results.strategies_used,
        }

    def generate_text_report(self) -> str:
        """
        Generate a text-based report.

        Returns:
            Formatted text report

        Example:
            >>> report = generator.generate_text_report()
            >>> print(report)
        """
        summary = self.generate_summary()

        report_lines = [
            "=" * 80,
            "RED TEAM ASSESSMENT REPORT",
            "=" * 80,
            "",
            f"Target: {summary['target']}",
            f"Run ID: {summary['run_id']}",
            f"Start Time: {summary['start_time']}",
            f"Duration: {summary['duration_seconds']:.2f} seconds",
            "",
            "SUMMARY",
            "-" * 80,
            f"Total Tests: {summary['total_tests']}",
            f"Passed: {summary['passed_tests']}",
            f"Failed: {summary['failed_tests']}",
            f"Errors: {summary['error_tests']}",
            f"Vulnerabilities Found: {summary['vulnerabilities_found']}",
            f"Attack Success Rate: {summary['attack_success_rate']:.2f}%",
            "",
        ]

        # Vulnerabilities by severity
        if summary['vulnerabilities_by_severity']:
            report_lines.extend([
                "VULNERABILITIES BY SEVERITY",
                "-" * 80,
            ])
            for severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH, SeverityLevel.MEDIUM, SeverityLevel.LOW]:
                count = summary['vulnerabilities_by_severity'].get(severity.value, 0)
                if count > 0:
                    report_lines.append(f"  {severity.value.upper()}: {count}")
            report_lines.append("")

        # Vulnerabilities by plugin
        if summary['vulnerabilities_by_plugin']:
            report_lines.extend([
                "VULNERABILITIES BY PLUGIN",
                "-" * 80,
            ])
            for plugin, count in sorted(
                summary['vulnerabilities_by_plugin'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                report_lines.append(f"  {plugin}: {count}")
            report_lines.append("")

        # Vulnerabilities by strategy
        if summary['vulnerabilities_by_strategy']:
            report_lines.extend([
                "VULNERABILITIES BY STRATEGY",
                "-" * 80,
            ])
            for strategy, count in sorted(
                summary['vulnerabilities_by_strategy'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                report_lines.append(f"  {strategy}: {count}")
            report_lines.append("")

        # Top vulnerabilities
        critical_vulns = [
            r for r in self.results.test_results
            if r.is_vulnerable and r.severity == SeverityLevel.CRITICAL
        ]

        if critical_vulns:
            report_lines.extend([
                "CRITICAL VULNERABILITIES",
                "-" * 80,
            ])
            for i, vuln in enumerate(critical_vulns[:10], 1):  # Top 10
                report_lines.extend([
                    f"\n{i}. {vuln.metadata.get('plugin', 'Unknown')}",
                    f"   Severity: {vuln.severity.value}",
                    f"   Test ID: {vuln.test_case_id}",
                    f"   Explanation: {vuln.explanation}",
                ])
            report_lines.append("")

        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def generate_json_report(self) -> str:
        """
        Generate a JSON report.

        Returns:
            JSON string

        Example:
            >>> json_report = generator.generate_json_report()
            >>> with open("report.json", "w") as f:
            ...     f.write(json_report)
        """
        summary = self.generate_summary()

        report_data = {
            "summary": summary,
            "vulnerabilities": [
                {
                    "test_id": r.test_case_id,
                    "plugin": r.metadata.get("plugin"),
                    "strategy": r.metadata.get("strategy"),
                    "severity": r.severity.value,
                    "explanation": r.explanation,
                    "input": r.metadata.get("original_input", ""),
                    "output": r.actual_output[:500],  # Truncate long outputs
                }
                for r in self.results.test_results
                if r.is_vulnerable
            ],
        }

        return json.dumps(report_data, indent=2)

    def generate_html_report(self) -> str:
        """
        Generate an HTML report with visualizations.

        Returns:
            HTML string

        Example:
            >>> html = generator.generate_html_report()
            >>> with open("report.html", "w") as f:
            ...     f.write(html)
        """
        summary = self.generate_summary()

        # Create severity distribution chart data
        severity_data = summary['vulnerabilities_by_severity']

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Red Team Assessment Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .stat-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .vulnerability {{
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin: 15px 0;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .vulnerability.critical {{
            border-left-color: #e74c3c;
        }}
        .vulnerability.high {{
            border-left-color: #e67e22;
        }}
        .vulnerability.medium {{
            border-left-color: #f39c12;
        }}
        .vulnerability.low {{
            border-left-color: #3498db;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .badge.critical {{
            background: #e74c3c;
            color: white;
        }}
        .badge.high {{
            background: #e67e22;
            color: white;
        }}
        .badge.medium {{
            background: #f39c12;
            color: white;
        }}
        .badge.low {{
            background: #3498db;
            color: white;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: bold;
        }}
        .progress-bar {{
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Red Team Assessment Report</h1>
        <p>Target: {summary['target']}</p>
        <p>Run ID: {summary['run_id']}</p>
        <p>Date: {summary['start_time']}</p>
    </div>

    <div class="summary">
        <div class="stat-card">
            <h3>Total Tests</h3>
            <div class="value">{summary['total_tests']}</div>
        </div>
        <div class="stat-card">
            <h3>Vulnerabilities</h3>
            <div class="value" style="color: #e74c3c;">{summary['vulnerabilities_found']}</div>
        </div>
        <div class="stat-card">
            <h3>Attack Success Rate</h3>
            <div class="value" style="color: #e67e22;">{summary['attack_success_rate']:.1f}%</div>
        </div>
        <div class="stat-card">
            <h3>Duration</h3>
            <div class="value" style="font-size: 24px;">{summary['duration_seconds']:.1f}s</div>
        </div>
    </div>

    <div class="section">
        <h2>Test Results Overview</h2>
        <table>
            <tr>
                <th>Status</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
            <tr>
                <td>✓ Passed</td>
                <td>{summary['passed_tests']}</td>
                <td>{(summary['passed_tests']/summary['total_tests']*100):.1f}%</td>
            </tr>
            <tr>
                <td>✗ Failed</td>
                <td>{summary['failed_tests']}</td>
                <td>{(summary['failed_tests']/summary['total_tests']*100):.1f}%</td>
            </tr>
            <tr>
                <td>⚠ Errors</td>
                <td>{summary['error_tests']}</td>
                <td>{(summary['error_tests']/summary['total_tests']*100):.1f}%</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>Vulnerabilities by Severity</h2>
        {self._generate_severity_section(summary['vulnerabilities_by_severity'])}
    </div>

    <div class="section">
        <h2>Vulnerabilities by Plugin</h2>
        <table>
            <tr>
                <th>Plugin</th>
                <th>Vulnerabilities Found</th>
            </tr>
            {''.join(f'<tr><td>{plugin}</td><td>{count}</td></tr>'
                     for plugin, count in sorted(summary['vulnerabilities_by_plugin'].items(),
                                                  key=lambda x: x[1], reverse=True))}
        </table>
    </div>

    <div class="section">
        <h2>Critical Vulnerabilities</h2>
        {self._generate_vulnerabilities_section()}
    </div>

    <div class="section">
        <h2>Plugins & Strategies Used</h2>
        <p><strong>Plugins:</strong> {', '.join(summary['plugins_used'])}</p>
        <p><strong>Strategies:</strong> {', '.join(summary['strategies_used']) if summary['strategies_used'] else 'None'}</p>
    </div>
</body>
</html>"""
        return html

    def _generate_severity_section(self, severity_data: Dict[str, int]) -> str:
        """Generate HTML for severity section."""
        html_parts = []
        for severity in ['critical', 'high', 'medium', 'low']:
            count = severity_data.get(severity, 0)
            html_parts.append(f"""
                <div style="margin: 10px 0;">
                    <span class="badge {severity}">{severity}</span>
                    <span style="margin-left: 10px; font-weight: bold;">{count} found</span>
                </div>
            """)
        return ''.join(html_parts)

    def _generate_vulnerabilities_section(self) -> str:
        """Generate HTML for vulnerabilities section."""
        critical_vulns = [
            r for r in self.results.test_results
            if r.is_vulnerable and r.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]
        ]

        if not critical_vulns:
            return "<p>No critical or high severity vulnerabilities found.</p>"

        html_parts = []
        for vuln in critical_vulns[:20]:  # Show top 20
            html_parts.append(f"""
                <div class="vulnerability {vuln.severity.value}">
                    <span class="badge {vuln.severity.value}">{vuln.severity.value}</span>
                    <h4>{vuln.metadata.get('plugin', 'Unknown Plugin')}</h4>
                    <p><strong>Explanation:</strong> {vuln.explanation}</p>
                    <p><strong>Test ID:</strong> {vuln.test_case_id}</p>
                </div>
            """)

        return ''.join(html_parts)

    def save_report(
        self,
        format: str = "html",
        file_path: Optional[str] = None
    ) -> str:
        """
        Save report to file.

        Args:
            format: Report format ('html', 'json', 'text')
            file_path: Output file path

        Returns:
            Path to saved file

        Example:
            >>> generator.save_report(format="html", file_path="report.html")
        """
        if format == "html":
            content = self.generate_html_report()
            extension = ".html"
        elif format == "json":
            content = self.generate_json_report()
            extension = ".json"
        elif format == "text":
            content = self.generate_text_report()
            extension = ".txt"
        else:
            raise ValueError(f"Unsupported format: {format}")

        if not file_path:
            file_path = f"report_{self.results.run_id}{extension}"

        with open(file_path, 'w') as f:
            f.write(content)

        print(f"Report saved to: {file_path}")
        return file_path

    def print_summary(self):
        """Print a quick summary to console."""
        summary = self.generate_summary()

        print("\n" + "=" * 60)
        print("ASSESSMENT SUMMARY")
        print("=" * 60)
        print(f"Target: {summary['target']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Vulnerabilities: {summary['vulnerabilities_found']}")
        print(f"Attack Success Rate: {summary['attack_success_rate']:.2f}%")

        if summary['vulnerabilities_by_severity']:
            print("\nBy Severity:")
            for severity, count in summary['vulnerabilities_by_severity'].items():
                print(f"  {severity.upper()}: {count}")

        print("=" * 60 + "\n")
