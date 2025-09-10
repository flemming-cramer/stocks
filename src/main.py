"""
Main entry point for the ChatGPT Micro Cap Experiment report generator.
"""

import pandas as pd
from datetime import datetime
from cli.arguments import parse_args
from data.loaders.portfolio_loader import PortfolioLoader
from data.loaders.trade_loader import TradeLoader
from analysis.roi_analyzer import ROIAnalyzer
from analysis.drawdown_analyzer import DrawdownAnalyzer
from analysis.risk_analyzer import RiskAnalyzer
from analysis.performance_analyzer import PerformanceAnalyzer
from visualization.plot_generator import PlotGenerator
from visualization.html_generator import HTMLGenerator
from utils.helpers import download_sp500
from pathlib import Path


def main():
    """Main function to generate the financial report."""
    # Parse command line arguments
    args = parse_args()
    
    # Initialize loaders
    portfolio_loader = PortfolioLoader(args.data_dir)
    trade_loader = TradeLoader(args.data_dir)
    
    # Load data
    portfolio_df = portfolio_loader.load_portfolio_data(args.date)
    portfolio_totals = portfolio_loader.load_portfolio_totals(args.date)
    trade_df = trade_loader.load_trade_data(args.date)
    
    # Initialize analyzers
    roi_analyzer = ROIAnalyzer(portfolio_loader)
    drawdown_analyzer = DrawdownAnalyzer()
    risk_analyzer = RiskAnalyzer()
    performance_analyzer = PerformanceAnalyzer()
    
    # Create reports directory
    reports_dir = HTMLGenerator.create_reports_directory(args.date)
    print(f"Saving reports to: {reports_dir}")
    
    # Initialize generators
    plot_generator = PlotGenerator(reports_dir)
    html_generator = HTMLGenerator(reports_dir)
    
    # Perform analyses
    current_stocks_roi = roi_analyzer.calculate_stock_roi(portfolio_df)
    all_stocks_roi = roi_analyzer.calculate_all_stocks_roi(portfolio_df, trade_df)
    current_portfolio_roi = roi_analyzer.calculate_current_portfolio_roi(portfolio_df)
    
    drawdown_data = drawdown_analyzer.calculate_all_drawdowns(portfolio_df)
    
    # Calculate daily performance
    daily_data = performance_analyzer.calculate_daily_performance(portfolio_totals)
    
    # Calculate ROI over time
    roi_time_df = performance_analyzer.calculate_roi_over_time(portfolio_df, trade_df)
    
    # Get date range
    start_date = pd.Timestamp("2025-06-27")
    end_date = portfolio_totals["Date"].max()
    sp500 = download_sp500(start_date, end_date)
    
    # Generate plots
    performance_plot = plot_generator.generate_performance_comparison_plot(portfolio_totals, sp500)
    print(f"Saved performance comparison plot to: {performance_plot}")
    
    roi_plot = plot_generator.generate_roi_bars_plot(current_stocks_roi)
    print(f"Saved ROI bars plot to: {roi_plot}")
    
    composition_plot = plot_generator.generate_portfolio_composition_plot(all_stocks_roi)
    print(f"Saved portfolio composition plot to: {composition_plot}")
    
    # Generate additional plots
    roi_drawdown_plot = plot_generator.generate_roi_drawdown_dashboard(current_stocks_roi, drawdown_data)
    print(f"Saved ROI/Drawdown dashboard to: {roi_drawdown_plot}")
    
    comparative_plot = plot_generator.generate_comparative_roi_dashboard(all_stocks_roi, current_portfolio_roi)
    print(f"Saved comparative ROI dashboard to: {comparative_plot}")
    
    daily_performance_plot = plot_generator.generate_daily_performance_plot(daily_data)
    print(f"Saved daily performance plot to: {daily_performance_plot}")
    
    position_analysis_plot = plot_generator.generate_position_size_analysis(all_stocks_roi)
    print(f"Saved position analysis plot to: {position_analysis_plot}")
    
    sector_analysis_plot = plot_generator.generate_sector_analysis(all_stocks_roi)
    print(f"Saved sector analysis plot to: {sector_analysis_plot}")
    
    # Calculate win/loss metrics
    win_loss_metrics = performance_analyzer.calculate_win_loss_metrics(all_stocks_roi)
    
    win_loss_plot = plot_generator.generate_win_loss_analysis(win_loss_metrics)
    print(f"Saved win/loss analysis plot to: {win_loss_plot}")
    
    roi_over_time_plot = plot_generator.generate_roi_over_time_plot(roi_time_df)
    print(f"Saved ROI over time plot to: {roi_over_time_plot}")
    
    individual_drawdown_plot = plot_generator.generate_individual_drawdown_plot(portfolio_df)
    print(f"Saved individual drawdown plot to: {individual_drawdown_plot}")
    
    # Calculate advanced risk metrics
    advanced_risk_metrics = risk_analyzer.calculate_advanced_risk_metrics(portfolio_totals)
    print(f"Advanced risk metrics calculated: Sortino Ratio = {advanced_risk_metrics['sortino_ratio']:.2f}")
    
    risk_return_plot = plot_generator.generate_risk_return_plot(portfolio_totals)
    print(f"Saved risk-return plot to: {risk_return_plot}")
    
    # Calculate portfolio-level metrics
    summary_stats = risk_analyzer.calculate_risk_metrics(all_stocks_roi, drawdown_data)
    
    # Calculate volatility metrics
    volatility_metrics = risk_analyzer.calculate_portfolio_volatility(portfolio_totals)
    
    # Format all stocks ROI table
    all_stocks_display = all_stocks_roi.copy()
    # Reorder columns to place Realized Proceeds ($) next to Cost Basis ($)
    column_order = ["Ticker", "Shares", "Cost Basis ($)", "Realized Proceeds ($)", "Market Value ($)", "ROI (%)", "Net Gain/Loss ($)"]
    # Only reorder columns that exist in the DataFrame
    available_columns = [col for col in column_order if col in all_stocks_display.columns]
    all_stocks_display = all_stocks_display[available_columns]
    all_stocks_display["Cost Basis ($)"] = all_stocks_display["Cost Basis ($)"].apply(lambda x: f"${x:.2f}")
    all_stocks_display["Realized Proceeds ($)"] = all_stocks_display["Realized Proceeds ($)"].apply(lambda x: f"${x:.2f}")
    all_stocks_display["Market Value ($)"] = all_stocks_display["Market Value ($)"].apply(lambda x: f"${x:.2f}")
    all_stocks_display["ROI (%)"] = all_stocks_display["ROI (%)"].apply(lambda x: f"{x:.2f}%")
    all_stocks_display["Net Gain/Loss ($)"] = all_stocks_display["Net Gain/Loss ($)"].apply(lambda x: f"${x:.2f}")
    
    # Format current portfolio ROI table
    current_stocks_display = current_portfolio_roi.copy()
    # Reorder columns to place Realized Proceeds ($) next to Cost Basis ($)
    column_order = ["Ticker", "Shares", "Cost Basis ($)", "Realized Proceeds ($)", "Market Value ($)", "ROI (%)", "Net Gain/Loss ($)"]
    # Only reorder columns that exist in the DataFrame
    available_columns = [col for col in column_order if col in current_stocks_display.columns]
    current_stocks_display = current_stocks_display[available_columns]
    current_stocks_display["Cost Basis ($)"] = current_stocks_display["Cost Basis ($)"].apply(lambda x: f"${x:.2f}")
    current_stocks_display["Realized Proceeds ($)"] = current_stocks_display["Realized Proceeds ($)"].apply(lambda x: f"${x:.2f}")
    current_stocks_display["Market Value ($)"] = current_stocks_display["Market Value ($)"].apply(lambda x: f"${x:.2f}")
    current_stocks_display["ROI (%)"] = current_stocks_display["ROI (%)"].apply(lambda x: f"{x:.2f}%")
    current_stocks_display["Net Gain/Loss ($)"] = current_stocks_display["Net Gain/Loss ($)"].apply(lambda x: f"${x:.2f}")
    
    # Convert to HTML tables
    all_stocks_table_html = html_generator.dataframe_to_html_table(all_stocks_display, "All Stocks Ever Purchased ROI Analysis")
    current_stocks_table_html = html_generator.dataframe_to_html_table(current_stocks_display, "Currently Held Stocks ROI Analysis")
    
    # Generate HTML report
    html_generator.generate_professional_index_html(
        performance_plot, roi_plot, composition_plot, 
        roi_drawdown_plot, comparative_plot,
        daily_performance_plot, position_analysis_plot,
        sector_analysis_plot, win_loss_plot, roi_over_time_plot,
        individual_drawdown_plot, risk_return_plot,
        all_stocks_table_html, current_stocks_table_html, 
        summary_stats, summary_stats, volatility_metrics,
        win_loss_metrics, advanced_risk_metrics,
        args.date
    )
    print(f"Saved professional index.html to: {reports_dir / 'index.html'}")
    
    # Print summary to console
    print("\n" + "="*80)
    print("CHATGPT MICRO CAP EXPERIMENT - PROFESSIONAL FINANCIAL REPORT")
    print("="*80)
    # Use the specified report date if provided, otherwise use current date
    if args.date:
        try:
            report_datetime = datetime.strptime(args.date, "%Y-%m-%d")
            formatted_report_date = report_datetime.strftime('%Y-%m-%d')
        except ValueError:
            formatted_report_date = datetime.now().strftime('%Y-%m-%d')
    else:
        formatted_report_date = datetime.now().strftime('%Y-%m-%d')
    print(f"Report Date: {formatted_report_date}")
    print(f"Total Portfolio Value: ${summary_stats['total_value']:.2f}")
    print(f"Total Return: {summary_stats['overall_roi']:.2f}% ({ '$+' if summary_stats['absolute_gain'] >= 0 else '$' }{summary_stats['absolute_gain']:.2f})")
    print(f"Annualized Volatility: {volatility_metrics['annualized_volatility']:.2f}%")
    print(f"Sharpe Ratio: {volatility_metrics['sharpe_ratio']:.2f}")
    print(f"Win Rate: {win_loss_metrics['win_rate']:.1f}% ({win_loss_metrics['winning_positions']}/{win_loss_metrics['total_positions']})")
    print(f"Average Win: {win_loss_metrics['avg_win']:.1f}% | Average Loss: {win_loss_metrics['avg_loss']:.1f}%")
    
    print("\nRisk Metrics:")
    print("-"*30)
    print(f"Average Drawdown: {summary_stats['avg_drawdown']:.2f}%")
    print(f"Worst Drawdown: {summary_stats['worst_drawdown_value']:.2f}% ({summary_stats['worst_drawdown_ticker']})")
    print(f"Best Drawdown: {summary_stats['best_drawdown_value']:.2f}% ({summary_stats['best_drawdown_ticker']})")
    print(f"Stocks with >10% Drawdown: {summary_stats['significant_drawdown_count']}")
    
    print(f"\nReports saved to: {reports_dir}")
    print("Open 'index.html' in your browser to view the full professional report.")


if __name__ == "__main__":
    main()