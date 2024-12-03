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

4. Deploy Elaticsearch pod with `kubectl apply -f elasticsearch-deployment.yaml` This will create a single pod on a node on your cluster. With `kubectl get pods` you will be able to see the container creating. 

## Deploying Elasticsearch container

5. Once the contianer has been created it is time to expose the elasticserach container to the cluster with a service. This service will expose the pod to the cluster. To do this run `kubectl apply -f elasticsearch-service.yaml`. Once you have completed this step run `kubectl get services` and you should see a new service named elasticsearch. Your elasticsearch pod is now availible across the cluster!

## Deploying Application

6. Now we can deploy our application. To do this you must build the Dockerfile in this repo and push it to your dockerhub repository. To do this do the following. (We are under the assumption have the docker CLI and that you are logged into your docker account). 
    - build the `Dockerfile` locally and tag it with the following command: `docker build -t <your_docker_username>/joy-tactics-app . --no-cache=true --platform=linux/amd64` Note: `--platform=linux/amd64` ensures that if you are running this on Apple Silicon the container will work on non-Apple silocone CPU's.

7. Once the image has been built, push the image to your dockerhub repository `docker push <your_docker_username>/joy-tactics-app` . Now the image is availible in your dockerhub repository!

8. Now it is time to deploy our container to our pods using a deployment for our newly pushed image. Open up the `joy_deployment.yaml` file and replace `YOUR_DOCKER_USERNAME` with your docker username and `ES_HOSTNAME_VALUE` with the ClUSTER-IP of our elasticsearch service (make sure you pass as a string ex. "CLUSTER_IP_VALUE").  Run `kubectl get services` to get this IP address. We are doing this to pass in environment variabled to our containers so they can access our db container in our cluster. This container is not exposed to the internet and can only be accessed within the cluster. Save the file once this has been completed. 

9. Deploy using `kubectl apply -f joy_deployment.yaml`. Check that containers have been created using `kubectl get pods` and you should see 3 pods created! Note that the number of pods created is equal to the number of `replicas` in the deployment file. In our case that value is 3.

10. Now that we have our application running in our cluster it is time to expose it to the internet with a loadbalancer! To do this run `kubectl apply -f joy_service.yaml` . This will automatically create a loadbalance on digital ocean that will expose our application to the internet on `port 8501`. Monitor the creation of the IP address using `kubectl get services` and look at the `joy-service` row and the value at the `EXTERNAL-IP` column. It will say pending for a some time. This is beacuse the managed DigitalOcean Kubernetes cluster is automaticlly being created assigning an IP address to your cluster. Once the external ip is assigned open a browser and go to `<EXTERNAL_IP_ADDRESS>:8501` and you should see the applicaiton!

11. Now that we have our application open lets type in "hello" into our search bar and press enter. We get an error reading 
```NotFoundError: NotFoundError(404, 'index_not_found_exception', 'no such index [transcripts]', transcripts, index_or_alias)``` 
This is because our elasticsearch database has no data. Time to seed the database. 

12. Instead of having to run the seeding process on your local machine we will run a container that will seed the db for us. First open `Dockerfile-seedDB` and replace `ES_HOSTNAME` with the CLUSTER-IP of the elasticsearch service we created earlier. 

13. Build the image with `docker build -t <YOUR_DOCKER_USERNAME>/seed-es -f Dockerfile-seedDB . --no-cache=true --platform=linux/amd64`

14. Push the image with `docker push <YOUR_DOCKER_USERNAME>/seed-es`

15. We can now run this container by itself without a deployment file using `kubectl run seed-es --image=<YOUR_DOCKER_USERNAME>/seed-es` Once the pod is running we can view the logs using `kubectl logs seed-es`. The expected output should be `Loaded 79 episodes from CSV`. We can delete the pod using `kubectl delete pod seed-es`

16. We can go back to our browser and search! Type in the word `hello` and you will see all the times the word `hello` has been mentioned in the podcast with links to the Youtube episode time! 





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