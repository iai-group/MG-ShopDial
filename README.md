# MG-ShopDial: A Multi-Goal Conversational Dataset for e-Commerce

This repository provides resources developed within the following article:

> N. Bernard and K. Balog. **MG-ShopDial: A Multi-Goal Conversational Dataset for e-Commerce** In: Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR '23), July 23--27, 2023, Taipei, Taiwan. ACM. New York, NY, USA. July 2023. [DOI: 10.1145/3539618.3591883](https://doi.org/10.1145/3539618.3591883) [[PDF]](https://arxiv.org/pdf/2304.12636.pdf)

## Summary

Conversational systems can be particularly effective in supporting complex information seeking scenarios with evolving information needs.
Finding the right products on an e-commerce platform is an example of such complex scenario, where a conversational agent would need to be able to provide search capabilities over the item catalog, understand the user's preferences and make recommendations based on them, and answer a range of questions related to items and their usage.
Yet, existing conversational datasets do not fully support the idea of mixing different conversational goals (i.e., search, recommendation, and question answering) and instead focus on a single goal.
We address this by introducing the MG-ShopDial dataset that contains English conversations mixing different goals in the domain of e-commerce.
Specifically, we make the following contributions.
First, we develop a coached human-human data collection protocol where each dialogue participant is given a set of instructions, instead of a specific script or answers to choose from.
Second, we implement a data collection tool to facilitate the collection of multi-goal conversations via a web chat interface, using the above protocol.
Third, we create the MG-ShopDial collection, which contains 64 high-quality dialogues with a total of 2,196 utterances for e-commerce scenarios of varying complexity. The dataset is additionally annotated with both intents and goals on the utterance level.
Finally, we present an analysis of this dataset and identify multi-goal conversational patterns.

## Repository Structure

This repository is structured as follows:

  * `CCC/`: Source code and documentation of the Coached Conversation Collector tool.
  * `MGShopDial`: MG-ShopDial dataset card and annotation task details.
  * `MGShopDial/MGShopDial.json`: Annotated MG-ShopDial dataset. 

## Citation

If you use the resources presented in this repository, please cite:

```
@inproceedings{Bernard:2023:SIGIR,
  author =    {Bernard, Nolwenn and Balog, Krisztian},
  title =     {MG-ShopDial: A Multi-Goal Conversational Dataset for e-Commerce},
  booktitle = {Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR '23), July 23--27, 2023, Taipei, Taiwan},
  series =    {SIGIR '23},
  year =      {2023}
}
```

## Contact

Should you have any questions, please contact Nolwenn Bernard at nolwenn.m.bernard@uis.no.
