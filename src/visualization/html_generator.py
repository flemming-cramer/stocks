"""
HTML report generation for the ChatGPT Micro Cap Experiment.
"""

import pandas as pd
from pathlib import Path
import os
from datetime import datetime


class HTMLGenerator:
    """Generator for HTML reports."""
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
    
    @staticmethod
    def create_reports_directory(report_date: str = None) -> Path:
        """Create reports directory with specified date or current date subdirectory."""
        if report_date:
            # Validate date format
            try:
                datetime.strptime(report_date, "%Y-%m-%d")
                current_date = report_date
            except ValueError:
                raise SystemExit(f"Invalid date format '{report_date}'. Use YYYY-MM-DD.")
        else:
            current_date = datetime.now().strftime("%Y-%m-%d")
        reports_dir = Path("Reports") / current_date
        reports_dir.mkdir(parents=True, exist_ok=True)
        return reports_dir
    
    def dataframe_to_html_table(self, df: pd.DataFrame, table_title: str = "") -> str:
        """Convert a DataFrame to an HTML table with totals row.
        
        For tables with numeric data, a totals row is automatically added at the bottom.
        For ROI columns, the total is calculated as a weighted average based on cost basis
        rather than a simple arithmetic average, providing a more accurate portfolio-level metric.
        """
        html = f"<h3>{table_title}</h3>" if table_title else ""
        
        # Check if DataFrame is empty
        if df.empty:
            html += "<p>No data available</p>"
            return html
        
        # Create a copy of the dataframe to work with
        df_copy = df.copy()
        
        # Add totals row if there are numeric columns
        if len(df_copy.columns) > 1:  # More than just Ticker column
            # Create totals row
            totals_row = {}
            for col in df_copy.columns:
                if col == "Ticker":
                    totals_row[col] = "TOTAL"
                elif col == "Shares":
                    # Sum shares
                    try:
                        total = df_copy[col].astype(float).sum()
                        totals_row[col] = f"{total:.1f}"
                    except:
                        totals_row[col] = "-"
                elif col == "ROI (%)":
                    # For ROI, we'll calculate a weighted average based on Cost Basis ($)
                    if "Cost Basis ($)" in df_copy.columns and "Realized Proceeds ($)" in df_copy.columns and "Market Value ($)" in df_copy.columns:
                        # Convert formatted strings back to numbers
                        try:
                            cost_basis_nums = df_copy["Cost Basis ($)"].str.replace('$', '').str.replace(',', '').astype(float)
                            proceeds_nums = df_copy["Realized Proceeds ($)"].str.replace('$', '').str.replace(',', '').astype(float)
                            market_value_nums = df_copy["Market Value ($)"].str.replace('$', '').str.replace(',', '').astype(float)
                            total_cost = cost_basis_nums.sum()
                            total_proceeds = proceeds_nums.sum()
                            total_market_value = market_value_nums.sum()
                            if total_cost > 0:
                                # Correct formula: ROI = ((Proceeds + Market Value) / Cost Basis - 1) * 100
                                weighted_roi = ((total_proceeds + total_market_value) / total_cost - 1) * 100
                                totals_row[col] = f"{weighted_roi:.2f}%"
                            else:
                                totals_row[col] = "0.00%"
                        except:
                            totals_row[col] = "-"
                    else:
                        totals_row[col] = "-"
                else:
                    # For other numeric columns, sum them up
                    try:
                        # Convert formatted strings back to numbers
                        if col in df_copy.columns:
                            numeric_values = df_copy[col].str.replace('$', '').str.replace(',', '').astype(float)
                            total = numeric_values.sum()
                            totals_row[col] = f"${total:.2f}"
                        else:
                            totals_row[col] = "-"
                    except:
                        totals_row[col] = "-"
            
            # Add the totals row to the dataframe
            totals_df = pd.DataFrame([totals_row])
            df_with_totals = pd.concat([df_copy, totals_df], ignore_index=True)
            
            # Convert to HTML
            html += df_with_totals.to_html(index=False, table_id="roi-table", escape=False, na_rep="")
        else:
            # No numeric columns, just convert normally
            html += df_copy.to_html(index=False, table_id="roi-table", escape=False, na_rep="")
        
        return html
    
    def generate_professional_index_html(self, performance_plot: str, roi_plot: str, 
                                       composition_plot: str, roi_drawdown_plot: str, comparative_plot: str,
                                       daily_performance_plot: str, position_analysis_plot: str,
                                       sector_analysis_plot: str, win_loss_plot: str, roi_over_time_plot: str,
                                       individual_drawdown_plot: str, risk_return_plot: str,
                                       cash_plot: str,
                                       all_stocks_table: str, current_stocks_table: str, 
                                       summary_stats: dict, risk_metrics: dict, volatility_metrics: dict,
                                       win_loss_metrics: dict, advanced_risk_metrics: dict,
                                       report_date: str = None) -> None:
        """Generate professional index.html file with all plots and tables."""
        # Format the report date for display
        if report_date:
            try:
                report_datetime = datetime.strptime(report_date, "%Y-%m-%d")
                formatted_report_date = report_datetime.strftime('%B %d, %Y')
            except ValueError:
                raise SystemExit(f"Invalid date format '{report_date}'. Use YYYY-MM-DD.")
        else:
            formatted_report_date = datetime.now().strftime('%B %d, %Y')
        
        # Get just the filename for relative paths
        performance_plot_name = os.path.basename(performance_plot)
        roi_plot_name = os.path.basename(roi_plot)
        composition_plot_name = os.path.basename(composition_plot)
        roi_drawdown_plot_name = os.path.basename(roi_drawdown_plot)
        comparative_plot_name = os.path.basename(comparative_plot)
        daily_performance_plot_name = os.path.basename(daily_performance_plot)
        position_analysis_plot_name = os.path.basename(position_analysis_plot)
        sector_analysis_plot_name = os.path.basename(sector_analysis_plot)
        win_loss_plot_name = os.path.basename(win_loss_plot)
        roi_over_time_plot_name = os.path.basename(roi_over_time_plot)
        individual_drawdown_plot_name = os.path.basename(individual_drawdown_plot)
        risk_return_plot_name = os.path.basename(risk_return_plot)
        cash_plot_name = os.path.basename(cash_plot)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT Micro Cap Experiment - Professional Financial Report</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
            margin: 10px 0 0;
        }}
        .report-date {{
            font-size: 1em;
            opacity: 0.8;
            margin-top: 5px;
        }}
        .navigation {{
            background-color: #e9ecef;
            padding: 15px 30px;
            text-align: center;
            border-bottom: 1px solid #dee2e6;
        }}
        .navigation a {{
            color: #1e3c72;
            text-decoration: none;
            margin: 0 10px;
            font-weight: 500;
        }}
        .navigation a:hover {{
            text-decoration: underline;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin: 40px 0;
        }}
        .section-title {{
            color: #1e3c72;
            border-bottom: 2px solid #1e3c72;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
            font-weight: 300;
        }}
        .subsection-title {{
            color: #2a5298;
            margin: 25px 0 15px;
            font-size: 1.4em;
            font-weight: 300;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-title {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .positive {{
            color: #28a745;
        }}
        .negative {{
            color: #dc3545;
        }}
        .plot-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .plot-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        th, td {{
            border: 1px solid #dee2e6;
            padding: 12px 15px;
            text-align: right;
        }}
        th {{
            background-color: #e9ecef;
            font-weight: 600;
            text-align: center;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e9ecef;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #dee2e6;
        }}
        .disclaimer {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
            color: #856404;
        }}
        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            .content {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ChatGPT Micro Cap Experiment</h1>
            <p>Professional Financial Performance Report</p>
            <div class="report-date">Report Date: {formatted_report_date}</div>
        </div>
        
        <div class="navigation">
            <a href="#performance-analysis">Performance Analysis</a> |
            <a href="#portfolio-composition">Portfolio Composition</a> |
            <a href="#risk-metrics">Risk Metrics</a> |
            <a href="#win-loss-analysis">Win/Loss Analysis</a> |
            <a href="#detailed-position-analysis">Detailed Position Analysis</a>
        </div>
        
        <div class="content">
            <div class="section">
                <h2 class="section-title">Executive Summary</h2>
                <div class="disclaimer">
                    <strong>Disclaimer:</strong> This is a 6-month live trading experiment with real money ($100 initial investment) managed by ChatGPT. 
                    Past performance does not guarantee future results. This report is for educational and research purposes only.
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Total Portfolio Value</div>
                        <div class="metric-value">${summary_stats['total_value']:.2f}</div>
                        <div>Current Value</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Total Return</div>
                        <div class="metric-value { 'positive' if summary_stats['overall_roi'] >= 0 else 'negative' }">
                            {summary_stats['overall_roi']:.2f}%
                        </div>
                        <div>({ '$+' if summary_stats['absolute_gain'] >= 0 else '$' }{summary_stats['absolute_gain']:.2f})</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Annualized Volatility</div>
                        <div class="metric-value">{volatility_metrics['annualized_volatility']:.2f}%</div>
                        <div>Risk Metric</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Sharpe Ratio</div>
                        <div class="metric-value">{volatility_metrics['sharpe_ratio']:.2f}</div>
                        <div>Risk-Adjusted Return</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title" id="performance-analysis">Performance Analysis</h2>
                
                <h3 class="subsection-title" id="portfolio-performance">Portfolio Performance vs. Benchmark</h3>
                <div class="plot-container">
                    <img src="{performance_plot_name}" alt="Performance Comparison">
                </div>
                
                <h3 class="subsection-title" id="daily-performance">Daily Performance</h3>
                <div class="plot-container">
                    <img src="{daily_performance_plot_name}" alt="Daily Performance">
                </div>
                
                <h3 class="subsection-title" id="roi-over-time">ROI Over Time</h3>
                <div class="plot-container">
                    <img src="{roi_over_time_plot_name}" alt="ROI Over Time">
                </div>
                
                <h3 class="subsection-title" id="individual-drawdowns">Individual Stock Drawdowns</h3>
                <div class="plot-container">
                    <img src="{individual_drawdown_plot_name}" alt="Individual Drawdowns">
                </div>
                
                <h3 class="subsection-title" id="risk-return-profile">Risk-Return Profile</h3>
                <div class="plot-container">
                    <img src="{risk_return_plot_name}" alt="Risk-Return Profile">
                </div>
                
                <h3 class="subsection-title" id="risk-return-dashboard">Risk-Return Dashboard</h3>
                <div class="plot-container">
                    <img src="{roi_drawdown_plot_name}" alt="ROI Analysis Dashboard">
                </div>
                
                <!-- Add Cash Position Analysis section -->
                <h3 class="subsection-title" id="cash-position">Cash Position Analysis</h3>
                <div class="plot-container">
                    <img src="{cash_plot_name}" alt="Cash Position">
                    <p class="mt-3">
                        This chart shows the daily portfolio composition as a stacked bar chart, combining cash position and total stock market value.
                        Each bar represents a trading day, with the cash position at the base and the total value of all stocks stacked on top.
                        Value labels show the cash amount, stock value, and total portfolio value for each day.
                        Negative cash balances indicate either additional cash was added during the period or
                        trades were executed with margin/borrowed funds.
                    </p>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title" id="portfolio-composition">Portfolio Composition & Allocation</h2>
                
                <h3 class="subsection-title" id="current-holdings">Current Holdings Analysis</h3>
                <div class="plot-container">
                    <img src="{composition_plot_name}" alt="Portfolio Composition">
                </div>
                
                <h3 class="subsection-title" id="position-size">Position Size Analysis</h3>
                <div class="plot-container">
                    <img src="{position_analysis_plot_name}" alt="Position Analysis">
                </div>
                
                <h3 class="subsection-title" id="category-analysis">Category Analysis</h3>
                <div class="plot-container">
                    <img src="{sector_analysis_plot_name}" alt="Sector Analysis">
                </div>
                
                <h3 class="subsection-title" id="comparative-analysis">Comparative Portfolio Analysis</h3>
                <div class="plot-container">
                    <img src="{comparative_plot_name}" alt="Comparative ROI Analysis">
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title" id="risk-metrics">Risk Metrics</h2>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Average Drawdown</div>
                        <div class="metric-value { 'negative' if risk_metrics['avg_drawdown'] < 0 else '' }">
                            {risk_metrics['avg_drawdown']:.2f}%
                        </div>
                        <div>Across All Positions</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Worst Drawdown</div>
                        <div class="metric-value negative">
                            {risk_metrics['worst_drawdown_value']:.2f}%
                        </div>
                        <div>{risk_metrics['worst_drawdown_ticker']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Best Drawdown</div>
                        <div class="metric-value { 'negative' if risk_metrics['best_drawdown_value'] < 0 else 'positive' }">
                            {risk_metrics['best_drawdown_value']:.2f}%
                        </div>
                        <div>{risk_metrics['best_drawdown_ticker']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">High Drawdown Stocks</div>
                        <div class="metric-value">
                            {risk_metrics['significant_drawdown_count']}
                        </div>
                        <div>>10% Drawdown</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Sortino Ratio</div>
                        <div class="metric-value">
                            {advanced_risk_metrics['sortino_ratio']:.2f}
                        </div>
                        <div>Downside Risk-Adjusted Return</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Max Consecutive Wins</div>
                        <div class="metric-value">
                            {advanced_risk_metrics['max_consecutive_wins']}
                        </div>
                        <div>Trading Days</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Max Consecutive Losses</div>
                        <div class="metric-value negative">
                            {advanced_risk_metrics['max_consecutive_losses']}
                        </div>
                        <div>Trading Days</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title" id="win-loss-analysis">Win/Loss Analysis</h2>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Win Rate</div>
                        <div class="metric-value">
                            {win_loss_metrics['win_rate']:.1f}%
                        </div>
                        <div>{win_loss_metrics['winning_positions']}/{win_loss_metrics['total_positions']} Positions</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Average Win</div>
                        <div class="metric-value positive">
                            {win_loss_metrics['avg_win']:.1f}%
                        </div>
                        <div>Profitable Positions</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Average Loss</div>
                        <div class="metric-value negative">
                            {win_loss_metrics['avg_loss']:.1f}%
                        </div>
                        <div>Losing Positions</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Best Position</div>
                        <div class="metric-value positive">
                            {win_loss_metrics['best_position']['ROI (%)']:.1f}%
                        </div>
                        <div>{win_loss_metrics['best_position']['Ticker']}</div>
                    </div>
                </div>
                
                <h3 class="subsection-title" id="win-loss-distribution">Win/Loss Distribution</h3>
                <div class="plot-container">
                    <img src="{win_loss_plot_name}" alt="Win/Loss Analysis">
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title" id="detailed-position-analysis">Detailed Position Analysis</h2>
                
                <h3 class="subsection-title" id="all-stocks">All Stocks Ever Purchased</h3>
                {all_stocks_table}
                
                <h3 class="subsection-title" id="currently-held">Currently Held Stocks</h3>
                {current_stocks_table}
            </div>
        </div>
        <div class="footer">
            <p>ChatGPT Micro Cap Experiment | Professional Financial Report | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>This report is automatically generated and should be reviewed by a qualified financial professional before making investment decisions.</p>
        </div>
    </div>
</body>
</html>
        """
        
        index_path = self.reports_dir / "index.html"
        with open(index_path, "w") as f:
            f.write(html_content)