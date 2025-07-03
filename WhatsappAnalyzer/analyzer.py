import os
import re
from collections import defaultdict, Counter
from datetime import datetime
import string
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import streamlit as st


def is_system_message(line):
    whatsapp_phrases = ["<Media omitted>", "You deleted this message", "This message was edited",
                        "This message was deleted"]
    for phrase in whatsapp_phrases:
        if phrase in line:
            return True
    return False


def parse_chat_transcript(lines):
    """
    Parse the chat transcript and return organized data including per-person statistics.
    Takes a list of lines from an uploaded WhatsApp .txt file.
    """

    monthly_messages = defaultdict(list)
    hourly_messages = defaultdict(int)
    person_messages = defaultdict(list)
    person_monthly_messages = defaultdict(lambda: defaultdict(list))
    person_message_counts = defaultdict(int)

    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)'

    for line in lines:
        line = line.strip()
        if not line or is_system_message(line):
            continue

        match = re.match(pattern, line)
        if match:
            date_str, time_str, name, message = match.groups()
            name = name.strip()

            # Parse the date
            try:
                date = datetime.strptime(date_str, '%m/%d/%y')
            except ValueError:
                try:
                    date = datetime.strptime(date_str, '%m/%d/%Y')
                except ValueError:
                    continue

            # Parse time for hour
            try:
                time_obj = datetime.strptime(time_str, '%H:%M')
                hour = time_obj.hour
                hourly_messages[hour] += 1
            except ValueError:
                continue

            month_key = date.strftime('%Y-%m')

            monthly_messages[month_key].append(message)
            person_messages[name].append(message)
            person_monthly_messages[name][month_key].append(message)
            person_message_counts[name] += 1

    return monthly_messages, hourly_messages, person_messages, person_monthly_messages, person_message_counts


def clean_and_tokenize(text):
    """
    Clean the text and return a list of words, excluding WhatsApp system words.
    """

    # Convert to lowercase and clean whitespace
    text_clean = text.lower().strip()

    # Remove punctuation
    text = text_clean.translate(str.maketrans('', '', string.punctuation))

    # Split into words and filter out WhatsApp stop words and short words
    words = [word for word in text.split()
             if len(word) > 2 and word.isalpha()]

    return words


def analyze_monthly_word_frequency(monthly_messages):
    """
    Analyze word frequency for each month and return top 10 words per month.
    """
    monthly_analysis = {}

    for month, messages in monthly_messages.items():
        # Combine all messages for the month
        all_text = ' '.join(messages)

        # Clean and tokenize (this will exclude WhatsApp system words)
        words = clean_and_tokenize(all_text)

        # Count word frequencies
        word_counts = Counter(words)

        # Get top 10 most common words
        top_words = word_counts.most_common(10)

        monthly_analysis[month] = {
            'total_messages': len(messages),  # Count ALL messages including system messages
            'total_words': len(words),  # Count only meaningful words
            'top_words': top_words
        }

    return monthly_analysis


def analyze_person_statistics(person_messages, person_message_counts):
    """
    Analyze statistics for each person including their most used words.
    """
    person_analysis = {}

    for person, messages in person_messages.items():
        # Combine all messages for the person
        all_text = ' '.join(messages)

        # Clean and tokenize (excludes WhatsApp system words)
        words = clean_and_tokenize(all_text)

        # Count word frequencies
        word_counts = Counter(words)

        # Get top 10 most common words for this person
        top_words = word_counts.most_common(10)

        person_analysis[person] = {
            'total_messages': person_message_counts[person],  # Count ALL messages
            'total_words': len(words),  # Count only meaningful words
            'top_words': top_words,
            'avg_words_per_message': len(words) / person_message_counts[person] if person_message_counts[
                                                                                       person] > 0 else 0
        }

    return person_analysis


