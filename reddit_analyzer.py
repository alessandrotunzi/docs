#!/usr/bin/env python3
"""
Reddit Content Analyzer
Scans Reddit posts and comments for keywords, then analyzes content using LLM
to identify pain points and product features.
"""

import os
import re
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

import praw
import openai
from openai import OpenAI
import argparse
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RedditContent:
    """Data class for Reddit content"""
    id: str
    title: str
    content: str
    url: str
    score: int
    created_utc: float
    subreddit: str
    content_type: str  # 'post' or 'comment'
    author: str

@dataclass
class AnalysisResult:
    """Data class for analysis results"""
    pain_points: List[str]
    product_features: List[str]
    sentiment_summary: str
    keyword_frequency: Dict[str, int]
    total_content_analyzed: int

class RedditAnalyzer:
    """Main Reddit analyzer class"""
    
    def __init__(self, reddit_client_id: str, reddit_client_secret: str, 
                 reddit_user_agent: str, openai_api_key: str):
        """Initialize the Reddit analyzer"""
        self.reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent
        )
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.collected_content = []
        
    def search_reddit_content(self, keyword: str, subreddits: List[str] = None, 
                            time_filter: str = 'week', limit: int = 100) -> List[RedditContent]:
        """
        Search Reddit for content containing the keyword
        
        Args:
            keyword: The keyword to search for
            subreddits: List of subreddits to search (None for all)
            time_filter: Time filter ('hour', 'day', 'week', 'month', 'year', 'all')
            limit: Maximum number of posts to analyze per subreddit
            
        Returns:
            List of RedditContent objects
        """
        logger.info(f"Searching Reddit for keyword: '{keyword}'")
        content_list = []
        
        # Default to popular subreddits if none specified
        if subreddits is None:
            subreddits = ['all']
        
        for subreddit_name in subreddits:
            try:
                logger.info(f"Searching in r/{subreddit_name}")
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search posts
                for submission in subreddit.search(keyword, time_filter=time_filter, limit=limit):
                    if self._contains_keyword(submission.title + " " + submission.selftext, keyword):
                        content_list.append(RedditContent(
                            id=submission.id,
                            title=submission.title,
                            content=submission.selftext,
                            url=submission.url,
                            score=submission.score,
                            created_utc=submission.created_utc,
                            subreddit=submission.subreddit.display_name,
                            content_type='post',
                            author=str(submission.author) if submission.author else '[deleted]'
                        ))
                    
                    # Also check comments for keyword mentions
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list()[:20]:  # Limit comments per post
                        if hasattr(comment, 'body') and self._contains_keyword(comment.body, keyword):
                            content_list.append(RedditContent(
                                id=comment.id,
                                title=submission.title,
                                content=comment.body,
                                url=f"https://reddit.com{submission.permalink}{comment.id}",
                                score=comment.score,
                                created_utc=comment.created_utc,
                                subreddit=submission.subreddit.display_name,
                                content_type='comment',
                                author=str(comment.author) if comment.author else '[deleted]'
                            ))
                
                # Small delay to respect rate limits
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error searching r/{subreddit_name}: {str(e)}")
                continue
        
        logger.info(f"Found {len(content_list)} pieces of content")
        self.collected_content = content_list
        return content_list
    
    def _contains_keyword(self, text: str, keyword: str) -> bool:
        """Check if text contains keyword (case insensitive)"""
        if not text:
            return False
        return keyword.lower() in text.lower()
    
    def analyze_content_with_llm(self, content_list: List[RedditContent], keyword: str) -> AnalysisResult:
        """
        Analyze collected content using LLM to extract pain points and product features
        
        Args:
            content_list: List of RedditContent to analyze
            keyword: The original search keyword for context
            
        Returns:
            AnalysisResult with extracted insights
        """
        logger.info(f"Analyzing {len(content_list)} pieces of content with LLM")
        
        # Prepare content for analysis
        combined_content = self._prepare_content_for_analysis(content_list)
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(combined_content, keyword)
        
        try:
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert market researcher specializing in analyzing social media content to identify customer pain points and desired product features."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            return self._parse_llm_response(analysis_text, content_list, keyword)
            
        except Exception as e:
            logger.error(f"Error during LLM analysis: {str(e)}")
            # Return a basic analysis if LLM fails
            return self._fallback_analysis(content_list, keyword)
    
    def _prepare_content_for_analysis(self, content_list: List[RedditContent]) -> str:
        """Prepare content for LLM analysis by combining and cleaning"""
        combined_text = []
        
        for content in content_list[:50]:  # Limit to avoid token limits
            text = f"[{content.content_type.upper()}] {content.title}\n{content.content}\n"
            # Clean and truncate
            text = re.sub(r'\n+', '\n', text)
            text = text.strip()[:500]  # Limit each piece
            combined_text.append(text)
        
        return "\n---\n".join(combined_text)
    
    def _create_analysis_prompt(self, content: str, keyword: str) -> str:
        """Create a detailed prompt for LLM analysis"""
        return f"""
Please analyze the following Reddit posts and comments related to "{keyword}". 

Extract and categorize insights into these specific areas:

1. **PAIN POINTS**: What problems, frustrations, or challenges are people expressing? Look for complaints, difficulties, and unmet needs.

2. **PRODUCT FEATURES**: What specific features, capabilities, or solutions are people requesting or discussing positively? Look for feature requests, desired functionality, and praised capabilities.

3. **SENTIMENT SUMMARY**: Provide a brief overview of the general sentiment and common themes.

Please format your response as JSON with this structure:
{{
    "pain_points": ["pain point 1", "pain point 2", ...],
    "product_features": ["feature 1", "feature 2", ...],
    "sentiment_summary": "Brief summary of sentiment and themes"
}}

Content to analyze:
{content}
"""
    
    def _parse_llm_response(self, response_text: str, content_list: List[RedditContent], keyword: str) -> AnalysisResult:
        """Parse LLM response into structured results"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                parsed = json.loads(json_str)
                
                return AnalysisResult(
                    pain_points=parsed.get('pain_points', []),
                    product_features=parsed.get('product_features', []),
                    sentiment_summary=parsed.get('sentiment_summary', ''),
                    keyword_frequency=self._calculate_keyword_frequency(content_list, keyword),
                    total_content_analyzed=len(content_list)
                )
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
        
        # Fallback parsing
        return self._fallback_analysis(content_list, keyword)
    
    def _fallback_analysis(self, content_list: List[RedditContent], keyword: str) -> AnalysisResult:
        """Provide basic analysis if LLM fails"""
        logger.info("Using fallback analysis method")
        
        # Basic keyword extraction
        pain_keywords = ['problem', 'issue', 'bug', 'broken', 'terrible', 'awful', 'hate', 'frustrated']
        feature_keywords = ['feature', 'want', 'need', 'should', 'would', 'add', 'improve']
        
        pain_points = []
        product_features = []
        
        for content in content_list:
            text = (content.title + " " + content.content).lower()
            
            for pain_word in pain_keywords:
                if pain_word in text:
                    # Extract sentence containing the pain word
                    sentences = text.split('.')
                    for sentence in sentences:
                        if pain_word in sentence:
                            pain_points.append(sentence.strip()[:100])
                            break
            
            for feature_word in feature_keywords:
                if feature_word in text:
                    sentences = text.split('.')
                    for sentence in sentences:
                        if feature_word in sentence:
                            product_features.append(sentence.strip()[:100])
                            break
        
        return AnalysisResult(
            pain_points=list(set(pain_points))[:10],
            product_features=list(set(product_features))[:10],
            sentiment_summary="Analysis completed using basic keyword matching",
            keyword_frequency=self._calculate_keyword_frequency(content_list, keyword),
            total_content_analyzed=len(content_list)
        )
    
    def _calculate_keyword_frequency(self, content_list: List[RedditContent], keyword: str) -> Dict[str, int]:
        """Calculate frequency of keywords and related terms"""
        frequency = defaultdict(int)
        
        for content in content_list:
            text = (content.title + " " + content.content).lower()
            # Count main keyword
            frequency[keyword.lower()] += text.count(keyword.lower())
            
            # Count common related words
            words = re.findall(r'\w+', text)
            for word in words:
                if len(word) > 3 and word not in ['that', 'this', 'they', 'them', 'with']:
                    frequency[word] += 1
        
        # Return top 20 most frequent
        return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:20])
    
    def generate_report(self, analysis_result: AnalysisResult, keyword: str, 
                       output_file: str = None) -> str:
        """Generate a comprehensive report"""
        report = f"""
