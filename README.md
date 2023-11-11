![usage](https://github.com/rly0nheart/tor2tor/assets/74001397/b62b5775-ddca-448a-a556-c5b8cd05a6e0)
![banner](https://github.com/rly0nheart/tor2tor/assets/74001397/3ce19824-9414-4828-a770-081b0b0ae857)

**Tor2Tor** scrapes a given onion link and captures screenshots of all links available on it.

![Python](https://img.shields.io/badge/Python-14354C?style=flat&logo=python)
![Powershell](https://img.shields.io/badge/PowerShell-000000?style=flat&logo=powershell)
![Shell](https://img.shields.io/badge/Shell-121011?style=flat&logo=gnu-bash)
![Dockerfile](https://img.shields.io/badge/Dockerfile-grey.svg?style=flat&logo=docker)
[![Docker](https://github.com/rly0nheart/tor2tor/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/rly0nheart/tor2tor/actions/workflows/docker-publish.yml)
[![CodeQL](https://github.com/rly0nheart/tor2tor/actions/workflows/codeql.yml/badge.svg)](https://github.com/rly0nheart/tor2tor/actions/workflows/codeql.yml)
***
# Installation ⬇️
## Note ⚠️
> This assumes the Firefox browser is installed on the user's machine.

**1.** Clone the repository
  ```commandline
  git clone https://github.com/rly0nheart/tor2tor
  ```

  **2.** Move to the tor2tor directory
  ```commandline
  cd tor2tor
  ```

<details>
  <summary>🐧 Linux</summary>
  
  Run the installation script
  > Assuming it has already been made executable with `sudo chmod +x install.sh`

  ```commandline
  sudo ./install.sh
  ```
  The installation script will install `tor` then download and setup the latest version of `geckodriver`, and install `tor2tor` together with its dependencies (because we're all too lazy to manually do it)
  ***
</details>

<details>
  <summary>🪟 Windows</summary>
  
  Run the powershell installation script
  ```powershell
  .\install.ps1
  ```
  The installation script will download the `tor` bundle, `geckodriver`, and install `tor2tor` together with its dependencies. The downloads will be stored in the `tor2tor` directory.
</details>

<details>
  <summary>🐋 Docker Image</summary>

  ## Note ⚠️
  > This assumes you have docker installed and running

   You can just pull the docker image from [DockerHub](https://hub.docker.com/r/rly0nheart/tor2tor) by running:
  ```commandline
  docker pull rly0nheart/tor2tor
  ```
***
</details>


# Usage ⌨️
<details>
  <summary>🐧 Linux</summary>
  
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

***

</details>

<details>
  <summary>🪟 Windows</summary>
  
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
tor2tor http://example.onion
```

***

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

***
</details>


# Updating ⬆️
<details>
  <summary>🐧 Linux</summary>

   [*update.sh*](https://github.com/rly0nheart/tor2tor/blob/latest/update.sh)
   > Assuming it has already been made executable with `sudo chmod +x update.sh`

   Navigate to the `tor2tor` directory that you cloned and find the `update.sh` file.

  and run it
  ```commandline
  sudo ./update.sh
  ```
  The script will pull the latest changes (if any are available) then rebuild and install the package.

***

</details>

<details>
  <summary>🪟 Windows</summary>

   Navigate to the `tor2tor` directory that you cloned and find the `update.ps1` file.

  ```powershell
  .\update.ps1
  ```
  The script will pull the latest changes (if any are available) then rebuild and install the package.

***

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

***
</details>


# Uninstalling ❌
<details>
  <summary>🐧 Linux</summary>

  ## Note ⚠️
  > Assuming it has already been made executable with `sudo chmod +x uninstall.sh`

  Navigate to the `tor2tor` directory that you cloned and find the `uninstall.sh` file.
  
  Run it!
  ```commandline
  sudo ./uninstall.sh
  ```
  This will uninstall `tor`, delete the `geckodriver` binary and uninstall `tor2tor`
  ***
</details>

<details>
  <summary>🪟 Windows</summary>

  Navigate to the `tor2tor` directory that you cloned and find the `uninstall.ps1` file.
  
  Run it!
  ```powershell
  .\uninstall.sh
  ```
  This will delete the `geckodriver` and tor binaries then uninstall `tor2tor`
  ***
</details>

<details>
  <summary>🐋 Docker Container</summary>

  You can stop (if it's running) and remove the container by running:
  ```commandline
  docker rm -f rly0nheart/tor2tor
  ```
***
</details>

# Important 🚧
As you probably already know,Tor routes data via three relays (servers) for your privacy.
As a result, connections become slower than an ordinary connection.

## Point ⚠️
Once you start **Tor2Tor**, give it at least 2 minutes tops to query the specified onion url and extract links from it.

If you want to work around this, you can always just use a cloud shell service.

# Screenshots
![tor2tor-archive](https://github.com/rly0nheart/tor2tor-archive/assets/74001397/759082c5-f5ea-4b25-80da-a756d182ae86)

There's a dedicated repository of onion screenshots captured with **Tor2Tor** at [Tor2Tor Archive](https://github.com/rly0nheart/tor2tor-archive)
## CI/CD Workflow 🌊

### Docker Image Building 🐳

- Pushing to or merging into the `latest` branch triggers an automatic build of the Docker image.
- This image is tagged as `latest` on Docker Hub, indicating it's the most stable release.

***
![me](https://github.com/rly0nheart/tor2tor/assets/74001397/97bf7845-db43-4fd0-87bd-04e8b6b02e74)