def analyze_overall_statistics(monthly_messages, person_message_counts):
    """
    Analyze overall chat statistics including top words across all months.
    """
    # Combine all messages from all months
    all_messages = []
    for messages in monthly_messages.values():
        all_messages.extend(messages)

    # Combine all text
    all_text = ' '.join(all_messages)

    # Clean and tokenize all text (excludes WhatsApp system words)
    all_words = clean_and_tokenize(all_text)

    # Count word frequencies
    overall_word_counts = Counter(all_words)

    # Get top 10 most common words overall
    top_overall_words = overall_word_counts.most_common(10)

    # Calculate time span
    sorted_months = sorted(monthly_messages.keys())
    if len(sorted_months) >= 2:
        start_date = datetime.strptime(sorted_months[0], '%Y-%m')
        end_date = datetime.strptime(sorted_months[-1], '%Y-%m')
        # Calculate approximate days (assuming average 30.4 days per month)
        months_diff = len(sorted_months)
        total_days = months_diff * 30.4
    else:
        total_days = 30.4  # Default to 1 month if only one month

    # Calculate averages
    total_messages = sum(len(messages) for messages in monthly_messages.values())
    total_words = len(all_words)

    avg_messages_per_month = total_messages / len(sorted_months) if sorted_months else 0
    avg_words_per_month = total_words / len(sorted_months) if sorted_months else 0
    avg_messages_per_day = total_messages / total_days if total_days > 0 else 0
    avg_words_per_day = total_words / total_days if total_days > 0 else 0

    return {
        'total_messages': total_messages,
        'total_words': total_words,
        'total_months': len(sorted_months),
        'total_days': int(total_days),
        'top_overall_words': top_overall_words,
        'avg_messages_per_month': avg_messages_per_month,
        'avg_words_per_month': avg_words_per_month,
        'avg_messages_per_day': avg_messages_per_day,
        'avg_words_per_day': avg_words_per_day,
        'all_words': all_words,
        'overall_word_counts': overall_word_counts
    }


