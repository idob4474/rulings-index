# rulings-index

Find an Israeli Supreme Court ruling by case number or by the parties' names, and get its exact full text.

```bash
gh api repos/idob4474/rulings-index/contents/scripts/lookup.py -H "Accept: application/vnd.github.raw" > lookup.py
python3 lookup.py 'ע"א 8146/13'
python3 lookup.py "ג'ושה אלדג'אני"
```

The texts live in the `rulings-2022` release, built by the workflow in this repo. About 97,000 documents, of which about 82,000 are judgments. Lower courts, rulings after 2022 and many rulings from before the late 1990s are not included.

## Source and credit

The data comes from the dataset [LevMuchnik/SupremeCourtOfIsrael](https://huggingface.co/datasets/LevMuchnik/SupremeCourtOfIsrael), a 2022 snapshot of the Supreme Court website, curated by Prof. Lev Muchnik (Hebrew University of Jerusalem) and Dr. Inbal Yahav Shenberger (Tel Aviv University) and published under the OpenRAIL license. Court rulings themselves are not protected by copyright under section 6 of the Israeli Copyright Act.
