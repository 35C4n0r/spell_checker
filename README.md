# spell_checker

To build this spell checker, I had a lot of approaches in mind, but after a lot of research, I decided implemented a basic version of ``Symmetric Delete Spelling Correction`` algorithm.
You can read more about it [here](https://wolfgarbe.medium.com/1000x-faster-spelling-correction-algorithm-2012-8701fcd87a5f).

The word dictionary I'm using can be found [here](https://github.com/dwyl/english-words), it has a list of 370K+ words.

The SymetricDeleteDictionary is made with words with edit distance of 2

Runtime Metric
1000 Words with Edit distance 2 against a database of 370K+ words is ~4seconds.
1000 Words with Edit distance 3 against a database of 370K+ words is ~8seconds.
