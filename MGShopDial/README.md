# MG-ShopDial Data Card

*Based on the [template](https://github.com/PAIR-code/datacardsplaybook/blob/main/templates/DataCardsExtendedTemplate.md) by M. Pushkarna, A. Zaldivar, D. Nanas, et al. Data Cards Playbook. Published March 5, 2021.*

The MG-ShopDial dataset that contains English conversations mixing different goals in the domain of e-commerce.
The conversations are collected following our coached human-human data collection protocol where each dialogue participant is given a set of instructions, instead of a specific script or answers to choose from. The protocol is described in the associated paper.
MG-ShopDial enables the development of future multi-goal conversational agents as well as user simulators facilitating the evaluation of such agents.

#### Dataset Link
<!-- width: half -->

[Link to GitHub](https://github.com/iai-group/MG-ShopDial)

#### Data Card Authors
<!-- width: half -->

  * **Nolwenn Bernard, IAI group** 
  * **Krisztian Balog, IAI group**

## Authorship

### Dataset Owners

#### Team
<!-- scope: telescope -->

[IAI group](http://iai.group/)

#### Contact Details
<!-- scope: periscope -->

  * **Dataset Owners:** Nolwenn Bernard and Krisztian Balog
  * **Affiliation:** University of Stavanger
  * **Contact:** nolwenn.m.bernard@uis.no

#### Authors
<!-- scope: microscope -->

  * Nolwenn Bernard, University of Stavanger, 2023
  * Krisztian Balog, University of Stavanger, 2023

### Funding Sources

  * [Norwegian Research Center for AI Innovation](https://www.ntnu.edu/norwai), NorwAI (Research Council of Norway, project number 309834)

## Dataset Overview

#### Data Subjects
<!-- scope: telescope -->

  * Multi-goal conversational data
  * Conversations about products in the e-commerce domain

#### Dataset Snapshot
<!-- scope: periscope -->

Category | Data
--- | ---
Size of Dataset | 1MB
Number of conversations | 64
Number of utterances | 2196
Number of conversational goals | 3
Number of intents | 12
Number of product categories | 4

**Above:** Summary of the MG-ShopDial dataset.

#### Content Description
<!-- scope: microscope -->

The dataset contains conversations mixing conversational goals (search, recommendation, and QA) in the domain of e-commerce. Each conversation has metadata and its utterances are annotated with both intents and conversational goal.

#### Detailed summary 
<!-- width: full -->

Product category | # conversations | # utterances  
--- | :---: | :---: 
Books | 14 | 482
Sports and Outdoors | 17 | 697
Cell Phones and Accessories | 19 | 559 
Office Products | 14 | 458 
Total | 64 | 2196

**Above:** Summary per product category of the MG-ShopDial dataset.

### Sensitivity of Data

#### Sensitivity Type
<!-- scope: telescope -->

  * Anonymous Data

#### Fields with Sensitive Data
<!-- scope: periscope -->

**Intentional Collected Sensitive Data**

No sensitive data was intentionally collected.

**Unintentionally Collected Sensitive Data**

Personal information such as name were not explicitly collected as a part of the dataset creation process and any utterances we found may contain such information have been anonymized.

### Dataset Version and Maintenance

#### Maintenance Status
<!-- scope: telescope -->

**Limited Maintenance** - The data will not be updated, but any technical issues will be addressed.

#### Version Details
<!-- scope: periscope -->

**Current Version:** 1.0

**Last Updated:** 02/2023

**Release Date:** 02/2023

#### Maintenance Plan
<!-- scope: microscope -->

MG-ShopDial is a static dataset from a specific point in time and maintenance will be limited.

**Feedback:** For feedback reach out to nolwenn.m.bernard@uis.no. 

## Example of Data Points

#### Primary Data Modality
<!-- scope: telescope -->

  * Text Data

#### Data Fields
<!-- scope: microscope -->

Field Name | Field Value | Description
--- | --- | ---
id | String | Conversation id
metadata | Object | Conversation metadata
metadata.type | String | Scenario complexity 
metadata.id | String | Scenario id
metadata.constraint | String | Level of constraint of the scenario
metadata.desc | String | Scenario
metadata.client_checklist | List | List of actions completed by the client
metadata.assistant_checklist | List | List of actions completed by the shopping assistant
metadata.search_logs | List | List of query objects
utterances | List | List of utterance objects

**Above:** Description of data fields

**Additional Notes:** An utterance object as the following fields: `utterance_id`, `participant`, `utterance`, `goal`, and `intents`. The field `intents` contains a list of tuple with an intent and the number of annotator agreeing out of 5, e.g., [["greetings", 4]] means that 4 annotators out of 5 selected this intent.

#### Typical Data Point
<!-- width: half -->

Below is a typical data point.

```
{"id": "Books:45:109:118",
  "metadata": {
    "type": "simple",
    "id": "45",
    "constraint": "low",
    "desc": "You are looking for a book in one of the following genre: romance, sociology, classical literature, or thriller.",
    "client_checklist": [
      "greetings",
      "need"
    ],
    "assistant_checklist": [],
    "search_logs": []
  },
  "utterances": [
    {
      "utterance_id": 1,
      "participant": "Assistant",
      "utterance": "Hello, how I can help?",
      "goal": "recommendation",
      "intents": [
          [
              "greeting",
              4.0
          ],
          ...
      ]
    },
    ...
  ]
}
```

#### Atypical Data Point
<!-- width: half -->

The dataset does not contain atypical data points as far as we know.

## Motivations & Intentions

### Motivations

#### Purpose
<!-- scope: telescope -->

  * Research

#### Domains of Application
<!-- scope: periscope -->

`Conversational Information Access`, `Product search`

#### Motivating Factor(s)
<!-- scope: microscope -->

  * Dataset with conversations mixing conversational goals
  * Development of multi-goal conversational agents
  * Development of user simulator to facilitate the evaluation of multi-goal conversational agents

### Intended Use

#### Dataset Use
<!-- scope: telescope -->

  * Safe for research use


#### Intended and/or Suitable Use Cases
<!-- scope: periscope -->

  * Study of multi-goal conversations
  * Training of multi-goal conversational agents
  * User simulation


#### Unsuitable Use Case
<!-- scope: microscope -->

  * The dataset is not intended to be used in a way that would cause or likely to cause overall harm.

#### Research and Problem Space(s)
<!-- scope: periscope -->

This dataset intends to support research in Conversational Information Access, more particularly, the development of multi-goal conversational agents and user simulators to facilitate the evaluation of these agents.

#### Citation Guidelines
<!-- scope: microscope -->

**BiBTeX:**
```
@inproceedings{Bernard:2022:SIGIR,
  author =    {Bernard, Nolwenn and Balog, Krisztian},
  title =     {MG-ShopDial: A Multi-Goal Conversational Dataset for e-Commerce},
  booktitle = {Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval},
  series =    {SIGIR '23},
  year =      {2023}
}
```

## Access

#### Access Type
<!-- scope: telescope -->

  * External - Open Access

## Provenance

### Collection

#### Method Used
<!-- scope: telescope -->

  * Data collection session with volunteers

#### Methodology Detail
<!-- scope: periscope -->

**Source:** The conversations were collected during dedicated sessions. 

**Platform:** [Coached Conversation Collector (CCC)](https://github.com/iai-group/MG-ShopDial/tree/main/CCC), platform to collect conversations with coached participants

**Is this source considered sensitive or high-risk?** [Yes/**No**]

**Dates of Collection:** [Sep 2022 - Dec 2022]

**Primary modality of collection data:**

  * Text Data

**Update Frequency for collected data:**

  * Static

#### Collection Cadence
<!-- scope: telescope -->

**Others:** Data was collected during multiple sessions with volunteers.

### Collection Criteria

#### Data Inclusion
<!-- scope: periscope -->

Conversations that are not excluded are in the final dataset.

#### Data Exclusion
<!-- scope: microscope -->

Conversations that do not contain multiple conversational goals.

## Transformations

### Synopsis

#### Transformation Applied
<!-- scope: telescope -->

  * Anonymization

#### Method Used
<!-- scope: microscope -->

**Anonymization**: The participant's name disclosed in an utterance is replaced by [NAME].


## Annotations 

Annotation details are available [here](https://github.com/iai-group/MG-ShopDial/blob/main/MGShopDial/Annotation_task.md).
