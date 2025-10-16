"""
Download Routes for MindMend Financial Documents
Provides dynamic download links for financial projections and reports
"""

from flask import Blueprint, send_file, jsonify, render_template_string
import os
from datetime import datetime

download_bp = Blueprint('download', __name__, url_prefix='/download')

# Base path for download files
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'static', 'downloads')

@download_bp.route('/financial-projections')
def financial_projections():
    """Serve the financial projections markdown file as downloadable"""
    file_path = os.path.join(DOWNLOAD_DIR, 'MINDMEND_FINANCIAL_PROJECTIONS_2025_2026.md')

    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f'MindMend_Financial_Projections_{datetime.now().strftime("%Y%m%d")}.md',
            mimetype='text/markdown'
        )
    else:
        return jsonify({"error": "File not found"}), 404

@download_bp.route('/financial-projections/view')
def view_financial_projections():
    """View the financial projections in browser with formatted HTML"""
    file_path = os.path.join(DOWNLOAD_DIR, 'MINDMEND_FINANCIAL_PROJECTIONS_2025_2026.md')

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()

        # Simple markdown-to-HTML converter (basic tables and formatting)
        html_content = content.replace('\n## ', '\n<h2>').replace('\n### ', '\n<h3>')
        html_content = html_content.replace('\n# ', '\n<h1>')
        html_content = html_content.replace('\n**', '\n<strong>').replace('**\n', '</strong>\n')
        html_content = html_content.replace('**', '</strong>').replace('<strong>', '<strong>', 1)

        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MindMend Financial Projections 2025-2026</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                    border-bottom: 2px solid #ecf0f1;
                    padding-bottom: 8px;
                }}
                h3 {{
                    color: #7f8c8d;
                    margin-top: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th {{
                    background: #3498db;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    padding: 10px;
                    border-bottom: 1px solid #ecf0f1;
                }}
                tr:hover {{
                    background: #f8f9fa;
                }}
                .download-btn {{
                    display: inline-block;
                    background: #27ae60;
                    color: white;
                    padding: 12px 24px;
                    border-radius: 5px;
                    text-decoration: none;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .download-btn:hover {{
                    background: #229954;
                }}
                code {{
                    background: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}
                .metric-box {{
                    background: #e8f4f8;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 15px 0;
                }}
                .warning-box {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 15px 0;
                }}
                .success-box {{
                    background: #d4edda;
                    border-left: 4px solid #28a745;
                    padding: 15px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1>📊 MindMend Financial Projections</h1>
                    <p><strong>Comprehensive Income & Cost Analysis 2025-2026</strong></p>
                    <a href="/download/financial-projections" class="download-btn">
                        📥 Download Markdown File
                    </a>
                </div>

                <div class="success-box">
                    <strong>✅ Document Ready for Download</strong><br>
                    This comprehensive financial projection includes 12-month revenue forecasts,
                    cost breakdowns, profitability analysis, and strategic recommendations.
                </div>

                <pre style="white-space: pre-wrap; background: #f8f9fa; padding: 20px; border-radius: 5px; overflow-x: auto;">
{content}
                </pre>

                <div style="text-align: center; margin-top: 30px;">
                    <a href="/download/financial-projections" class="download-btn">
                        📥 Download Full Document (Markdown)
                    </a>
                </div>
            </div>
        </body>
        </html>
        """

        return template
    else:
        return jsonify({"error": "File not found"}), 404

@download_bp.route('/ai-safety-research')
def ai_safety_research():
    """Serve the AI safety research report as downloadable"""
    file_path = '/home/mindmendxyz/AI_CHATBOT_SUICIDE_LIABILITY_RESEARCH_REPORT.md'

    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f'AI_Safety_Research_Report_{datetime.now().strftime("%Y%m%d")}.md',
            mimetype='text/markdown'
        )
    else:
        return jsonify({"error": "File not found"}), 404

@download_bp.route('/')
def download_center():
    """Download center page with all available documents"""

    documents = [
        {
            'title': 'Financial Projections 2025-2026',
            'description': 'Comprehensive 12-month income and cost analysis with revenue streams, profitability forecasts, and break-even analysis',
            'size': 'Large (150+ pages)',
            'format': 'Markdown (.md)',
            'download_url': '/download/financial-projections',
            'view_url': '/download/financial-projections/view'
        },
        {
            'title': 'AI Safety Research Report',
            'description': 'Critical analysis of AI chatbot suicide liability cases (ChatGPT, Character.AI) with safety enhancement recommendations',
            'size': 'Large (100+ pages)',
            'format': 'Markdown (.md)',
            'download_url': '/download/ai-safety-research',
            'view_url': None
        }
    ]

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MindMend Document Download Center</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 10px;
            }
            .subtitle {
                text-align: center;
                color: #7f8c8d;
                margin-bottom: 40px;
            }
            .document-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 25px;
                margin: 20px 0;
                transition: all 0.3s ease;
            }
            .document-card:hover {
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }
            .document-title {
                color: #2c3e50;
                font-size: 1.4em;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .document-description {
                color: #555;
                line-height: 1.6;
                margin-bottom: 15px;
            }
            .document-meta {
                color: #999;
                font-size: 0.9em;
                margin-bottom: 15px;
            }
            .btn {
                display: inline-block;
                padding: 10px 20px;
                margin-right: 10px;
                border-radius: 5px;
                text-decoration: none;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            .btn-download {
                background: #27ae60;
                color: white;
            }
            .btn-download:hover {
                background: #229954;
            }
            .btn-view {
                background: #3498db;
                color: white;
            }
            .btn-view:hover {
                background: #2980b9;
            }
            .timestamp {
                text-align: center;
                color: #999;
                margin-top: 40px;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 MindMend Document Download Center</h1>
            <p class="subtitle">Access comprehensive financial projections, research reports, and strategic planning documents</p>

    """

    for doc in documents:
        html += f"""
            <div class="document-card">
                <div class="document-title">📄 {doc['title']}</div>
                <div class="document-description">{doc['description']}</div>
                <div class="document-meta">
                    <strong>Size:</strong> {doc['size']} &nbsp;|&nbsp;
                    <strong>Format:</strong> {doc['format']}
                </div>
                <div>
                    <a href="{doc['download_url']}" class="btn btn-download">📥 Download</a>
        """

        if doc['view_url']:
            html += f'<a href="{doc["view_url"]}" class="btn btn-view">👁️ View Online</a>'

        html += """
                </div>
            </div>
        """

    html += f"""
            <div class="timestamp">
                <strong>Generated:</strong> {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
            </div>
        </div>
    </body>
    </html>
    """

    return html

# Register blueprint in app.py with:
# from download_routes import download_bp
# app.register_blueprint(download_bp)
