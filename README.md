# WhatsApp Chat Analyzer

A Python tool for analyzing WhatsApp chat exports, providing detailed statistics, word frequency analysis, and visualizations.
This is the streamlit branch, there is an online working version (DO NOT SHARE SENSITIVE DATA) or you can run it locally  


## Features

- **Message Statistics**: Total messages, words, and activity patterns
- **Word Frequency Analysis**: Most commonly used words overall and per person
- **Per-Person Analytics**: Individual chat statistics and usage patterns
- **Temporal Analysis**: Monthly breakdowns and hourly activity patterns
- **Data Visualizations**: Charts and word clouds
- **Comprehensive Reports**: Detailed text output with all analysis results


# Online app - Streamlit link
https://chat-analyzer-with-graphs.streamlit.app/

* PLEASE NOTICE, DO NOT SHARE SENSITIVE INFORMATION
* IT SHOULD ALL RUN LOCALLY ON YOUR BROWSER, BUT I AM NOT RESPONSIBLE FOR STREAMLIT DOING SOMETHING TO INPUTTED DATA
* IF YOU WANT TO BE 100 PERCENT SURE, DOWNLOAD GITHUB REPOSITORY AND RUN LOCALLY OR USE THE BRANCH NOT FOR STREAMLIT :)
* On Streamlit Cloud, uploaded files may be temporarily stored on Streamlit’s servers. For sensitive data, run this app locally
* AGAIN, THE CREATOR OF THIS APP TAKES NO RESPONSABILITY IN SENSITIVE DATA SHARED BEING USED BY STREAMLIT

# Running it locally 
```bash
streamlit run analyzer.py
```


## Requirements

### Python Dependencies
streamlit
matplotlib
seaborn
pandas
numpy
plotly
wordcloud
statsmodels

### Input File Format
The script expects a WhatsApp chat export file in standard text format. To export your WhatsApp chat:

1. **Android**: Open chat → Menu (⋮) → More → Export chat → Without Media
2. **iPhone**: Open chat → Contact/Group name → Export Chat → Without Media

The exported file should contain messages in this format:
```
[DD/MM/YYYY, HH:MM:SS] Contact Name: Message text
[DD/MM/YYYY, HH:MM:SS] Another Person: Another message
```

## Usage
Upload your chat file or click on the demo button to check out a demo chat

### Analysis Results
- **Message Statistics**: Total counts, averages per day/month
- **Word Analysis**: Most common words with frequency counts
- **Person Breakdown**: Individual statistics for each chat participant
- **Activity Patterns**: Peak hours and monthly trends


## Privacy & Data Security
- PLEASE NOTICE, DO NOT SHARE SENSITIVE INFORMATION
- IT SHOULD ALL RUN LOCALLY ON YOUR BROWSER, BUT I AM NOT RESPONSIBLE FOR STREAMLIT DOING SOMETHING TO INPUTTED DATA
- IF YOU WANT TO BE 100 PERCENT SURE, DOWNLOAD GITHUB REPOSITORY AND RUN LOCALLY OR USE THE BRANCH NOT FOR STREAMLIT :)
- On Streamlit Cloud, uploaded files may be temporarily stored on Streamlit’s servers. For sensitive data, run this app locally
- AGAIN, THE CREATOR OF THIS APP TAKES NO RESPONSABILITY IN SENSITIVE DATA SHARED BEING USED BY STREAMLIT

---

**Note**: This tool is for personal use and analysis. Always respect privacy and obtain necessary permissions before analyzing chat data involving other people.