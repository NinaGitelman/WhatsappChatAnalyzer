# WhatsApp Chat Analyzer

A Python tool for analyzing WhatsApp chat exports, providing detailed statistics, word frequency analysis, and visualizations.

## Features

- **Message Statistics**: Total messages, words, and activity patterns
- **Word Frequency Analysis**: Most commonly used words overall and per person
- **Per-Person Analytics**: Individual chat statistics and usage patterns
- **Temporal Analysis**: Monthly breakdowns and hourly activity patterns
- **Data Visualizations**: Charts and word clouds
- **Comprehensive Reports**: Detailed text output with all analysis results

## Requirements

### Python Dependencies
```bash
pip install matplotlib
pip install wordcloud
pip install pandas
pip install numpy
```

### Input File Format
The script expects a WhatsApp chat export file in standard text format. To export your WhatsApp chat:

1. **Android**: Open chat → Menu (⋮) → More → Export chat → Without Media
2. **iPhone**: Open chat → Contact/Group name → Export Chat → Without Media

The exported file should contain messages in this format:
```
[DD/MM/YYYY, HH:MM:SS] Contact Name: Message text
[DD/MM/YYYY, HH:MM:SS] Another Person: Another message
```

## Installation & Setup

1. Clone or download the script files
2. Install required dependencies:
   ```bash
   pip install matplotlib wordcloud pandas numpy
   ```
3. Place your WhatsApp chat export file in the same directory as the script
4. Update the file path in the script if needed

## Usage

### Basic Usage
1. Name your chat export file `test_chat.txt` (or update `FILE_PATH` in the script)
2. Run the script:
   ```bash
   python whatsapp_analyzer.py
   ```

### Customizing File Paths
Edit these variables at the top of the script:
```python
FILE_PATH = "your_chat_file.txt"    # Your chat export file
OUTPUT_DIR = "output"                # Output directory for results
```

## Output Files

The script generates several output files in the specified output directory:

### 1. `chat_analysis_results.txt`
Comprehensive text report containing:
- Overall chat statistics
- Per-person message and word counts
- Top 10 most used words (overall and per person)
- Hourly activity patterns
- Monthly breakdown with word frequency analysis

### 2. `chat_analysis_dashboard.png`
Visual dashboard with multiple charts showing:
- Messages over time
- Activity by hour of day
- Message distribution by person
- Word frequency trends

### 3. `word_cloud.png`
Word cloud visualization highlighting the most frequently used words in the chat.

## Sample Output

### Console Output
```
Analyzing chat transcript: test_chat.txt
Processing...

OVERALL STATISTICS
==================
Total messages: 15,432
Total words analyzed: 89,234
Total months analyzed: 18
Number of people in chat: 3

Generating visualizations...
Results saved to: output/chat_analysis_results.txt
```

### Analysis Results
- **Message Statistics**: Total counts, averages per day/month
- **Word Analysis**: Most common words with frequency counts
- **Person Breakdown**: Individual statistics for each chat participant
- **Activity Patterns**: Peak hours and monthly trends

## Configuration

### Customizing Analysis
You can modify the script to:
- Change the number of top words displayed (default: 10)
- Filter out specific words or phrases
- Adjust date/time parsing for different WhatsApp export formats
- Modify visualization styles and colors

## Troubleshooting

### Common Issues

**"No messages found or error reading file"**
- Check that your chat export file exists and is in the correct format
- Ensure the file path in `FILE_PATH` is correct
- Verify the file isn't empty or corrupted

**Permission/Path Errors**
- Ensure you have write permissions in the output directory
- Check that the output path doesn't contain invalid characters
- Try using a different output directory

**Missing Dependencies**
- Install required packages: `pip install matplotlib wordcloud pandas numpy`
- Check Python version compatibility (Python 3.6+)

**Encoding Issues**
- Ensure your chat export file is saved in UTF-8 encoding
- Some special characters might need additional handling

### Performance Notes
- Large chat files (>100MB) may take several minutes to process
- Memory usage scales with chat size - very large chats may require additional RAM
- Visualization generation is typically the slowest part of the process

## Privacy & Data Security

- This tool processes chat data locally on your machine
- No data is sent to external servers or services
- All analysis is performed offline
- Consider the sensitivity of your chat data when sharing results


---

**Note**: This tool is for personal use and analysis. Always respect privacy and obtain necessary permissions before analyzing chat data involving other people.