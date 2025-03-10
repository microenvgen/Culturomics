Description
=

Generic protocol for performing the second barcoded PCR with the robot (using the robot's own thermocycler or an external one).

**Parameters:**

1. Internal or external PCR (external by default)
2. 1/10 dilution of the template DNA (no by default)
3. Type of template DNA plate (NEST fullskirt or Shapire semi-skirt, NEST by default)
4. Number of cycles (internal only)
5. Melting temperature (internal only)

**Protocol**

1. defrost reagents and plates
> - Template, dH2O, Bff, dNTPs, Pfw, Prv (specific ones with Ns or not). 
> - Check that there is enough of each one and enzymes (See below). 
2. Clean the deck with isopropanol. 
3. Change pipettes if necessary **(multi20 on the right)**. 
4. If the PCR is internal, put the PCR module (slots 7-11), clean the PCR silicone with 10% bleach and distilled water and **note silicone used**. 
5. Place PCR plate: 
> - Nest fullskirt in PCR module (internal). 
> - Shapire semi-skirt in slot 7 with its [adapter](https://github.com/microenvgen/OT2/blob/426f8d04e7917903d9d31d308ecbcd8541383280/custom_labware/pcr_plate_semi_skirt.md) (external). 
6. Place 20 ul tips with opentrons filters in slots 1, 2 and 9. 
7. Make the PCR reaction mix in a Falcon 15 and mix well with a vortex:

|                   |  Units     | [Initial] | [Final] |  Vol (25 µl) | Pool 109X |
|-------------------|:----------:|:---------:|:-------:|:------------:|:---------:|
| Q5 Pol            |    U/µl    |     2     |   0,02  |     0,25     |   27,25   |
| Q5 Reac Buffer    |      X     |     5     |    1    |     5,00     |   545,00  |
| dNTP              |     mM     |     10    |   0,40  |     1,00     |   109,00  |
| Primers   P5&P7*  | µM -> pmol |     6     |  12,00  |     2,00     |     -     |
| Template          |      -     |     -     |    10   |     3,00     |     -     |
| H2O (NFW/A)       |      -     |     -     |    -    |     13,75    |  1498,75  |
|                   |            |           |         | Vol total--> |  2180,00  |
*The robot provides them, although they must be taken into account here to properly prepare the mix with the appropriate concentrations.

8. Distribute reaction mix into the first 2 columns of a full-skirt Nest PCR plate and place in slot 3 (133 ul per well). 
9. If dilution of the template DNA is required, place the Saphire semi-skirt plate with its adapter in slot 5 and add 140 ul of clean water (NFW) in columns 5 and 6 of the reagent plate in slot 3. 
10. Place the plate with the template DNA in slot 4 (give it a 1 min spin beforehand). 
11. Place the Barcode plate in slot 6 (note which mix you are going to use). 
> At the end of the PCR, the remains of the barcodes can be stored at 4ºC by labeling the plate with the name and date of the current experiment so that if you have to repeat the PCR of this same experiment, you can reuse the same plate. Once the experiment is complete, the remains of these barcodes should be thrown away.


> To repeat this second PCR (and the first one) for some samples, you can use the script "de_9_a_1.py" which will group the samples that did not come out of this PCR and others, both in the samples and in the barcode plates, so that the barcodes will be in the required positions to use them with the samples that did not come out. 
11. Launch the Second_PCR.py script
- If dilution has been selected, perform the dilution. 
- Then distribute 20 ul of the PCR reaction mix on the PCR plate. 
- Add 3 ul of the template plate (diluted or not, according to the selected parameters) to the PCR plate. 
- Add 3 ul of the barcode plate. 
- If the PCR is external, the protocol ends here. The PCR plate must be sealed and taken to the external thermal cycler. The template DNA plate must also be sealed and stored appropriately. 
- If the PCR is internal, the PCR plate must be sealed and the PCR protocol must be pressed to execute. While the PCR protocol is running, the template DNA plate and the rest of the labware can be collected.

Settings
= 

### Pipettes

Right\) p20_multi_gen2  

### Slots

1, 2 y 9): [opentrons_96_tiprack_20ul](https://opentrons.com/products/opentrons-20-l-tips-160-racks-800-refills?sku=999-00007)  
3): Reagents [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/#/?loadName=nest_96_wellplate_100ul_pcr_full_skirt)  
4) template DNA [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/#/?loadName=nest_96_wellplate_100ul_pcr_full_skirt)  
5) If dilution is required: Diluted template DNA[pcr_plate_semi_skirt](https://github.com/microenvgen/OT2/blob/426f8d04e7917903d9d31d308ecbcd8541383280/custom_labware/pcr_plate_semi_skirt.md)  
6) Barcodes plate [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/#/?loadName=nest_96_wellplate_100ul_pcr_full_skirt)  
7) PCR plate [pcr_plate_semi_skirt](https://github.com/microenvgen/OT2/blob/426f8d04e7917903d9d31d308ecbcd8541383280/custom_labware/pcr_plate_semi_skirt.md)  

or

7-8-10-11) [PCR module](https://opentrons.com/products/modules/thermocycler/) + PCR plate [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt?category=wellPlate&manufacturer=NEST)  

CHANGELOG
=

### Notes for future changes...

A parameter could be added to define the number of columns to be made in case a complete plate is not needed.