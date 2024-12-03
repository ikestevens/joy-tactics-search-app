import streamlit as st
from elasticsearch import Elasticsearch
from datetime import datetime
import re
from collections import defaultdict
import os


# Set Streamlit to use wide layout
st.set_page_config(layout="wide", page_title="Joy Tactics Search")

def search_transcripts(query, size=50):
    ES_HOSTNAME = os.environ['ES_HOSTNAME']
    es = Elasticsearch([{'host': ES_HOSTNAME, 'port': 9200, 'scheme': 'http'}])
    # es = Elasticsearch([{'host': 'host.docker.internal', 'port': 9200, 'scheme': 'http'}])
    print("trying to connect")
    res = es.search(
        index="transcripts",
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["text", "formatted_title", "raw_title"]
                }
            },
            "highlight": {
                "fields": {
                    "text": {
                        "pre_tags": ["<mark style='background-color: yellow;'>"],
                        "post_tags": ["</mark>"]
                    }
                }
            },
            "size": size
        }
    )
    return res['hits']['hits']

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        return date_obj.strftime('%B %d, %Y')
    except ValueError:
        return date_str

def convert_timestamp_to_display_time(timestamp):
    parts = timestamp.split(":")
    hours, minutes = 0, 0
    if len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(float(parts[2]))
    elif len(parts) == 2:
        minutes = int(parts[0])
        seconds = int(float(parts[1]))
    else:
        seconds = int(float(parts[0]))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return f"{total_seconds // 60}m{total_seconds % 60}s"

def clean_raw_title(title):
    return re.sub(r'\s+(VIDEO|Video|video|VISUAL|Visual|visual)$', '', title, flags=re.IGNORECASE)

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# Layout with three columns
col1, col2, col3 = st.columns([1, 4, 2])

with col2:
    st.title('Joy Tactics Episode Search App')
    search_container = st.container()
    with search_container:
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            query = st.text_input("Search through linguistic genius:", "")
        with search_col2:
            st.write("")  # To balance the search bar to be 50% of the screen width

    if query:
        results = search_transcripts(query, size=50)  # Increase size here as needed
        
        if results:
            grouped_results = defaultdict(list)
            for result in results:
                date_posted = result['_source'].get('date_posted', 'N/A')
                grouped_results[date_posted].append(result)
            
            for date_posted, hits in grouped_results.items():
                formatted_date = format_date(date_posted)
                first_hit = hits[0]
                raw_title = clean_raw_title(first_hit['_source'].get('raw_title', 'N/A'))

                # Create the HTML content for the grouped results
                html_content = f"<div style='border:1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>"
                html_content += f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>"
                html_content += f"<h3 style='margin: 0;'>{raw_title}</h3><h3 style='margin: 0;'>{formatted_date}</h3>"
                html_content += f"</div><hr style='margin: 5px 0;'>"

                for result in hits:
                    text = result['_source']['text']
                    timestamp = result['_source']['timestamp'].split(" - ")[0]  # Grab the start of the timestamp
                    previous_timestamp = result['_source'].get('previous_timestamp', '').split(" - ")[0]  # Grab the start of the previous timestamp
                    youtube_url = result['_source']['youtube_url']

                    # Highlighting
                    if 'highlight' in result:
                        hit_text = ' '.join(result['highlight']['text'])
                    else:
                        hit_text = text

                    start_timestamp = previous_timestamp if previous_timestamp else timestamp
                    display_timestamp = convert_timestamp_to_display_time(start_timestamp)
                    
                    if 'patreon.com' in youtube_url:
                        final_youtube_url = youtube_url
                        patreon_note = " (Patreon link)"
                    else:
                        final_youtube_url = youtube_url + "&t=" + display_timestamp
                        patreon_note = ""

                    # Get text context
                    previous_text = result['_source'].get('previous_text', '')
                    next_text = result['_source'].get('next_text', '')

                    html_content += f"<p><a href='{final_youtube_url}'><strong>{display_timestamp}</strong></a>{patreon_note}</p>"
                    html_content += f"<p>{previous_text}<br>{hit_text}<br>{next_text}</p>"
                    html_content += "<hr style='margin: 5px 0;'>"

                html_content += "</div>"

                # Render the HTML content
                st.markdown(html_content, unsafe_allow_html=True)
        else:
            st.write("No results found")



with col3:
    st.image('logo.png', width=200, use_container_width=True)  # Adjust the width here
