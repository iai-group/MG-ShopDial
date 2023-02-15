# Data collection setup

## MG-ShopDial

In this experiment, there is a user who is acting as a client and another user playing a retail assistant.
The aim of this experiment is to collect realistic conversations mixing goals in the domain of shopping. 
The metadata of the products originate from Amazon review data (2018) [[1]](#1).
We limit the number of product categories to 4 which are listed below. 

Amazon products categories:
* Sports and Outdoors
* Books
* Office Products
* Cell Phones and Accessories

**Domain**: shopping, can include several categories of products (e.g., books, running shoes).  
**Goals covered**: search, recommendation, and QA.

### Create scenario pool

A pool of scenarios is created in order to collect a balanced number of conversations per category, herein after referred to as topics. A [scenario](../ccc/app/chat/topics.py) represent the objective of the conversation, it is composed of a description, a type, and a level of constraint.
Once a chatroom is completed, one scenario is assigned and removed from the pool.  
The different scenarios are available [here](../ccc/app/chat/static/yml/topics.yml).

### Create lists of pre-selected products

As product search is a complex task, a list of products that can meet the requirements of the scenarios is created for each category. 
Based on the category of the scenario, the associated list of products will be displayed to the shopping assistant.

The product lists for MG-ShopDial are under `data\items`.

### Define instructions

The instructions are defined in HTML files: `user_task_template.html` for the client and `assistant_task_template.html` for the shopping assistant.
These files will be loaded automatically.

The client instructions for MG-ShopDial are available [here](../ccc/app/chat/templates/chat/user_task_template.html) and [here](../ccc/app/chat/templates/chat/assistant_task_template.html) for the shopping assitant. 

## Create your own setup

The MG-ShopDial example can serve as a base to setup your own data collection.
For the data collection, the following is needed:

### Topics

Create scenarios per product category in the topic [file](../ccc/app/chat/static/yml/topics.yml). A scenario is composed of a description, a type, and a level of constraint.

### Lists of pre-selected products

JSON files with list of pre-selected products for each catogery. 

For each category, the following needs to be done:

  * Create a list of product items. A product item is a dictionary with the following entries: `name`, `price`, `short_description`, `images`, `rating`, and `product_description`. 
  * Save the list to a JSON file in `data/items` with the following name convention: `{category}_items.json`.

### Instructions

Define the client instructions in `/ccc/app/chat/templates/chat/user_task_template.html` and `/ccc/app/chat/templates/chat/assistant_task_template.html`.

## References
<a id="1">[1]</a>
Ni, Jianmo, Jiacheng Li, and Julian McAuley. "Justifying recommendations using distantly-labeled reviews and fine-grained aspects." Proceedings of the 2019 conference on empirical methods in natural language processing and the 9th international joint conference on natural language processing (EMNLP-IJCNLP). 2019.
