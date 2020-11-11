# Zombie Voter Hunter

A set of scripts that downloads death indexes from myheritage.com. 

Then uses that data to determine if dead people are registered to vote.

# Why

The purpose of this project is not to prove that there is voter fraud to help any political candidate or party.

The purpose of this is to test the claims that there is or is not dead people voting.

The goal is to provide tangible proof that this either is or is not happening and put an end to hyperbolic claims from all sides.

If dead folks are voting, that presents a clear danger to our republic.
If it is not happening and baseless accusations are made, confidence in our democratic institutions will fade, presenting another danger to our republic.

So in short the goal is to put baseless claims that it is or is not happening aside, and get to the facts. Hopefully all Americans would like to put this debate to rest.

## Voter lookup support

### Implemented 

* Michigan

### Investigating

* Georgia
* North Carolina
* Nevada
* Pennsylvania

### Not Possible

* Arizona - [Drivers License or Voter ID # required to look up at](https://my.arizona.vote/WhereToVote.aspx?s=individual&Language=en)

need to add more

## Death data download support

This should work with any county in the country, but I've only tested it thus far with Wayne County MI.

# Setup

Install Python libraries and create your local config file.

```bash
pip3 install -r requirements.txt
cp config.example.json config.json 
```

Obtain a `bearer_token` and `guest_id` from myheritage:

* Open your browser and visit [https://www.myheritage.com/research](https://www.myheritage.com/research).
* Open your browsers developer tools and switch to the `network` tab.
* Enter any value in the search fields and then click `Search`.
* Look for the XHR request `/search_in_historical_records/` and click on it & stay in the `Headers` tab in the right pane.
* Scroll down in the headers tab and look for the POST data section, you'll see `Form Data`.
* Copy the values of `bearer_token` & `guest_id`. Then paste their values in their respective spots in the `config.json` file.

Make any adjustments you'd like to `config.json`.

# Update

```bash
git pull;
pip3 install -r requirements.txt
```

Check `config.example.json` for any changes by comparing it with your local `config.json`.

# Usage

## Download deaths example

The example below will download death data from the social security death index from myheritage.com.

* --sy = the year to start at
* --ey = the year to end at
* -s = the state you are looking into two letter abbreviation
* -c = the county in the sate you are looking into

```bash
./death_scraper.py --sy 1900 --ey 2000 -s mi -c wayne
```

## Find zombies

The script will automatically check the dead person's information against supported voter registration websites.

The output will be stored in `output/checked/`. From there there are two sub-folders, `dead` and `zombies`.
If the person did not vote or is not registered the info will be stored in the `dead` folder.
If they sent a ballot in the info will be stored in `zombies/balloted` if they are just registered it their info will be in `zombies/registered`.

# Helping & Improvements

If you'd like to help this project would benefit from more regional voter lookups.

The code is kind of a mess, I wrote this in a few hours to get results ASAP. It could use some polish.

# Mirrors

* https://github.com/BenWirus/ZombieVoters <-- primary
* https://gitlab.com/BenWirus/ZombieVoters
* https://bitbucket.org/BenWirus/zombievoters
* https://git.sr.ht/~benwirus/ZombieVoters
