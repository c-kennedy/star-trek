About This Repository
================

This repository contains various work I've done using the Star Trek Scripts corpus, which was scraped from [chakoteya](http://www.chakoteya.net/StarTrek/index.html) and compiled into JSON files by Gary Broughton on Kaggle:

[Star Trek Scripts](https://www.kaggle.com/gjbroughton/start-trek-scripts)

The code in this repository is sufficient to recover a pandas DataFrame of all the lines from each Star Trek show (not including *Discovery*), as far as I can tell. It takes as input the ```all_scripts_raw.json``` file rather than ```all_series_lines.json``` to get scene descriptions, stage directions, and iron out a couple of other little issues. The result is ```table_of_lines.csv```.

Note: the *code* in this repository has the GPL, but the episode list and especially the table of lines themselves are still under Copyright by the various rights owners--usage in this repo is purely educational.

Contents
-----

Right now, what's in here is:

* **episode_list.csv**, which gives the title, stardate, and airdate by series and episode number; to import this into pandas, I suggest using 
```index_col=['series','episode']``` 
so that you can access the data for an episode with a single tuple of information, e.g.
```episode_list.loc[('TNG',72)]```
for the best cliffhanger in the history of television.
* **table_of_lines.csv**, containing every line of dialogue from the first six series (TOS, TAS, TNG, DS9, VOY, ENT). I suggest importing it either without an index or with ```index_col=['series','ep_number','scene_number','line_number']```.
* **parser.py**, which contains the functions I used to compile the episode list and the full table of lines from ```all_scripts_raw.json```. If you pass that JSON array to ```make_big_line_table()```, the output is the DataFrame of lines. Note that ```build_episode_table()``` will not quite give you the right thing to make the table of episodes, since several titles get extracted wrong or inconsistently from the scripts, and I fixed them by hand.
* **trek_analysis1.ipnyb**, a (currently very) brief intro to the data set.
* **trek_analysis2.ipynb**, a more in-depth look at which characters appear in which locations most frequently in each series.

Usage
-----

My main goals with this dataset were to get some more experience cleaning and manipulating data with pandas and to play around with NLP tools a little bit. This data is especially good for NLP because all the lines are intact; the original ```all_series_lines.json``` file has an issue where words got stuck together across line breaks, which makes doing NLP pretty tough.

Errors
----

If you find that lines are missing or that anything wonky has happened (e.g., several lines of dialogue got stuck in a scene name), please let me know--I've ironed out a lot of those problems but probably not all of them!
