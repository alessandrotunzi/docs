#!/usr/bin/env python3
"""
Reddit Content Analyzer Web Interface
A Flask web application for analyzing Reddit content.
"""

import os
import json
import asyncio
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.exceptions import BadRequest
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our analyzer
from reddit_analyzer import RedditAnalyzer, AnalysisResult

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze Reddit content based on user input"""
    try:
        data = request.get_json()
        
        # Validate input
        keyword = data.get('keyword', '').strip()
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        subreddits = data.get('subreddits', [])
        if subreddits and not isinstance(subreddits, list):
            subreddits = [s.strip() for s in subreddits.split(',') if s.strip()]
        
        time_filter = data.get('time_filter', 'week')
        limit = min(int(data.get('limit', 50)), 200)  # Cap at 200 for performance
        
        # Check for required environment variables
        required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT', 'OPENAI_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            return jsonify({
                'error': f'Missing required environment variables: {", ".join(missing_vars)}. Please check your .env file.'
            }), 500
        
        # Initialize analyzer
        analyzer = RedditAnalyzer(
            reddit_client_id=os.getenv('REDDIT_CLIENT_ID'),
            reddit_client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            reddit_user_agent=os.getenv('REDDIT_USER_AGENT'),
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Search Reddit content
        logger.info(f"Starting analysis for keyword: {keyword}")
        content = analyzer.search_reddit_content(
            keyword=keyword,
            subreddits=subreddits if subreddits else None,
            time_filter=time_filter,
            limit=limit
        )
        
        if not content:
            return jsonify({
                'error': 'No content found for the specified keyword and criteria.'
            }), 404
        
        # Analyze with LLM
        analysis = analyzer.analyze_content_with_llm(content, keyword)
        
        # Generate report
        report = analyzer.generate_report(analysis, keyword)
        
        # Prepare response
        response_data = {
            'keyword': keyword,
            'analysis_date': datetime.now().isoformat(),
            'total_content_analyzed': analysis.total_content_analyzed,
            'pain_points': analysis.pain_points,
            'product_features': analysis.product_features,
            'sentiment_summary': analysis.sentiment_summary,
            'keyword_frequency': analysis.keyword_frequency,
            'report': report,
            'sample_content': [
                {
                    'title': content_item.title,
                    'content': content_item.content[:200] + '...' if len(content_item.content) > 200 else content_item.content,
                    'subreddit': content_item.subreddit,
                    'score': content_item.score,
                    'type': content_item.content_type,
                    'url': content_item.url
                }
                for content_item in content[:10]  # Show first 10 items
            ]
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return jsonify({'error': f'An error occurred during analysis: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Check if we're in development mode
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)