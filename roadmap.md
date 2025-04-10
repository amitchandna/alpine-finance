## ROADMAP 

### What this entails
As this project is fleshed out more and more it is inevitable that new information will need to be synthesized into the project. This aims to do that

### Data collection:
* What data to collect?
  * Data set will consist of as many 10-k forms from the SEC as possible. Every year a new 10-k should be released
  * Training data will be done on data from 2020(?)-2022.
  * Testing data will consist of 2023 forms. 
  * Model comparison will look at the market performance in 2023; did the model select the correct stocks?

### Pre-processing steps
* Merge all sections of the text into one line of data - see table_drafts.ods, sheet raw_data_storage

### Modelling
* A singular model will be selected, the main models to consider:
  1. SVMs
  2. Markov Chain Derivatives
     1. ie: Hidden Markov Model
  3. Naive Bayes
  4. Conditional random fields
  5. Neural Networks (Probably all will need to deployed via NN given the dataset size)

### Outcome usage
The results of the model will consist of a signal that determines whether a security is a worthwhile investment
  * Quantifiable by
    * Value Investing methodologies
    * PNL statements
    * Past performance + expected performance

