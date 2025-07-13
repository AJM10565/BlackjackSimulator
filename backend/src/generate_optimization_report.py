#!/usr/bin/env python3
"""
Generate HTML report from optimization CSV files
"""

import os
import csv
import glob
from datetime import datetime
import argparse
import json


def load_csv_results(csv_file):
    """Load results from a CSV file"""
    results = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric values
            row['roi'] = float(row['roi'])
            row['win_rate'] = float(row['win_rate'])
            row['hands_played'] = int(row['hands_played'])
            row['final_bankroll'] = float(row['final_bankroll'])
            row['bet_threshold'] = int(row['bet_threshold'])
            row['bet_increment'] = int(row['bet_increment'])
            results.append(row)
    return results


def generate_html_report(output_dir='optimization_results'):
    """Generate comprehensive HTML report from all CSV files"""
    
    # Find all CSV files
    csv_files = glob.glob(os.path.join(output_dir, 'grid_search_*.csv'))
    csv_files.sort(reverse=True)  # Most recent first
    
    if not csv_files:
        print("No optimization results found!")
        return
    
    # Load all results
    all_runs = []
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        timestamp = filename.replace('grid_search_', '').replace('.csv', '')
        
        results = load_csv_results(csv_file)
        if results:
            # Sort by ROI
            results.sort(key=lambda x: x['roi'], reverse=True)
            
            all_runs.append({
                'filename': filename,
                'timestamp': timestamp,
                'total_configs': len(results),
                'best_roi': results[0]['roi'],
                'best_config': results[0],
                'top_10': results[:10],
                'all_results': results
            })
    
    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Blackjack Strategy Optimization Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .summary {{
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: right;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            position: sticky;
            top: 0;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #e8f4f8;
        }}
        .positive {{
            color: green;
            font-weight: bold;
        }}
        .negative {{
            color: red;
        }}
        .run-section {{
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .best-config {{
            background-color: #d4edda;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
        }}
        .metric-label {{
            font-weight: bold;
            color: #666;
        }}
        .metric-value {{
            font-size: 1.2em;
            color: #333;
        }}
        details {{
            margin: 10px 0;
        }}
        summary {{
            cursor: pointer;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 5px;
        }}
        summary:hover {{
            background-color: #e0e0e0;
        }}
    </style>
    <script>
        function sortTable(tableId, columnIndex) {{
            var table = document.getElementById(tableId);
            var rows = Array.from(table.getElementsByTagName('tr'));
            var header = rows.shift();
            
            rows.sort(function(a, b) {{
                var aVal = parseFloat(a.cells[columnIndex].textContent);
                var bVal = parseFloat(b.cells[columnIndex].textContent);
                return bVal - aVal;
            }});
            
            table.innerHTML = '';
            table.appendChild(header);
            rows.forEach(row => table.appendChild(row));
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>Blackjack Strategy Optimization Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="metric">
                <span class="metric-label">Total Optimization Runs:</span>
                <span class="metric-value">{len(all_runs)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Configurations Tested:</span>
                <span class="metric-value">{sum(run['total_configs'] for run in all_runs):,}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Best ROI Found:</span>
                <span class="metric-value {('positive' if max(run['best_roi'] for run in all_runs) > 0 else 'negative')}">
                    {max(run['best_roi'] for run in all_runs):.4%}
                </span>
            </div>
        </div>
"""
    
    # Add each optimization run
    for i, run in enumerate(all_runs):
        best = run['best_config']
        roi_class = 'positive' if best['roi'] > 0 else 'negative'
        
        html += f"""
        <div class="run-section">
            <h2>Run #{i+1} - {run['timestamp']}</h2>
            
            <div class="best-config">
                <h3>Best Configuration</h3>
                <div class="metric">
                    <span class="metric-label">ROI:</span>
                    <span class="metric-value {roi_class}">{best['roi']:.4%}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Win Rate:</span>
                    <span class="metric-value">{best['win_rate']:.2%}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Final Bankroll:</span>
                    <span class="metric-value">${best['final_bankroll']:,.0f}</span>
                </div>
                
                <h4>Card Counting Values:</h4>
                <p>
                    2={best['card_2']}, 3={best['card_3']}, 4={best['card_4']}, 5={best['card_5']}, 
                    6={best['card_6']}, 7={best['card_7']}, 8={best['card_8']}, 9={best['card_9']},
                    10/J/Q/K={best['card_10']}, A={best['card_A']}
                </p>
                
                <h4>Other Parameters:</h4>
                <p>
                    Ace Adjustment: {best['ace_adjustment']},
                    Betting Threshold: {best['bet_threshold']},
                    Betting Increment: {best['bet_increment']}
                </p>
            </div>
            
            <details>
                <summary>Top 10 Configurations (click to expand)</summary>
                <table>
                    <thead>
                        <tr>
                            <th onclick="sortTable('table_{i}', 0)">ROI ↓</th>
                            <th onclick="sortTable('table_{i}', 1)">Win Rate</th>
                            <th>Card 3</th>
                            <th>Card 4</th>
                            <th>Card 5</th>
                            <th>Card 6</th>
                            <th>Card 8</th>
                            <th>Card 9</th>
                            <th>Ace Adj</th>
                            <th>Bet Thresh</th>
                            <th>Bet Incr</th>
                        </tr>
                    </thead>
                    <tbody id="table_{i}">
"""
        
        for config in run['top_10']:
            roi_class = 'positive' if config['roi'] > 0 else 'negative'
            html += f"""
                        <tr>
                            <td class="{roi_class}">{config['roi']:.4%}</td>
                            <td>{config['win_rate']:.2%}</td>
                            <td>{config['card_3']}</td>
                            <td>{config['card_4']}</td>
                            <td>{config['card_5']}</td>
                            <td>{config['card_6']}</td>
                            <td>{config['card_8']}</td>
                            <td>{config['card_9']}</td>
                            <td>{config['ace_adjustment']}</td>
                            <td>{config['bet_threshold']}</td>
                            <td>{config['bet_increment']}</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </details>
        </div>
"""
    
    # Find overall best configuration
    overall_best = max((run['best_config'] for run in all_runs), key=lambda x: x['roi'])
    
    html += f"""
        <div class="summary">
            <h2>Overall Best Configuration</h2>
            <div class="best-config">
                <p><strong>Found in run:</strong> {next(run['timestamp'] for run in all_runs if run['best_config'] == overall_best)}</p>
                <div class="metric">
                    <span class="metric-label">ROI:</span>
                    <span class="metric-value {('positive' if overall_best['roi'] > 0 else 'negative')}">
                        {overall_best['roi']:.4%}
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Win Rate:</span>
                    <span class="metric-value">{overall_best['win_rate']:.2%}</span>
                </div>
                
                <h3>Configuration Details:</h3>
                <pre>{json.dumps(dict(
                    card_values=dict(
                        two=overall_best['card_2'],
                        three=overall_best['card_3'],
                        four=overall_best['card_4'],
                        five=overall_best['card_5'],
                        six=overall_best['card_6'],
                        seven=overall_best['card_7'],
                        eight=overall_best['card_8'],
                        nine=overall_best['card_9'],
                        ten_jack_queen_king=overall_best['card_10'],
                        ace=overall_best['card_A']
                    ),
                    ace_adjustment=overall_best['ace_adjustment'],
                    betting=dict(
                        threshold=overall_best['bet_threshold'],
                        increment=overall_best['bet_increment']
                    )
                ), indent=2)}</pre>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    # Save report
    report_path = os.path.join(output_dir, 'optimization_report.html')
    with open(report_path, 'w') as f:
        f.write(html)
    
    print(f"Report generated: {report_path}")
    return report_path


def main():
    parser = argparse.ArgumentParser(description='Generate HTML report from optimization results')
    parser.add_argument('--dir', default='optimization_results',
                        help='Directory containing CSV results')
    
    args = parser.parse_args()
    generate_html_report(args.dir)


if __name__ == "__main__":
    main()