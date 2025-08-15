# Modern Blackboard Scraper

A Python-based web scraper for extracting course information and grades from Blackboard Learn. This tool is designed to work with modern Blackboard installations and provides both automatic and manual login options.

## Features

- **Modern Selenium Implementation**: Uses current Selenium syntax and best practices
- **Flexible Login**: Supports both automatic and manual login methods
- **Course Discovery**: Automatically finds and navigates to available courses
- **Grade Extraction**: Attempts to access and extract grade information
- **Content Mapping**: Maps course structure and navigation elements
- **Robust Error Handling**: Graceful fallbacks when automatic detection fails
- **Data Export**: Saves all scraped data to JSON format
- **Multiple Browser Support**: Works with Chrome and Firefox

## Prerequisites

- Python 3.8 or higher
- Chrome or Firefox browser installed
- Appropriate WebDriver (ChromeDriver or GeckoDriver)

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download the appropriate WebDriver:
   - **Chrome**: Download [ChromeDriver](https://chromedriver.chromium.org/) and add to PATH
   - **Firefox**: Download [GeckoDriver](https://github.com/mozilla/geckodriver/releases) and add to PATH

## Usage

### Basic Usage

```bash
python scrape.py "https://your-university.blackboard.com"
```

### With Automatic Login

```bash
python scrape.py "https://your-university.blackboard.com" --username "your_username" --password "your_password"
```

### Advanced Options

```bash
python scrape.py "https://your-university.blackboard.com" \
    --username "your_username" \
    --password "your_password" \
    --browser chrome \
    --headless \
    --output "my_grades.json"
```

### Command Line Arguments

- `url`: Blackboard base URL (required)
- `--username`: Username for automatic login
- `--password`: Password for automatic login
- `--browser`: Browser to use (chrome or firefox, default: chrome)
- `--headless`: Run in headless mode (no visible browser window)
- `--output`: Output JSON filename (default: blackboard_data.json)

## How It Works

1. **Initialization**: Sets up the appropriate WebDriver with browser options
2. **Login**: Attempts automatic login or falls back to manual login
3. **Course Discovery**: Searches for available courses using multiple selector strategies
4. **Content Mapping**: For each course, maps the navigation structure and content areas
5. **Grade Access**: Attempts to navigate to and extract grade information
6. **Data Export**: Saves all collected data to a JSON file

## Output Format

The scraper generates a JSON file with the following structure:

```json
{
  "scraped_at": "2025-01-XX...",
  "courses": [
    {
      "name": "Course Name",
      "url": "course_url",
      "content": {
        "menu_items": [...],
        "content_items": [...]
      },
      "grades": {
        "grades": [...],
        "page_title": "...",
        "url": "..."
      }
    }
  ],
  "grades": {
    "Course Name": {...}
  }
}
```

## Troubleshooting

### Common Issues

1. **WebDriver Not Found**: Ensure ChromeDriver/GeckoDriver is in your PATH
2. **Login Fails**: Use manual login mode if automatic detection fails
3. **No Courses Found**: The scraper will prompt you to navigate manually
4. **Grades Not Accessible**: Some institutions restrict grade access

### Manual Override

If automatic detection fails, the scraper will prompt you to:
- Log in manually
- Navigate to course lists manually
- Navigate to grades pages manually

Simply follow the prompts and press Enter when ready to continue.

## Security Notes

- **Never commit credentials** to version control
- **Use environment variables** for production deployments
- **Respect rate limits** and be mindful of server load
- **Check your institution's terms of service** regarding automated access

## Legal and Ethical Considerations

- This tool is for educational and personal use only
- Respect your institution's terms of service
- Do not use for commercial purposes
- Be mindful of server load and rate limiting
- Ensure you have permission to access the data you're scraping

## Contributing

Feel free to submit issues and enhancement requests. When contributing:

1. Test with multiple Blackboard installations
2. Add appropriate error handling
3. Update documentation for any new features
4. Follow existing code style and patterns

## License

This project is provided as-is for educational purposes. Please ensure compliance with your institution's terms of service and applicable laws.

## Disclaimer

This tool is not affiliated with Blackboard Inc. or any educational institution. Use at your own risk and ensure compliance with all applicable terms of service and laws.