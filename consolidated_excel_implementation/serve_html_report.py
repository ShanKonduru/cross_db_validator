#!/usr/bin/env python3
"""
Simple web server to serve the consolidated trends HTML report.
This allows proper viewing of the interactive charts and features.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path


def serve_html_report(port=8080):
    """Serve the HTML report on a local web server."""
    
    # Change to the output directory
    output_dir = Path(__file__).parent / "output"
    if not output_dir.exists():
        print("❌ Output directory not found!")
        return
    
    os.chdir(output_dir)
    
    # Find the latest HTML report
    html_files = list(output_dir.glob("consolidated_trends_report_*.html"))
    if not html_files:
        print("❌ No HTML reports found!")
        return
    
    latest_report = max(html_files, key=os.path.getctime)
    report_filename = latest_report.name
    
    print(f"🌐 Starting web server for: {report_filename}")
    print(f"📁 Serving from: {output_dir}")
    print(f"🔗 URL: http://localhost:{port}/{report_filename}")
    
    try:
        # Create server
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"✅ Server started on port {port}")
            print(f"🌍 Open your browser to: http://localhost:{port}/{report_filename}")
            print("Press Ctrl+C to stop the server")
            
            # Try to open browser automatically
            try:
                webbrowser.open(f"http://localhost:{port}/{report_filename}")
                print("🚀 Browser opened automatically")
            except:
                print("💡 Please manually open the URL in your browser")
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")


def show_report_info():
    """Show information about the generated report."""
    output_dir = Path(__file__).parent / "output"
    
    html_files = list(output_dir.glob("consolidated_trends_report_*.html"))
    json_files = list(output_dir.glob("consolidated_analytics_*.json"))
    
    print("📊 Generated Reports")
    print("=" * 30)
    
    if html_files:
        for html_file in html_files:
            size = html_file.stat().st_size
            print(f"📄 HTML Report: {html_file.name}")
            print(f"   📏 Size: {size:,} bytes")
            print(f"   📅 Created: {html_file.stat().st_mtime}")
    
    if json_files:
        for json_file in json_files:
            size = json_file.stat().st_size
            print(f"📋 JSON Analytics: {json_file.name}")
            print(f"   📏 Size: {size:,} bytes")
    
    print("\n🌟 Report Features:")
    print("   📊 6 Interactive Charts (Chart.js)")
    print("   📈 Test Type Distribution")
    print("   📋 Category & Priority Analysis")
    print("   🌍 Environment Distribution")
    print("   ⚙️ Parameter Usage Statistics") 
    print("   🚀 Execution Readiness Status")
    print("   📱 Responsive Design")
    print("   🎨 Modern CSS Styling")
    print("   📄 Detailed Data Tables")
    print("   📊 Comprehensive Metrics")


if __name__ == "__main__":
    print("🎨 Consolidated Trends HTML Report Server")
    print("=" * 45)
    
    # Show report information
    show_report_info()
    
    # Ask user if they want to start server
    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        serve_html_report()
    else:
        print("\n💡 To view the report in your browser:")
        print("   python serve_html_report.py --serve")
        print("\n📁 Or manually open the HTML file from the output directory")