# Joy Tactics Episode Search

### What Is This Repo 
This repo downloads all episodes from the Joy Tactics pod and transcribes the podcast discourse into text. The text is indexed into an Elastic cluster in a docker container, and via a streamlit app you can search through the episodes and open the youtube link at the time stamps of each search hit.

### Why Is This Repo
Joy Tactics is an emerging podcast hosted by three hilarious alternative comedians (Nate Varrone, Jack Bensinger, and Eric Rahill). Because of the circuitous nature of each episode discussion, finding funny bits from each episode can be hard. So this app helps to find those bits.

**Note:** Because half of Joy Tactics eppys are Bonus episodes for paying Patreons only, this repo only has the free episode transcripts. But you can fill out the episodes.csv with the bonus episodes youtube_urls and download/transcribe the bonus episodes to use the complete transcripts if you're a Patron. Become a Joy Tactician at https://www.patreon.com/joytactics.

## How to deploy App on DigitalOcean Managed Kubernetes Cluster

**prerequisites:** [Kubectl](https://kubernetes.io/docs/tasks/tools/), [Doctl](https://github.com/digitalocean/doctl?tab=readme-ov-file#installing-doctl), a DigitalOcean Managed Kubernetes Cluster, and [Docker](https://docs.docker.com/engine/install/), 

1. Create DigitalOcean Managed Kubernetes Cluster on your [DigitalOcean](https://cloud.digitalocean.com/) account. For this example we used the folloing 
    - datacenter region: `NYC1` or the region closest to you.
    - version: `1.31.1-do.4 - recommeneded` 
    - Node pool name: `<your-choice>`
    - Shared CPU
    - Machine type (Droplet): Basic
    - Node Plan: `2GB total RAM / 1 vCPU / 50GB storage`
    - Nodes: `3`
    - Cluster name: `<your-choice>`
    - Project: `<your-project>`
    Click Create Cluster to create the cluster. Give it a couple minutes to 
   

2. Follow this [guide](https://docs.digitalocean.com/products/kubernetes/how-to/connect-to-cluster/) to connect to your Kubernetes Cluster. Once you have completed this part you should be connected to your DigitalOcean Kubernetes Cluster!!! 
Run `kubectl get nodes` and you should see your three nodes up and running!

3. Download this repo onto your local machine with your preffered method `git`, `gh`, etc. 

4. 




## How To Run the App Locally

**Requirements:** Python, Docker

1. Install python package requirements: <br>
`pip install -r requirements.txt`

2. Make sure docker is running, then spin up the Elastic instance using this command from the top level directory: 
`docker-compose up -d`

3. Ingest all of the transcripts <br>
`python ingest_data.py`

4. Confirm the 'transcripts' index was successfully ingested: <br>
`curl -X GET "localhost:9200/transcripts/_count"`

5. Run the streamlit app: <br>
`streamlit run app.py`

6. The app will now be running on localhost:8501 with the free episodes available to search!


## How To Add Patron Bonus Episodes and Maintain with Episodes to Come

**Requirements:** Python and Docker still

1. Install python package requirements: <br> `pip install -r requirements.txt`

2. The notebook `01_scrape_joy_tactics_data.ipynb` does three things: <br>
    * First cell of that notebook uses the Patreon public API to get all the posts from the Joy Tactics page <br>
        * This produces data/raw_episodes.csv that has the link to each post and date_posted and other metadata
    * Next cell enriches the data from raw_episodes into episodes.csv <br>
        * It tags bonus episodes based on if it was posted on Monday or not
        * It tags video posts bc those ones we'll scrape the youtube_url
        * It formats the transcript name as YYYYMMDD_formatted_title.txt
    * Lastly, the notebook scrapes the youtube_url using selenium
        * This also gets the youtube video for bonus eppys so you need to write your email and patreon password into the code to authenticate into Patreon
        * This cell goes soooo slow. I ended up just clicking on each patreon video post manually and clicking the 'Watch on YouTube' link and copying the url manually bc it was so slow. But it does do it automatically if yours loads the patreon pages faster
        * This cell is just filling out the youtube_url in episodes.csv, so you could do it manually

3. The `02_download_transcripts.ipynb` notebook goes through episodes.csv and downloads the audio from each youtube_url and saves the transcript
    * Bc each eppy is like an hour, this script also chunks each audio file into 5 minute chunks and saves that in data/audio/chunks then it transcribes each 5 min file into data/transcripts/chunks, finally it pieces together the 5 min transcripts and timestamps into a final transcript in data/transcripts/full
    * The first like ~10 episodes don't have a YouTube link, I downloaded those manually and saved them in data/audio/full and this notebook will automatically just skip to the chunking steps


4. Once the transcripts are in data/transcripts/full and episodes.csv is updated then the `ingest_data.py` script will be ingesting those into Elastic so you're all set!!

![Project Logo](logo.png)