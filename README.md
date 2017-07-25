# Networks

This repository contains projects from my Networks course at UC Davis. Please see corresponding pdf in each project folder for more details. If project does not seem to work, please change the port on which it is run. 

## Project 1
This project explores the fundamentals of socket programming using UDP protocol. The client will send 10 pings to the server and time the response. If no reponse is received within 1 second, the client will assume the packet is lost. 

### Usage
1. Open 2 terminal windows (NOT tabs)
2. Run `python UDPPingerServer.py` first
3. Run `python UDPPingerClient.py` second

## Project 2 Part 1
This part simulates a simple queuing system with both a finite buffer and infinite buffer to study the packet loss probability.

### Usage
1. Install SimPy if needed: `pip install simpy`
2. Run `python FiniteBufferQueue.py`
3. Run `python InfiniteBufferQueue.py`

## Project 2 Part 2
The second part of this project simulates insertion and transmission of packets on 10 hosts to analyze Exponential Backoff algorithm following Slotted Aloha protocol.

### Usage
1. Install SimPy if needed: `pip install simpy`
2. Run `python BinaryBackoff.py`

![Exponential Backoff](http://i.imgur.com/buz2wbe.jpg)     
![Linear Backoff](http://i.imgur.com/PFlTDQ1.jpg)

## Requirements
Program | Version 
--- | ---
Python | 2