# Reddit Content Analysis Report
**Keyword:** {keyword}
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Content Analyzed:** {analysis_result.total_content_analyzed}

## Top Pain Points
"""
        
        for i, pain_point in enumerate(analysis_result.pain_points, 1):
            report += f"{i}. {pain_point}\n"
        
        report += f"""
## Requested/Mentioned Product Features
"""
        
        for i, feature in enumerate(analysis_result.product_features, 1):
            report += f"{i}. {feature}\n"
        
        report += f"""
## Sentiment Summary
{analysis_result.sentiment_summary}

## Keyword Frequency Analysis
"""
        
        for word, count in list(analysis_result.keyword_frequency.items())[:10]:
            report += f"- {word}: {count} mentions\n"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to {output_file}")
        
        return report

def main():
    """Main function to run the Reddit analyzer"""
    parser = argparse.ArgumentParser(description='Analyze Reddit content for pain points and product features')
    parser.add_argument('keyword', help='Keyword to search for')
    parser.add_argument('--subreddits', nargs='+', help='Subreddits to search (default: all)', default=None)
    parser.add_argument('--time-filter', choices=['hour', 'day', 'week', 'month', 'year', 'all'], 
                       default='week', help='Time filter for posts')
    parser.add_argument('--limit', type=int, default=100, help='Maximum posts per subreddit')
    parser.add_argument('--output', help='Output file for report')
    
    args = parser.parse_args()
    
    # Check for required environment variables
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these environment variables before running the analyzer.")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = RedditAnalyzer(
        reddit_client_id=os.getenv('REDDIT_CLIENT_ID'),
        reddit_client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        reddit_user_agent=os.getenv('REDDIT_USER_AGENT'),
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    try:
        # Search Reddit content
        content = analyzer.search_reddit_content(
            keyword=args.keyword,
            subreddits=args.subreddits,
            time_filter=args.time_filter,
            limit=args.limit
        )
        
        if not content:
            logger.warning("No content found for the specified keyword.")
            return
        
        # Analyze with LLM
        analysis = analyzer.analyze_content_with_llm(content, args.keyword)
        
        # Generate and display report
        report = analyzer.generate_report(analysis, args.keyword, args.output)
        print(report)
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()