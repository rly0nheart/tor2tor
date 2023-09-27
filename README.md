```
┌┬┐┌─┐┬─┐┌─┐┌┬┐┌─┐┬─┐
 │ │ │├┬┘┌─┘ │ │ │├┬┘
 ┴ └─┘┴└─└─┘ ┴ └─┘┴└─
```

**Tor2Tor** scrapes a given onion link and captures screenshots of all links available on it.

[![Docker](https://github.com/rly0nheart/tor2tor/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/rly0nheart/tor2tor/actions/workflows/docker-publish.yml)
[![CodeQL](https://github.com/rly0nheart/tor2tor/actions/workflows/codeql.yml/badge.svg)](https://github.com/rly0nheart/tor2tor/actions/workflows/codeql.yml)
![-](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)
# Installation ⬇️
## Note ⚠️
> This assumes the Firefox browser is installed on the user's machine.

<details>
  <summary>🏠 Local</summary>
  
  **1.** Clone the repository
  ```commandline
  git clone https://github.com/rly0nheart/tor2tor
  ```

  **2.** Move to the tor2tor directory
  ```commandline
  cd tor2tor
  ```
  **3.** Run the installation script
  > Assuming it has already been made executable with `sudo chmod +x install.sh`

  ```commandline
  sudo ./install.sh
  ```
  The installation script will install `tor` then download and setup the latest version of `geckodriver`, and install `tor2tor` together with its dependencies (because we're all too lazy to manually do it)
  ![-](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)
</details>

<details>
  <summary>🐋 Docker Image</summary>

  ## Note ⚠️
  > This assumes you have docker installed and running

   You can just pull the docker image from [DockerHub](https://hub.docker.com/r/rly0nheart/tor2tor) by running:
  ```commandline
  docker pull rly0nheart/tor2tor
  ```
![-](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)
</details>


# Usage ⌨️
<details>
  <summary>🏠 Local Installation</summary>
  
  To see available options/usage, call *Tor2Tor* with the `-h/--help` flag
  ```commandline
  tor2tor --help
  ```
  or 
  ```commandline
  t2t --help
  ```
Calling it with an onion url should look like the following
```commandline
sudo tor2tor http://example.onion
```

![-](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

</details>

<details>
  <summary>🐋 Docker Container</summary>
  
  The *Tor2Tor* container can be called with `docker run` like so:
  ```commandline
  docker run rly0nheart/tor2tor --help
  ```

  Calling the container with an onion url should look like the following
  ```commandline
  docker run --tty --volume $PWD/tor2tor:/root/tor2tor rly0nheart/tor2tor http://example.onion
  ```
## Note ⚠️
  > --tty Allocates a pseudo-TTY, use it to enable the container to display colours (trust me, you will need this)
  >> --volume $PWD/tor2tor:/root/tor2tor Will mount the *tor2tor* directory from the container to your host machine's *tor2tor* directory.

![-](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)
</details>


# Updating ⬆️
<details>
  <summary>🏠 Local Installation</summary>
  
  *Tor2Tor* comes with an updating script that can be used  to get the latest updates.
  To check for Updates or update, navigate to the cloned *tor2tor* directory and find the `update.sh` file
  > Assuming it has already been made executable with `sudo chmod +x update.sh`

  and run it
  ```commandline
  sudo ./update.sh
  ```
  The script will pull the latest changes (if any are available) then rebuild and install the package.

![-](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)

</details>

<details>
  <summary>🐋 Docker Container</summary>
  
  As for the docker container, just run the docker pull command again.
  ```commandline
  docker run rly0nheart/tor2tor --help
  ```

  Calling the container with an onion url should look like the following
  ```commandline
  docker run --tty --volume $PWD/tor2tor:/root/tor2tor rly0nheart/tor2tor http://example.onion
  ```
## Note ⚠️
  > --tty Allocates a pseudo-TTY, use it to enable the container to display colours (trust me, you will need this)
  >> --volume $PWD/tor2tor:/root/tor2tor Will mount the *tor2tor* directory from the container to your host machine's *tor2tor* directory.

![-](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)
</details>


# Uninstalling ❌
<details>
  <summary>🏠 Local Installation</summary>

  ## Note ⚠️
  > Assuming it has already been made executablem `222 q2111 with `sudo chmod +x uninstall.sh`

  Navigate to the `tor2tor` directory that you cloned and find the `uninstall.sh` file.
  
  Run it!
  ```commandline
  sudo ./uninstall.sh
  ```
  This will uninstall `tor`, delete the `geckodriver` binary and uninstall `tor2tor`
  ![-](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)
</details>

<details>
  <summary>🐋 Docker Container</summary>

  You can stop (if it's running) and remove the container by running:
  ```commandline
  docker rm -f rly0nheart/tor2tor
  ```
![-](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)
</details>

# Important 🚧
As you probably already know,Tor routes data via three relays (servers) for your privacy.
As a result, connections become slower than an ordinary connection.

## Point ⚠️
Once you start **Tor2Tor**, give it at least 2 minutes tops to query the specified onion url and extract links from it.

If you want to work around this, you can always just use a cloud shell service.
## CI/CD Workflow 🌊

### Docker Image Building 🐳

- Pushing to or merging into the `latest` branch triggers an automatic build of the Docker image.
- This image is tagged as `latest` on Docker Hub, indicating it's the most stable release.

![-](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png)
![me](https://github.com/rly0nheart/glyphoji/assets/74001397/e202c4c1-9a69-40c4-a4da-1e95befb08ee)

