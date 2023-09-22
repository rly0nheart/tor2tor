Capture onion services on an onion service.
![Screenshot from 2023-09-22 19-20-14](https://github.com/rly0nheart/tor2tor/assets/74001397/86e3330b-6df2-4fef-8d0c-daa5d6ebd2cf)
![Screenshot from 2023-09-22 19-49-51](https://github.com/rly0nheart/tor2tor/assets/74001397/a3eb1318-0e23-48bb-9610-e2af2c7b1309)


With **tor2tor**, you can scrape a given onion link and capture screenshots of all links available on it.

# Wiki
Refer to the [Wiki](https://github.com/rly0nheart/tor2tor) for installation instructions, in addition to all other documentation.
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


