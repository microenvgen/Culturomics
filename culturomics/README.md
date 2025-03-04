1-Introduction
=

In order to isolate bacterial clones, we need to first decide on a dilution factor. To that end, we’ll start by screening different, increasing dilution factors (“Appropriate Dilution”) and selecting the last one where we can detect bacterial growth (“Dilution Calculator”). After that, we’ll dilute further as to obtain concentrations of 0.015, 0.15 and 1.5 cells per 100 μL, in three separate well plates (“Diluted Growth”).

In this series of protocols, we assume that if only **30% of wells** show growth in a given plate, the most likely possibility is that the growth in each well was sparked by a single cell and therefore each well contains an isolated clone. If that percentage is surpassed, we’ll discard the plate. Based on this assumption and with help of optical density measures we’ll select plates containing single clones (“Plate Evaluation”).

The cultures in these plates will be conserved in glycerol and also undergo DNA extraction and PCR. Both the PCRs and the DNA extraction can be done with the OT-2 robot (“Well Selection”). The PCR’s results can be evaluated with fluorescent nucleic acid stain (“Picogreen”). Once they are known, the samples will get their DNA concentrations normalized (“Normalize DNA Concentration”) and finally they will be prepared for 16S sequencing (“PCR Nested”).

2-Step and scripts
=


1. Appropriate Dilution

> Titer microbial sample to stimated the proper dilution for limiting dilution bacterial isolation.  
> [c1_Appropriate_Dilution.py](./c1_Appropriate_Dilution.md)

2. Dilution Calculator

> Calculate the dilution factor needed to obtain the desired concentrations in all wells.  
> [c2_Dilution_Calculator.R](./c2_Dilution_Calculator.R)

3. Diluted Growth

> Load the plates with the appropriate dilution and get isolated clones.  
> [c3_Diluted_Growth.py](./c3_Diluted_Growth.md)

4. Plate Evaluation

> Check controls and select plates with growth in less than 30% of wells.  
> [c4_Plate_Evaluation.R](./c4_Plate_Evaluation.R)

5. Well Selection

> Transfer up to 93 isolate from the 384 plates (accordingly to plate evaluation) to a new plate, prepare glycerol stocks and extract DNA.  
> [c5_Well_Selection_part_1.py & c5_Well_Selection_part_2.py](./c5_Well_Selection.md)






