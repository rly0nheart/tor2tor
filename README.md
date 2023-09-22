Capture onion services on an onion service.

![Screenshot from 2023-09-22 19-20-14](https://github.com/rly0nheart/tor2tor/assets/74001397/dd65f77e-3106-4dc9-a17a-81a82c0ed4bc)
![Screenshot from 2023-09-22 19-49-51](https://github.com/rly0nheart/tor2tor/assets/74001397/34404739-fc77-45ab-91fe-e86f7f00a39a)

With **tor2tor**, you can scrape a given onion link and capture screenshots of all links available on it.

# Pre-requisites
* Tor bundle (Windows)
* Tor package (GNU/Linux)
* Firefox Browser
* [Geckodriver](https://github.com/mozilla/geckodriver/releases)
```
Firefox, requires geckodriver, which needs to be installed before tor2tor can be run. Make sure it’s in your PATH, e. g., place it in /usr/bin or /usr/local/bin.

Failure to observe this step will give you an error selenium.common.exceptions.WebDriverException: Message: ‘geckodriver’ executable needs to be in PATH.

- Copied from Selenium PyPI :)
  ```
  
# Installation
Before the initial installation, make sure you have the tor package/bundle. On GNU/Linux, it can be installed with `sudo apt install tor -y`. 
On Windows systems you will need to download the Tor Bundle from [here](https://www.torproject.org/download/tor/) and extract it. 

### Note
> Installation of the tor bundle/package won't be required for the docker image. 

## Install from PyPi
```
pip install tor2tor
```

# Pull Docker Image from DockerHub
```
docker pull tor2tor:latest
```

# Usage
## Windows
Once installed, you will need to feed the path of the tor.exe binary to the program.

Navigate to the directory of the Tor bundle that you extracted and find `tor.exe` right-click on it and then click `Copy as Path` in the context menu.

After that's done, call tor2tor with the `-t/--tor` argument and pass the tor.exe path to the argument:
```
tor2tor --tor C:\path\to\tor.exe
```

### Note
> This will write the tor binary path to the program's data.json file.
>> This command is a once off.

To start scraping, just call tor2tor again and pass the target onion url to the `-u/--url` argument:
```
tor2tor --url http://example.onion
```

## GNU/Linux

### Note
> You will not need to call tor2tor with the `-t/--tor` argument on first run.

This assumes you alredy installed the tor package as previously mentioned in `Installation`, you can proceed to call tor2tor with `-u/--url` and pass the desired onion url:
```
tor2tor --url http://example.onion
```
or Docker Image
```
docker run tor2tor $PWD/tor2tor:/app/tor2tor --url http://example.com
```

### Note
> $PWD/tor2tor:/app/tor2tor will mount the program's tor2tor directory to the local system.

Captured screenshots will be saved in directories `C:\\Users\username\tor2tor\example.onion` (on Windows) or `/home/user/tor2tor/example.onion` (on GNU/Linux)

## Help
```
Basic Usage
===========
    tor2tor --url https://example.onion


Other Examples
==============
    Configure the tor.exe binary (for Windows systems)
    --------------------------------------------------
    tor2tor --tor C:\\path\\to\\tor.exe


    Run with headless Firefox
    -------------------------
    tor2tor --headless --url https://example.onion
            
            
    Open each image on capture
    --------------------------
    tor2tor --open --url https://example.onion
```


