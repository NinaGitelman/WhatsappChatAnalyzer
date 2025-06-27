import re
from collections import defaultdict, Counter
from datetime import datetime
import string


def parse_chat_transcript(file_path):
    """
    Parse the chat transcript and return a dictionary with messages organized by month.
    """
    monthly_messages = defaultdict(list)

    # Pattern to match the chat format: month/day/year, time - Name: Message
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s*\d{1,2}:\d{2}\s*-\s*([^:]+):\s*(.+)$'

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                match = re.match(pattern, line)
                if match:
                    date_str, name, message = match.groups()

                    # Parse the date
                    try:
                        date = datetime.strptime(date_str, '%m/%d/%y')
                    except ValueError:
                        try:
                            date = datetime.strptime(date_str, '%m/%d/%Y')
                        except ValueError:
                            continue

                    # Create month key (YYYY-MM format)
                    month_key = date.strftime('%Y-%m')
                    monthly_messages[month_key].append(message)

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {}
    except Exception as e:
        print(f"Error reading file: {e}")
        return {}

    return monthly_messages


def clean_and_tokenize(text):
    """
    Clean the text and return a list of words, excluding common stop words.
    """
    # Common stop words to exclude (expanded list)
    stop_words = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
        'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
        'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
        'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
        'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
        'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
        'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
        'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
        'just', 'don', 'should', 'now', 'to', 'from', 'into', 'would', 'could', 'get', 'got',
        'like', 'go', 'going', 'went', 'know', 'think', 'said', 'say', 'see', 'want', 'come',
        'came', 'way', 'time', 'day', 'make', 'made', 'take', 'took', 'good', 'well', 'back',
        'much', 'many', 'new', 'old', 'one', 'two', 'first', 'last', 'long', 'little', 'own',
        'right', 'big', 'high', 'small', 'large', 'next', 'early', 'young', 'important',
        'few', 'public', 'bad', 'same', 'able', 'media', 'omitted', 'null'
    }

    # Convert to lowercase and remove punctuation
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Split into words and filter out stop words and short words
    words = [word for word in text.split()
             if word not in stop_words and len(word) > 2 and word.isalpha()]

    return words


def analyze_monthly_word_frequency(monthly_messages):
    """
    Analyze word frequency for each month and return top 10 words per month.
    """
    monthly_analysis = {}

    for month, messages in monthly_messages.items():
        # Combine all messages for the month
        all_text = ' '.join(messages)

        # Clean and tokenize
        words = clean_and_tokenize(all_text)

        # Count word frequencies
        word_counts = Counter(words)

        # Get top 10 most common words
        top_words = word_counts.most_common(10)

        monthly_analysis[month] = {
            'total_messages': len(messages),
            'total_words': len(words),
            'top_words': top_words
        }

    return monthly_analysis


def print_analysis(monthly_analysis):
    """
    Print the analysis results in a formatted way.
    """
    print("=" * 80)
    print("CHAT TRANSCRIPT WORD FREQUENCY ANALYSIS")
    print("=" * 80)

    # Sort months chronologically
    sorted_months = sorted(monthly_analysis.keys())

    for month in sorted_months:
        data = monthly_analysis[month]

        # Convert month to readable format
        month_obj = datetime.strptime(month, '%Y-%m')
        readable_month = month_obj.strftime('%B %Y')

        print(f"\n📅 {readable_month}")
        print("-" * 40)
        print(f"Total messages: {data['total_messages']}")
        print(f"Total words analyzed: {data['total_words']}")
        print("\nTop 10 most used words:")

        for i, (word, count) in enumerate(data['top_words'], 1):
            print(f"{i:2d}. {word:<15} ({count} times)")

        print()

FILE_PATH = r"C:\Users\User\Desktop\D25\chatFull.txt"
def main():
    """
    Main function to run the chat analysis.
    """
    # You can change this to your transcript file path
    file_path = FILE_PATH

    if not file_path:
        file_path = "chat_transcript.txt"  # Default filename

    print(f"Analyzing chat transcript: {file_path}")
    print("Processing...")

    # Parse the chat transcript
    monthly_messages = parse_chat_transcript(file_path)

    if not monthly_messages:
        print("No messages found or error reading file.")
        return

    # Analyze word frequency
    analysis = analyze_monthly_word_frequency(monthly_messages)

    # Print results
    print_analysis(analysis)

    # Save results to file
    output_file = "chat_analysis_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("CHAT TRANSCRIPT WORD FREQUENCY ANALYSIS\n")
        f.write("=" * 80 + "\n\n")

        sorted_months = sorted(analysis.keys())
        for month in sorted_months:
            data = analysis[month]
            month_obj = datetime.strptime(month, '%Y-%m')
            readable_month = month_obj.strftime('%B %Y')

            f.write(f"{readable_month}\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total messages: {data['total_messages']}\n")
            f.write(f"Total words analyzed: {data['total_words']}\n")
            f.write("Top 10 most used words:\n")

            for i, (word, count) in enumerate(data['top_words'], 1):
                f.write(f"{i:2d}. {word:<15} ({count} times)\n")

            f.write("\n")

    print(f"\nResults also saved to: {output_file}")


if __name__ == "__main__":
    main()