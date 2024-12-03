import os
import csv
import re
from elasticsearch import Elasticsearch
from datetime import datetime
from tqdm import tqdm
import sys

def create_index(es):
    es.indices.create(
        index='transcripts',
        body={
            "mappings": {
                "properties": {
                    "formatted_title": {"type": "keyword"},
                    "text": {"type": "text"},
                    "previous_text": {"type": "text"},
                    "next_text": {"type": "text"},
                    "timestamp": {"type": "text"},
                    "previous_timestamp": {"type": "text"},
                    "youtube_url": {"type": "text"},
                    "date_posted": {"type": "date"},
                    "raw_title": {"type": "text"}
                }
            }
        },
        ignore=400
    )

def clean_title(title):
    title = re.sub(r'\[.*?\]', '', title)
    title = re.split(r'\|', title)[0]
    title = title.replace(' ', '_').replace('-', '_')
    title = re.sub(r'[^a-zA-Z0-9_]', '', title)
    title = title.rstrip('_')
    return title.lower()

def extract_date_from_filename(filename):
    match = re.match(r'(\d{8})_(.+)', filename)
    if match:
        date, title = match.groups()
        return date, title
    return None, None

def load_episode_data(csv_file):
    episode_data = {}
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['youtube_url']:
                episode_title = clean_title(row['formatted_title'])
                episode_data[episode_title] = {
                    'youtube_url': row['youtube_url'],
                    'date_posted': row['date_posted'],
                    'raw_title': row['raw_title'],
                    'formatted_title': row['formatted_title']
                }
    print(f"Loaded {len(episode_data)} episodes from CSV")
    return episode_data

def any_record_exists(es, index, formatted_title):
    query = {
        "query": {
            "term": {
                "formatted_title": formatted_title
            }
        }
    }
    try:
        response = es.search(index=index, body=query)
        return response['hits']['total']['value'] > 0
    except Exception as e:
        print(f"Error checking record existence: {e}")
        return False

def index_transcripts(es, transcripts_dir, episode_data):
    if not os.path.exists(transcripts_dir):
        print(f"Transcripts directory {transcripts_dir} does not exist")
        return 0

    filenames = [f for f in os.listdir(transcripts_dir) if f.endswith(".txt")]
    ingested_files = 0

    for filename in tqdm(filenames, desc="Indexing transcripts"):
        date, episode = extract_date_from_filename(filename.replace('.txt', ''))
        if episode in episode_data:
            formatted_title = episode_data[episode]['formatted_title']

            if any_record_exists(es, 'transcripts', formatted_title):
                continue
            
            with open(os.path.join(transcripts_dir, filename), 'r') as f:
                lines = f.readlines()
                youtube_url = episode_data[episode]['youtube_url']
                date_posted = datetime.strptime(episode_data[episode]['date_posted'], '%Y-%m-%d %H:%M:%S')
                for i, line in enumerate(lines):
                    if "::" in line:
                        try:
                            timestamp, text = line.split("::", 1)
                            timestamp = timestamp.strip()
                            previous_timestamp = lines[i - 1].split("::", 1)[0].strip() if i > 0 and "::" in lines[i - 1] else ""
                            previous_text = lines[i - 1].split("::", 1)[1].strip() if i > 0 and "::" in lines[i - 1] else ""
                            next_text = lines[i + 1].split("::", 1)[1].strip() if i < len(lines) - 1 and "::" in lines[i + 1] else ""
                            doc = {
                                "formatted_title": formatted_title,
                                "text": text.strip(),
                                "previous_text": previous_text,
                                "next_text": next_text,
                                "timestamp": timestamp,
                                "previous_timestamp": previous_timestamp,
                                "youtube_url": youtube_url,
                                "date_posted": date_posted,
                                "raw_title": episode_data[episode]['raw_title']
                            }
                            es.index(index='transcripts', body=doc)
                        except Exception as e:
                            print(f"Error processing line '{line.strip()}': {e}")
            ingested_files += 1
        else:
            print(f"No matching episode data found for {episode}")
    return ingested_files

if __name__ == "__main__":
    try:
        host_name = sys.argv[1]
        print("Hostname:", host_name)
    except Exception as e:
        print("please provide hostname from cluster")
        print(e)
    es = Elasticsearch([{'host': host_name, 'port': 9200, 'scheme': 'http'}]).options(
        request_timeout=30,
        max_retries=10,
        retry_on_timeout=True
    )
    # es = Elasticsearch([{'host': 'host.docker.internal', 'port': 9200, 'scheme': 'http'}]).options(
    #     request_timeout=30,
    #     max_retries=10,
    #     retry_on_timeout=True
    # )
    try:
        create_index(es)
        print("Index created or already exists.")
        episode_data = load_episode_data('data/episodes.csv')
        ingested_files = index_transcripts(es, 'data/transcripts/full', episode_data)
        print(f"Ingested {ingested_files} transcript files from data/transcripts/full")
    except Exception as e:
        print(f"An error occurred: {e}")
