# MGSM-Rev2
MGSM-Rev2 is a revised version of the Multilingual Grade School Math (MGSM) benchmark, originally proposed in the paper [Language models are multilingual chain-of-thought reasoners](http://arxiv.org/abs/2210.03057).
This revision improves upon the baseline dataset by correcting errors, mainly, but not exclusively, translation inaccuracies. As a verification step, we confirmed that the revised questions remain solvable by current Large Language Models (LLMs). More details can be found in [Mind the Gap... or Not? How Translation Errors and Evaluation Details Skew Multilingual Results](https://arxiv.org/abs/2511.05162).

## Languages
The benchmark maintains the original structure of 250 problems translated into the following 10 languages:

- Spanish
- French
- German
- Russian
- Chinese
- Japanese
- Thai
- Swahili
- Bengali
- Telugu

## Data Format
The data is provided in TSV (tab-separated values) files with the following structure:

- Column 1: Question
- Column 2: Answer

The data can be used as a direct replacement of the original [MGSM dataset](https://huggingface.co/datasets/juletxara/mgsm) since the format is identical to it.

# Metadata
The `MGSM-Rev2/replaced_questions.json` file contains a record of which questions were replaced from the original dataset for each language. Note: Question numbering uses 1-based indexing.

## License
This dataset is released under the [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.en) (Creative Commons Attribution-ShareAlike 4.0 International) license.

## Citation Information

```bibtex
@misc{peter2025mindgapnottranslation,
      title={Mind the Gap... or Not? How Translation Errors and Evaluation Details Skew Multilingual Results}, 
      author={Jan-Thorsten Peter and David Vilar and Tobias Domhan and Dan Malkin and Markus Freitag},
      year={2025},
      eprint={2511.05162},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2511.05162}, 
}

@misc{shi2022languagemodelsmultilingualchainofthought,
      title={Language Models are Multilingual Chain-of-Thought Reasoners}, 
      author={Freda Shi and Mirac Suzgun and Markus Freitag and Xuezhi Wang and Suraj Srivats and Soroush Vosoughi and Hyung Won Chung and Yi Tay and Sebastian Ruder and Denny Zhou and Dipanjan Das and Jason Wei},
      year={2022},
      eprint={2210.03057},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2210.03057}, 
}

@misc{cobbe2021trainingverifierssolvemath,
      title={Training Verifiers to Solve Math Word Problems}, 
      author={Karl Cobbe and Vineet Kosaraju and Mohammad Bavarian and Mark Chen and Heewoo Jun and Lukasz Kaiser and Matthias Plappert and Jerry Tworek and Jacob Hilton and Reiichiro Nakano and Christopher Hesse and John Schulman},
      year={2021},
      eprint={2110.14168},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2110.14168}, 
}

```
