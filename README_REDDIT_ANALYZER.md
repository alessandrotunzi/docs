# Reddit Content Analyzer

A powerful web application that scans Reddit posts and comments for specific keywords, then uses AI to analyze the content and extract:

- **Pain Points**: Common problems, frustrations, and challenges users express
- **Product Features**: Requested features, desired capabilities, and praised functionality
- **Sentiment Analysis**: Overall sentiment and trending themes
- **Keyword Frequency**: Most mentioned terms related to your search

## Features

✨ **AI-Powered Analysis**: Uses OpenAI GPT-4 to intelligently extract insights from Reddit content  
🔍 **Smart Search**: Searches across multiple subreddits with customizable filters  
📊 **Visual Dashboard**: Beautiful, responsive web interface with real-time results  
📈 **Detailed Analytics**: Comprehensive reporting with sentiment analysis and keyword frequency  
🎯 **Targeted Insights**: Specifically designed to identify customer pain points and feature requests  

## Quick Start

### 1. Setup Environment

```bash
# Clone or download the project
cd reddit-analyzer

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` file with your credentials:

```env
# Reddit API Credentials (Get from https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=RedditAnalyzer/1.0 by YourUsername

# OpenAI API Key (Get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Application

#### Web Interface (Recommended)
```bash
python web_app.py
```
Then open your browser to: http://localhost:5000

#### Command Line Interface
```bash
python reddit_analyzer.py "your keyword" --subreddits technology programming --limit 100
```

## Getting API Keys

### Reddit API Setup
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Choose "script" type
4. Note down your `client_id` and `client_secret`
5. Use a descriptive user agent like "RedditAnalyzer/1.0 by YourUsername"

### OpenAI API Setup
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (you won't see it again!)

## Usage Examples

### Web Interface
1. Enter a keyword (e.g., "productivity app", "smartphone battery")
2. Optionally specify subreddits (e.g., "technology, programming")
3. Choose time filter (past week, month, etc.)
4. Set content limit (10-200 posts)
5. Click "Analyze Content"
6. View results in organized tabs:
   - Pain Points
   - Product Features  
   - Sentiment Analysis
   - Sample Content

### Command Line Examples

Analyze productivity apps in specific subreddits:
```bash
python reddit_analyzer.py "productivity app" --subreddits productivity getmotivated --time-filter week --limit 50
```

Analyze smartphone discussions across all Reddit:
```bash
python reddit_analyzer.py "smartphone battery" --time-filter month --limit 100 --output battery_analysis.md
```

Search for gaming content:
```bash
python reddit_analyzer.py "video game" --subreddits gaming pcgaming --limit 75
```

## Sample Output

The analyzer will provide insights like:

### Pain Points Found:
- "Battery drains too quickly during heavy usage"
- "App crashes frequently when multitasking"  
- "Interface is confusing and hard to navigate"

### Product Features Requested:
- "Dark mode for better night usage"
- "Offline synchronization capabilities"
- "Integration with calendar apps"

### Sentiment Summary:
"Generally positive sentiment with users appreciating core functionality but expressing frustration with performance issues and requesting UI improvements."

## Configuration Options

### Command Line Arguments
- `keyword`: The main keyword to search for (required)
- `--subreddits`: Comma-separated list of subreddits
- `--time-filter`: Time period (hour, day, week, month, year, all)
- `--limit`: Maximum posts to analyze per subreddit (10-200)
- `--output`: Output file for the report

### Environment Variables
- `REDDIT_CLIENT_ID`: Your Reddit app client ID
- `REDDIT_CLIENT_SECRET`: Your Reddit app secret  
- `REDDIT_USER_AGENT`: User agent string for Reddit API
- `OPENAI_API_KEY`: Your OpenAI API key
- `FLASK_ENV`: Set to 'development' for debug mode

## Technical Details

### Architecture
- **Backend**: Python Flask web server
- **Reddit API**: PRAW (Python Reddit API Wrapper)
- **AI Analysis**: OpenAI GPT-4 API
- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **Data Processing**: JSON-based data structures

### Rate Limits & Performance
- Reddit API: Respects rate limits with automatic delays
- OpenAI API: Optimized prompts to minimize token usage
- Content Limit: Capped at 200 posts for performance
- Processing Time: Typically 30-60 seconds for 50 posts

### Security Features
- Environment variable configuration
- Input validation and sanitization
- Error handling with user-friendly messages
- CORS protection for API endpoints

## Troubleshooting

### Common Issues

**"Missing required environment variables"**
- Ensure your `.env` file exists and contains all required variables
- Check that variable names match exactly (case-sensitive)

**"No content found"**
- Try broader keywords or different subreddits
- Increase time filter (try 'month' instead of 'day')
- Check if the keyword is spelled correctly

**"Reddit API errors"**
- Verify your Reddit credentials are correct
- Make sure your Reddit app is set to "script" type
- Check your user agent follows Reddit guidelines

**"OpenAI API errors"**  
- Verify your OpenAI API key is valid
- Check you have available credits/quota
- Ensure you have access to GPT-4 model

### Performance Tips
- Start with smaller content limits (25-50) for faster results
- Use specific subreddits instead of searching all Reddit
- Use shorter time filters (week instead of year) for recent insights

## Development

### Project Structure
```
reddit-analyzer/
├── reddit_analyzer.py      # Core analysis engine
├── web_app.py             # Flask web application  
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── templates/
│   └── index.html        # Web interface
├── static/
│   ├── css/style.css     # Custom styles
│   └── js/app.js         # Frontend JavaScript
└── README_REDDIT_ANALYZER.md
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Future Enhancements
- [ ] Export results to CSV/PDF
- [ ] Historical trend analysis
- [ ] Sentiment visualization charts  
- [ ] Multi-language support
- [ ] Batch processing of multiple keywords
- [ ] Integration with other social platforms

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or feature requests, please create an issue in the repository or contact the maintainers.

---

**Happy Analyzing!** 🚀 Use this tool to discover valuable insights from Reddit communities and make data-driven decisions for your products and services.