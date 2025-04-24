# AI Newsletter System

An automated newsletter system that curates and delivers the latest news about AI and digital transformation using the Perplexity AI API.

## Features

- Automated news curation using Perplexity AI API
- Customizable topics for news gathering
- Relevance scoring for news items
- Beautiful HTML email template
- Configurable email delivery
- Error handling and logging

## Setup

1. Clone the repository:
```bash
git clone https://github.com/hanovamx/ai_newsletter.git
cd ai_newsletter
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your credentials:
```bash
PERPLEXITY_API_KEY=your_key_here
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient1@email.com,recipient2@email.com
EMAIL_PASSWORD=your_app_specific_password
```

Note: For Gmail, use an App-Specific Password instead of your regular password.

## Usage

Run the newsletter system:
```bash
python src/main.py
```

For testing:
```bash
python test_local.py
```

## Configuration

The system monitors the following topics:
- Digital transformation
- Enterprise AI
- Cloud computing
- Cybersecurity
- Data analytics

You can modify the topics and other settings in the configuration file.

## Deployment

The system can be deployed on any server with Python 3.11+ installed. For production use:

1. Set up a cron job to run the script periodically
2. Configure proper logging
3. Set up monitoring for the process

Example cron job (runs every Monday at 8 AM):
```bash
0 8 * * 1 cd /path/to/ai_newsletter && source venv/bin/activate && python src/main.py
```

## License

MIT License 