def create_visualizations(monthly_analysis, overall_stats, hourly_messages, person_analysis):
    """
    Create various visualizations of the chat data including per-person statistics.
    """
    # Set style for better-looking plots
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")

    # Create figure with subplots
    fig = plt.figure(figsize=(24, 28))

    # Prepare data for plotting
    sorted_months = sorted(monthly_analysis.keys())
    month_dates = [datetime.strptime(month, '%Y-%m') for month in sorted_months]
    messages_per_month = [monthly_analysis[month]['total_messages'] for month in sorted_months]
    words_per_month = [monthly_analysis[month]['total_words'] for month in sorted_months]
    month_labels = [date.strftime('%b %Y') for date in month_dates]

    # 1. Messages per Month (Line Chart)
    plt.subplot(4, 3, 1)
    plt.plot(month_dates, messages_per_month, marker='o', linewidth=2, markersize=6)
    plt.title('Messages per Month', fontsize=14, fontweight='bold')
    plt.xlabel('Month')
    plt.ylabel('Number of Messages')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    # 2. Words per Month (Bar Chart)
    plt.subplot(4, 3, 2)
    bars = plt.bar(range(len(month_labels)), words_per_month, alpha=0.7)
    plt.title('Words per Month', fontsize=14, fontweight='bold')
    plt.xlabel('Month')
    plt.ylabel('Number of Words')
    plt.xticks(range(len(month_labels)), month_labels, rotation=45)
    plt.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + max(words_per_month) * 0.01,
                 f'{int(height):,}', ha='center', va='bottom', fontsize=8)

    # 3. Top 10 Overall Words (Horizontal Bar Chart)
    plt.subplot(4, 3, 3)
    words = [word for word, count in overall_stats['top_overall_words']]
    counts = [count for word, count in overall_stats['top_overall_words']]
    y_pos = range(len(words))

    bars = plt.barh(y_pos, counts, alpha=0.7)
    plt.title('Top 10 Most Used Words (Overall)', fontsize=14, fontweight='bold')
    plt.xlabel('Frequency')
    plt.yticks(y_pos, words)
    plt.gca().invert_yaxis()
    plt.grid(True, alpha=0.3, axis='x')

    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width + max(counts) * 0.01, bar.get_y() + bar.get_height() / 2.,
                 f'{int(width):,}', ha='left', va='center', fontsize=9)

    # 4. Messages vs Words Correlation
    plt.subplot(4, 3, 4)
    plt.scatter(messages_per_month, words_per_month, alpha=0.7, s=60)
    plt.title('Messages vs Words per Month', fontsize=14, fontweight='bold')
    plt.xlabel('Messages per Month')
    plt.ylabel('Words per Month')
    plt.grid(True, alpha=0.3)

    # Add trend line
    if len(messages_per_month) > 1:
        z = np.polyfit(messages_per_month, words_per_month, 1)
        p = np.poly1d(z)
        plt.plot(messages_per_month, p(messages_per_month), "r--", alpha=0.8)

    # 5. Messages by Hour of Day
    plt.subplot(4, 3, 5)
    hours = sorted(hourly_messages.keys())
    hour_counts = [hourly_messages[hour] for hour in hours]

    bars = plt.bar(hours, hour_counts, alpha=0.7, color='orange')
    plt.title('Messages by Hour of Day', fontsize=14, fontweight='bold')
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of Messages')
    plt.xticks(hours[::2], [f"{hour:02d}:00" for hour in hours[::2]], rotation=45)
    plt.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars for peak hours
    max_count = max(hour_counts) if hour_counts else 0
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if height > max_count * 0.7:
            plt.text(bar.get_x() + bar.get_width() / 2., height + max_count * 0.01,
                     f'{int(height):,}', ha='center', va='bottom', fontsize=8)

    # 6. Average Words per Message
    plt.subplot(4, 3, 6)
    avg_words_per_msg = [words_per_month[i] / messages_per_month[i] if messages_per_month[i] > 0 else 0
                         for i in range(len(messages_per_month))]

    plt.plot(month_dates, avg_words_per_msg, marker='s', linewidth=2, markersize=6, color='green')
    plt.title('Average Words per Message', fontsize=14, fontweight='bold')
    plt.xlabel('Month')
    plt.ylabel('Words per Message')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    # 7. Messages per Person (Bar Chart)
    plt.subplot(4, 3, 7)
    person_names = list(person_analysis.keys())
    person_message_counts = [person_analysis[person]['total_messages'] for person in person_names]

    bars = plt.bar(range(len(person_names)), person_message_counts, alpha=0.7, color='purple')
    plt.title('Total Messages per Person', fontsize=14, fontweight='bold')
    plt.xlabel('Person')
    plt.ylabel('Number of Messages')
    plt.xticks(range(len(person_names)), person_names, rotation=45)
    plt.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + max(person_message_counts) * 0.01,
                 f'{int(height):,}', ha='center', va='bottom', fontsize=8)

    # 8. Words per Person (Bar Chart)
    plt.subplot(4, 3, 8)
    person_word_counts = [person_analysis[person]['total_words'] for person in person_names]

    bars = plt.bar(range(len(person_names)), person_word_counts, alpha=0.7, color='teal')
    plt.title('Total Words per Person', fontsize=14, fontweight='bold')
    plt.xlabel('Person')
    plt.ylabel('Number of Words')
    plt.xticks(range(len(person_names)), person_names, rotation=45)
    plt.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + max(person_word_counts) * 0.01,
                 f'{int(height):,}', ha='center', va='bottom', fontsize=8)

    # 9. Average Words per Message by Person
    plt.subplot(4, 3, 9)
    person_avg_words = [person_analysis[person]['avg_words_per_message'] for person in person_names]

    bars = plt.bar(range(len(person_names)), person_avg_words, alpha=0.7, color='coral')
    plt.title('Average Words per Message by Person', fontsize=14, fontweight='bold')
    plt.xlabel('Person')
    plt.ylabel('Average Words per Message')
    plt.xticks(range(len(person_names)), person_names, rotation=45)
    plt.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + max(person_avg_words) * 0.01,
                 f'{height:.1f}', ha='center', va='bottom', fontsize=8)

    # 10. Cumulative Messages Over Time
    plt.subplot(4, 3, 10)
    cumulative_messages = np.cumsum(messages_per_month)
    plt.plot(month_dates, cumulative_messages, marker='o', linewidth=3, markersize=6, color='purple')
    plt.fill_between(month_dates, cumulative_messages, alpha=0.3, color='purple')
    plt.title('Cumulative Messages Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Month')
    plt.ylabel('Cumulative Messages')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    # 11. Message Share by Person (Pie Chart)
    plt.subplot(4, 3, 11)
    colors = plt.cm.Set3(np.linspace(0, 1, len(person_names)))
    wedges, texts, autotexts = plt.pie(person_message_counts, labels=person_names, autopct='%1.1f%%',
                                       colors=colors, startangle=90)
    plt.title('Message Share by Person', fontsize=14, fontweight='bold')

    # 12. Summary Statistics Box
    plt.subplot(4, 3, 12)
    plt.axis('off')

    # Find peak hour
    peak_hour = max(hourly_messages.keys(), key=lambda k: hourly_messages[k]) if hourly_messages else 0
    peak_hour_count = hourly_messages[peak_hour] if hourly_messages else 0

    # Find most active person
    most_active_person = max(person_analysis.keys(),
                             key=lambda k: person_analysis[k]['total_messages']) if person_analysis else "N/A"
    most_active_count = person_analysis[most_active_person]['total_messages'] if person_analysis else 0

    # Create summary text
    summary_text = f"""
    CHAT SUMMARY STATISTICS

    Total Messages: {overall_stats['total_messages']:,}
    Total Words: {overall_stats['total_words']:,}
    Months Analyzed: {overall_stats['total_months']}
    People in Chat: {len(person_analysis)}

    AVERAGES:
    • Messages/Month: {overall_stats['avg_messages_per_month']:.1f}
    • Words/Month: {overall_stats['avg_words_per_month']:.1f}
    • Messages/Day: {overall_stats['avg_messages_per_day']:.1f}
    • Words/Day: {overall_stats['avg_words_per_day']:.1f}

    TOP WORD: "{overall_stats['top_overall_words'][0][0]}"
    Used {overall_stats['top_overall_words'][0][1]:,} times

    PEAK HOUR: {peak_hour:02d}:00
    {peak_hour_count:,} messages

    MOST ACTIVE: {most_active_person}
    {most_active_count:,} messages
    """

    plt.text(0.1, 0.9, summary_text, transform=plt.gca().transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

    plt.tight_layout()
    st.pyplot(fig)

    # Create Word Cloud
    try:
        plt.figure(figsize=(12, 8))

        # Prepare text for word cloud
        word_freq_dict = dict(overall_stats['top_overall_words'][:50])  # Top 50 words for better cloud

        wordcloud = WordCloud(width=1200, height=800,
                              background_color='white',
                              max_words=50,
                              colormap='viridis',
                              relative_scaling=0.5).generate_from_frequencies(word_freq_dict)

        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Word Cloud - Most Frequently Used Words', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()

        st.pyplot(plt.gcf())

    except Exception as e:
        st.write(f"Note: Could not generate word cloud. Install wordcloud package: pip install wordcloud")
        st.write(f"Error: {e}")


def print_analysis(monthly_analysis, overall_stats, hourly_messages, person_analysis):
    """
    Print the analysis results in a formatted way including per-person statistics.
    """
    st.write("=" * 80)
    st.write("CHAT TRANSCRIPT WORD FREQUENCY ANALYSIS")
    st.write("=" * 80)

    # Print overall statistics first
    st.write("\n🌟 OVERALL STATISTICS")
    st.write("=" * 50)
    st.write(f"Total messages: {overall_stats['total_messages']:,}")
    st.write(f"Total words analyzed: {overall_stats['total_words']:,}")
    st.write(f"Total months analyzed: {overall_stats['total_months']}")
    st.write(f"Approximate total days: {overall_stats['total_days']}")
    st.write(f"Number of people in chat: {len(person_analysis)}")
    st.write()
    st.write("📊 AVERAGES:")
    st.write(f"Average messages per month: {overall_stats['avg_messages_per_month']:.1f}")
    st.write(f"Average words per month: {overall_stats['avg_words_per_month']:.1f}")
    st.write(f"Average messages per day: {overall_stats['avg_messages_per_day']:.1f}")
    st.write(f"Average words per day: {overall_stats['avg_words_per_day']:.1f}")
    st.write()
    st.write("🏆 TOP 10 MOST USED WORDS (OVERALL):")
    for i, (word, count) in enumerate(overall_stats['top_overall_words'], 1):
        st.write(f"{i:2d}. {word:<15} ({count:,} times)")

    # Print per-person statistics
    st.write("\n" + "=" * 80)
    st.write("PER-PERSON STATISTICS")
    st.write("=" * 80)

    # Sort people by message count (descending)
    sorted_people = sorted(person_analysis.items(), key=lambda x: x[1]['total_messages'], reverse=True)

    for person, data in sorted_people:
        st.write(f"\n👤 {person}")
        st.write("-" * 50)
        st.write(f"Total messages: {data['total_messages']:,}")
        st.write(f"Total words: {data['total_words']:,}")
        st.write(f"Average words per message: {data['avg_words_per_message']:.1f}")
        st.write(f"Message share: {(data['total_messages'] / overall_stats['total_messages'] * 100):.1f}%")
        st.write("\nTop 10 most used words:")

        for i, (word, count) in enumerate(data['top_words'], 1):
            st.write(f"{i:2d}. {word:<15} ({count:,} times)")

    # Print hourly analysis
    if hourly_messages:
        st.write("\n🕐 HOURLY ACTIVITY:")
        st.write("=" * 50)
        sorted_hours = sorted(hourly_messages.keys())
        peak_hour = max(hourly_messages.keys(), key=lambda k: hourly_messages[k])
        st.write(f"Most active hour: {peak_hour:02d}:00 ({hourly_messages[peak_hour]:,} messages)")
        st.write("\nMessages by hour:")
        for hour in sorted_hours:
            st.write(f"{hour:02d}:00 - {hourly_messages[hour]:,} messages")

    st.write("\n" + "=" * 80)
    st.write("MONTHLY BREAKDOWN")
    st.write("=" * 80)

    # Sort months chronologically
    sorted_months = sorted(monthly_analysis.keys())

    for month in sorted_months:
        data = monthly_analysis[month]

        # Convert month to readable format
        month_obj = datetime.strptime(month, '%Y-%m')
        readable_month = month_obj.strftime('%B %Y')

        st.write(f"\n📅 {readable_month}")
        st.write("-" * 40)
        st.write(f"Total messages: {data['total_messages']:,}")
        st.write(f"Total words analyzed: {data['total_words']:,}")
        st.write("\nTop 10 most used words:")

        for i, (word, count) in enumerate(data['top_words'], 1):
            st.write(f"{i:2d}. {word:<15} ({count:,} times)")

        st.write()



def start_analysis(lines):
    monthly_messages, hourly_messages, person_messages, person_monthly_messages, person_message_counts = parse_chat_transcript(
        lines)

    if not monthly_messages:
        st.write("No messages found or error reading file.")
        return

    # Analyze word frequency
    monthly_analysis = analyze_monthly_word_frequency(monthly_messages)

    # Analyze per-person statistics
    person_analysis = analyze_person_statistics(person_messages, person_message_counts)

    # Analyze overall statistics
    overall_stats = analyze_overall_statistics(monthly_messages, person_message_counts)

    # Print results
    print_analysis(monthly_analysis, overall_stats, hourly_messages, person_analysis)

    # Create visualizations
    st.write("\nGenerating visualizations...")
    create_visualizations(monthly_analysis, overall_stats, hourly_messages, person_analysis)


def main():
    """
    Main function to run the chat analysis.
    """
    # file_path = FILE_PATH
    # output_dir = OUTPUT_DIR

    # Create output directory if it doesn't exist
    # os.makedirs(output_dir, exist_ok=True)



    st.title("📱 WhatsApp Chat Analyzer")
    st.write("")
    st.write("")
    st.warning("PLEASE NOTICE, DO NOT SHARE SENSITIVE INFORMATION.")
    st.warning("IT SHOULD ALL RUN LOCALLY ON YOUR BROWSER, BUT I AM NOT RESPONSIBLE FOR STREAMLIT DOING SOMETHING TO INPUTTED DATA")
    st.warning("IF YOU WANT TO BE 100 PERCENT SURE, DOWNLOAD GITHUB REPOSITORY AND RUN LOCALLY OR USE THE BRANCH NOT FOR STREAMLIT :))")
    st.warning("On Streamlit Cloud, uploaded files may be temporarily stored on Streamlit’s servers. For sensitive data, run this app locally")
    st.warning("AGAIN, THE CREATOR OF THIS APP TAKES NO RESPONSABILITY IN SENSITIVE DATA SHARED BEING USED BY STREAMLIT")
    st.write("for demo - click use demo file button")
    st.write("")
    st.write("")

    st.title("Start Analysis: ")

    uploaded_file = st.file_uploader("Upload WhatsApp Chat (.txt)", type="txt")
    lines = None
    if uploaded_file:
        lines = uploaded_file.getvalue().decode("utf-8").splitlines()
    else:
        st.write("Please upload a whatsapp chat export without media :)")
        use_demo = st.button("or use Demo File")
        if use_demo:
            try:
                with open("test_chat.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except FileNotFoundError:
                st.error("Error loading demo chat :(")

    if lines:
        start_analysis(lines)
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.warning("PLEASE NOTICE, DO NOT SHARE SENSITIVE INFORMATION.")
    st.warning("IT SHOULD ALL RUN LOCALLY ON YOUR BROWSER, BUT I AM NOT RESPONSIBLE FOR STREAMLIT DOING SOMETHING TO INPUTTED DATA")
    st.warning("IF YOU WANT TO BE 100 PERCENT SURE, DOWNLOAD GITHUB REPOSITORY AND RUN LOCALLY OR USE THE BRANCH NOT FOR STREAMLIT :))")
    st.warning("On Streamlit Cloud, uploaded files may be temporarily stored on Streamlit’s servers. For sensitive data, run this app locally")
    st.warning("AGAIN, THE CREATOR OF THIS APP TAKES NO RESPONSABILITY IN SENSITIVE DATA SHARED BEING USED BY STREAMLIT")



if __name__ == "__main__":
    main()

# to run locally do  streamlit run analyzer.py