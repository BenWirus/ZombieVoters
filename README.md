# Zombie Voter Hunter

A set of scripts that downloads death indexes from ancestry.com (payed subscription). 

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

This should work with any county in the country, but I've only tested it thus far with Wayne count MI.

# Setup

```bash
pip3 install -r requirements.txt
cp config.example.json config.json 
```

Edit `config.json` to include your ancestry.com credentials. 

Download chromedriver [for your Chrome version & OS](https://chromedriver.chromium.org/downloads).

Extract the zip and place the binary in the root of the project directory.

# Usage

## Download deaths example

The example below will download death data from the social security death index on ancestry.com.

* -y = the year the social security card was issued
* -p = the page of results to start at, (useful to resume where you left off)
* -c = the county in the sate you are looking into
* -s = the state you are looking into

```bash
./grab_deaths.py -y 1970 -p 1 -c wayne -s michigan
```

## Find zombies

The example below will poll voter registration websites and look up dead people to see if they are registered to vote.

The results will be stored in `output/checked/` there will be three folders. `dead`, `zombies`, and `voted`.

The `zombies` folder contains info on dead people who are registered to vote.

The `voted` folder contains info on dead people who likely submitted a ballot.

The `dead` folder contains everyone else. (Keep these as a way to prevent duplicating your checks).

```
./zombie_votes.py --mi
```

In this example we are specifying that we are looking up michigan voters with the `--mi` option.

# Helping & Improvements

If you'd like to help this project would benefit from more regional voter lookups.

It would also benefit from a way to look up deaths that does not require a payed ancestry.com account.

The code is kind of a mess, I wrote this in a few hours to get results ASAP. It could use some polish.
