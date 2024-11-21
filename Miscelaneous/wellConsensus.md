### wellConsensus

#### Improvements

Quizás deberíamos exigir un mínimo de 3 secuencias por pocillo (fastq). Hay casos en los que sólo hay 1, y no dan problemas, pero cuando hay 2 y son muy divergentes hay muchos "N" en l consenso porque ninguna supera el 50% exigido. Con 3, el porcentaje sería 33/66 y tendríamos consenso o 33/33/33 donde tendríamos "N".

#### Warnings 1 (sequence length?)

```

mothur > align.seqs(candidate=B10_Well_B1_Locus_16S_long.good.fasta, template=silva.seed_v138_1.align, processors=12 )

[WARNING]: 1 of your sequences generated alignments that eliminated too many bases, a list is provided in B10_Well_B1_Locus_16S_long.good.flip.accnos.
[NOTE]: 1 of your sequences were reversed to produce a better alignment.

```


#### Warning 2 (Too many error? )

```
mothur > degap.seqs(fasta=E7_Well_C2_Locus_16S_long.good.filter.cons.fasta)

Using 64 processors.
Degapping sequences from E7_Well_C2_Locus_16S_long.good.filter.cons.fasta ...
[WARNING]: We found more than 25% of the bases in sequence conseq to be ambiguous. Mothur is not setup to process protein sequences.
1
It took 0 secs to degap 1 sequences.
```
