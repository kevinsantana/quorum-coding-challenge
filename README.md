# quorum-coding-challenge

Quorum Coding Challenge: Working with Legislative Data

## Requirements

You need Python >= 3.13

## Running

You need two folders on the root folder where the `parse_votes.py` script is going to be executed. An example can be found below:

.
├── LICENSE
├── README.md
├── files
│   ├── in
│   │   ├── bills.csv
│   │   ├── legislators.csv
│   │   ├── vote_results.csv
│   │   └── votes.csv
│   └── out
│       ├── bill-vote-sponsor-analysis.csv
│       └── legislators-support-oppose-count.csv
├── parse_votes.py
└── writeup.md

To output both question 1 and question 2 CSvs, simple run:

```python
python parse_votes.py
```
