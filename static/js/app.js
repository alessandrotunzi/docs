// Reddit Content Analyzer Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const statusCard = document.getElementById('statusCard');
    const statusText = document.getElementById('statusText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const results = document.getElementById('results');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    const welcomeMessage = document.getElementById('welcomeMessage');

    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = {
            keyword: document.getElementById('keyword').value.trim(),
            subreddits: document.getElementById('subreddits').value.trim(),
            time_filter: document.getElementById('timeFilter').value,
            limit: parseInt(document.getElementById('limit').value)
        };

        // Validate
        if (!formData.keyword) {
            showError('Please enter a keyword to search for.');
            return;
        }

        // Parse subreddits
        if (formData.subreddits) {
            formData.subreddits = formData.subreddits.split(',').map(s => s.trim()).filter(s => s);
        } else {
            formData.subreddits = [];
        }

        // Start analysis
        await startAnalysis(formData);
    });

    async function startAnalysis(formData) {
        try {
            // Show loading state
            showLoading('Initializing analysis...');
            hideError();
            hideResults();
            hideWelcome();

            // Make API request
            updateStatus('Searching Reddit content...');
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Analysis failed');
            }

            updateStatus('Analyzing content with AI...');
            const data = await response.json();

            // Hide loading and show results
            hideLoading();
            displayResults(data);

        } catch (error) {
            console.error('Analysis error:', error);
            hideLoading();
            showError(error.message || 'An unexpected error occurred during analysis.');
        }
    }

    function showLoading(message = 'Processing...') {
        statusText.textContent = message;
        statusCard.style.display = 'block';
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
    }

    function hideLoading() {
        statusCard.style.display = 'none';
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-chart-line me-2"></i>Analyze Content';
    }

    function updateStatus(message) {
        statusText.textContent = message;
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'block';
        errorAlert.scrollIntoView({ behavior: 'smooth' });
    }

    function hideError() {
        errorAlert.style.display = 'none';
    }

    function hideResults() {
        results.style.display = 'none';
    }

    function hideWelcome() {
        welcomeMessage.style.display = 'none';
    }

    function displayResults(data) {
        // Update summary cards
        document.getElementById('totalContent').textContent = data.total_content_analyzed;
        document.getElementById('painPointsCount').textContent = data.pain_points.length;
        document.getElementById('featuresCount').textContent = data.product_features.length;

        // Display pain points
        displayPainPoints(data.pain_points);

        // Display product features
        displayProductFeatures(data.product_features);

        // Display sentiment analysis
        displaySentimentAnalysis(data.sentiment_summary, data.keyword_frequency);

        // Display sample content
        displaySampleContent(data.sample_content);

        // Show results with animation
        results.style.display = 'block';
        results.classList.add('fade-in');
        results.scrollIntoView({ behavior: 'smooth' });
    }

    function displayPainPoints(painPoints) {
        const container = document.getElementById('painPointsList');
        container.innerHTML = '';

        if (painPoints.length === 0) {
            container.innerHTML = '<p class="text-muted">No specific pain points identified in the analyzed content.</p>';
            return;
        }

        painPoints.forEach((point, index) => {
            const pointElement = document.createElement('div');
            pointElement.className = 'pain-point-item';
            pointElement.innerHTML = `
                <div class="d-flex align-items-start">
                    <span class="badge bg-danger me-3 mt-1">${index + 1}</span>
                    <div>
                        <p class="mb-0">${escapeHtml(point)}</p>
                    </div>
                </div>
            `;
            container.appendChild(pointElement);
        });
    }

    function displayProductFeatures(features) {
        const container = document.getElementById('featuresList');
        container.innerHTML = '';

        if (features.length === 0) {
            container.innerHTML = '<p class="text-muted">No specific product features mentioned in the analyzed content.</p>';
            return;
        }

        features.forEach((feature, index) => {
            const featureElement = document.createElement('div');
            featureElement.className = 'feature-item';
            featureElement.innerHTML = `
                <div class="d-flex align-items-start">
                    <span class="badge bg-success me-3 mt-1">${index + 1}</span>
                    <div>
                        <p class="mb-0">${escapeHtml(feature)}</p>
                    </div>
                </div>
            `;
            container.appendChild(featureElement);
        });
    }

    function displaySentimentAnalysis(sentimentSummary, keywordFrequency) {
        // Sentiment summary
        const sentimentContainer = document.getElementById('sentimentSummary');
        sentimentContainer.innerHTML = `
            <div class="sentiment-card">
                <p class="mb-0">${escapeHtml(sentimentSummary)}</p>
            </div>
        `;

        // Keyword frequency
        const frequencyContainer = document.getElementById('keywordFrequency');
        frequencyContainer.innerHTML = '';

        const frequencyEntries = Object.entries(keywordFrequency).slice(0, 15);
        
        if (frequencyEntries.length === 0) {
            frequencyContainer.innerHTML = '<p class="text-muted">No keyword frequency data available.</p>';
            return;
        }

        frequencyEntries.forEach(([word, count]) => {
            const freqElement = document.createElement('span');
            freqElement.className = 'keyword-frequency-item';
            freqElement.textContent = `${word} (${count})`;
            frequencyContainer.appendChild(freqElement);
        });
    }

    function displaySampleContent(sampleContent) {
        const container = document.getElementById('sampleContent');
        container.innerHTML = '';

        if (sampleContent.length === 0) {
            container.innerHTML = '<p class="text-muted">No sample content available.</p>';
            return;
        }

        sampleContent.forEach((content, index) => {
            const contentElement = document.createElement('div');
            contentElement.className = 'content-item';
            contentElement.innerHTML = `
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-1">${escapeHtml(content.title)}</h6>
                    <div>
                        <span class="subreddit-badge me-2">r/${escapeHtml(content.subreddit)}</span>
                        <span class="score-badge">↑ ${content.score}</span>
                    </div>
                </div>
                <p class="text-muted mb-2">${escapeHtml(content.content)}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                        <i class="fas fa-${content.type === 'post' ? 'file-text' : 'comment'} me-1"></i>
                        ${content.type.charAt(0).toUpperCase() + content.type.slice(1)}
                    </small>
                    <a href="${escapeHtml(content.url)}" target="_blank" rel="noopener" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-external-link-alt me-1"></i>View on Reddit
                    </a>
                </div>
            `;
            container.appendChild(contentElement);
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Add some example keywords for user guidance
    const keywordInput = document.getElementById('keyword');
    const examples = [
        'productivity app',
        'smartphone battery',
        'video game',
        'social media',
        'online learning',
        'fitness tracker',
        'streaming service',
        'food delivery'
    ];

    // Cycle through examples as placeholder
    let exampleIndex = 0;
    setInterval(() => {
        if (keywordInput.value === '') {
            keywordInput.placeholder = `e.g., ${examples[exampleIndex]}`;
            exampleIndex = (exampleIndex + 1) % examples.length;
        }
    }, 3000);

    // Add keyboard shortcut for analysis
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (!analyzeBtn.disabled) {
                form.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Add auto-resize to text areas if any
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});