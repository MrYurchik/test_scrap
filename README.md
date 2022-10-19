# 1XBET Scraping 
> Python scraper using async requests to the 1xbet.com Redis site as a database

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Contact](#contact)


## General Information
- This project solves the problem of scraping the [ua1xbet](https://ua1xbet.com/live/football) website.
- The purpose of the project is to show the ability to use scrapy and work with radis database.

## Technologies Used
- Scrapy - version 2.7.0
- redis - version 4.3.4
- Flask - version 2.2.2
- pydantic - version 1.10.2
- pre-commit - version 2.20.0


## Features
List the ready features here:
- Scrapyng all live start page football matches
- Adding result to Redis DataBase
- Display result at local server


## Setup
Python version 3.9 or higher. All project requirements stored in the root directory. 
Setup Redis, and specify the host and port in two files redis_pipline.py(line 7), app.py(line 8)

## Usage
After successful setup project run app.py to run local server.
Use this command to run Scrapy crawler in xbet directory:
`scrapy crawl ua1xbet`


## Project Status
Project is:  _in progress_

## Room for Improvement

To do:
- Add unittest
- Make Docker container with Redis database 
- Add typing


## Contact
Created by [Yurii Shykoriak](https://t.me/abubariba) - feel free to contact me!
