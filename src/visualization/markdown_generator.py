"""
Markdown report generation for the ChatGPT Micro Cap Experiment.
"""

import pandas as pd
from pathlib import Path
import os
from datetime import datetime
from .report_generator import ReportGenerator, ReportContent


class MarkdownGenerator(ReportGenerator):
    """Generator for Markdown reports."""
    
    def __init__(self, reports_dir: Path):
        super().__init__(reports_dir)
    
    def generate_report(self, content: ReportContent) -> str:
        """Generate a Markdown report from the provided content."""
        markdown_content = self._render_header(content)
        markdown_content += self._render_table_of_contents(content)
        markdown_content += self._render_executive_summary(content)
        markdown_content += self._render_sections(content)
        markdown_content += self._render_footer(content)
        
        # Save the markdown file
        md_path = self.reports_dir / "index.md"
        with open(md_path, "w") as f:
            f.write(markdown_content)
        return str(md_path)
    
    def _render_header(self, content: ReportContent) -> str:
        """Render the report header."""
        # Format the report date for display
        try:
            report_datetime = datetime.strptime(content.report_date, "%Y-%m-%d")
            formatted_report_date = report_datetime.strftime('%B %d, %Y')
        except ValueError:
            formatted_report_date = datetime.now().strftime('%B %d, %Y')
            
        return f"""# {content.title}
## {content.subtitle}

**Report Date:** {formatted_report_date}

---
"""
    
    def _render_table_of_contents(self, content: ReportContent) -> str:
        """Render the table of contents."""
        toc = "## Table of Contents\n\n"
        
        # Add executive summary
        toc += "- [Executive Summary](#executive-summary)\n"
        
        # Add all sections
        for i, section in enumerate(content.sections, 1):
            # Convert section title to lowercase and replace spaces with hyphens for anchor links
            anchor = section['title'].lower().replace(' ', '-').replace('/', '-').replace('&', 'and')
            toc += f"- [{section['title']}](#{anchor})\n"
            
            # Add subsections if they exist in the content
            for item in section['content']:
                if item['type'] == 'plot' or item['type'] == 'table':
                    # Create a subsection anchor
                    sub_anchor = item['title'].lower().replace(' ', '-').replace('/', '-').replace('&', 'and')
                    toc += f"  - [{item['title']}](#{sub_anchor})\n"
        
        # Add footer
        toc += "- [Footer](#footer)\n\n"
        toc += "---\n\n"
        
        return toc
    
    def _render_executive_summary(self, content: ReportContent) -> str:
        """Render the executive summary section."""
        # Extract metrics for the summary
        summary_stats = content.metrics.get('summary_stats', {})
        volatility_metrics = content.metrics.get('volatility_metrics', {})
        win_loss_metrics = content.metrics.get('win_loss_metrics', {})
        
        summary = """## Executive Summary

> **Disclaimer:** This is a 6-month live trading experiment with real money ($100 initial investment) managed by ChatGPT. Past performance does not guarantee future results. This report is for educational and research purposes only.

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Portfolio Value | ${:.2f} |
| Total Return | {:.2f}% ({}) |
| Annualized Volatility | {:.2f}% |
| Sharpe Ratio | {:.2f} |

""".format(
            summary_stats.get('total_value', 0),
            summary_stats.get('overall_roi', 0),
            '${:.2f}'.format(summary_stats.get('absolute_gain', 0)),
            volatility_metrics.get('annualized_volatility', 0),
            volatility_metrics.get('sharpe_ratio', 0)
        )
        
        return summary
    
    def _render_navigation(self, content: ReportContent) -> str:
        """Render the navigation section."""
        # For Markdown, we use a table of contents instead of navigation
        return self._render_table_of_contents(content)
    
    def _render_sections(self, content: ReportContent) -> str:
        """Render all sections of the report."""
        sections_md = ""
        
        for section in content.sections:
            # Convert section title to lowercase and replace spaces with hyphens for anchor links
            anchor = section['title'].lower().replace(' ', '-').replace('/', '-').replace('&', 'and')
            
            section_md = f"## {section['title']}\n\n"
            
            # Render section content
            for item in section['content']:
                if item['type'] == 'plot':
                    # Create a subsection anchor
                    sub_anchor = item['title'].lower().replace(' ', '-').replace('/', '-').replace('&', 'and')
                    plot_name = os.path.basename(item['path'])
                    section_md += f"### {item['title']}\n\n"
                    section_md += f"![{item['title']}]({plot_name})\n\n"
                elif item['type'] == 'table':
                    # Create a subsection anchor
                    sub_anchor = item['title'].lower().replace(' ', '-').replace('/', '-').replace('&', 'and')
                    section_md += f"### {item['title']}\n\n"
                    section_md += self._dataframe_to_markdown_table(item['data'])
                    section_md += "\n"
                elif item['type'] == 'text':
                    section_md += f"{item['text']}\n\n"
            
            sections_md += section_md
        
        return sections_md
    
    def _dataframe_to_markdown_table(self, df: pd.DataFrame) -> str:
        """Convert a DataFrame to a Markdown table."""
        if df.empty:
            return "No data available\n"
        
        # Create the markdown table
        markdown_table = ""
        
        # Header row
        markdown_table += "| " + " | ".join(df.columns) + " |\n"
        markdown_table += "| " + " | ".join(["---"] * len(df.columns)) + " |\n"
        
        # Data rows
        for _, row in df.iterrows():
            markdown_table += "| " + " | ".join(str(val) for val in row) + " |\n"
        
        return markdown_table
    
    def _render_footer(self, content: ReportContent) -> str:
        """Render the report footer."""
        return f"""## Footer

ChatGPT Micro Cap Experiment | Professional Financial Report | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This report is automatically generated and should be reviewed by a qualified financial professional before making investment decisions.
"""