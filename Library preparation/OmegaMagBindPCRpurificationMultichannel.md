1-Description
=
PCR (or DNA) purification using magnetic beads (Omega Bio-Tek Mag-Bind TotalPure NGS (SKU: M1378-00)).

Estimated running time: 1h:37m (96 samples)  Pausa a 1h 14 min


**Tip isolator preparation**: Prepare a clean empty 300ul opentrons tiprack (rinse opentrons tips rack with 0.1 N HCl and wash 3 times with MQ water). Wrap it in aluminum foil and autoclave it. When you put it in the drying oven, remove the aluminum foil so that it dries better.

> IMPORTANT: use a tip rack with tips to calibrate tip isolator, and change it before starting the protocol (there is a pause)  

> **IMPORTANT**: After calibration there is a pause and the script itself calculates the necessary volumes to add to the reservoir. Do not add anything until the robot tells you to.

> **BEADS**: Beads are prepared on a PCR plate using the scripts prepare_MagneticBeadsPlate_highVol.py or prepare_MagneticBeadsPlate_lowVol.py depending on the volume needed per well, which will depend on the bead ratio you want to use. We generally use a ratio of 0.85 and since the PCR volume we put is 20, the bead volume must be 17 ul (PCR_volume * beads_ratio).

> **REMOVE TIPS**: If a sample column is not complete, you may choose to remove tips (only those that will pipette the beads). The order of the tip boxes is slot 5, 6, 7 and 8. First add the water to the tip_isolator with a column of tips. Then add the beads. If we have 3 columns (the third one incomplete), we will have to remove the tips from the 4th column of slot 5. That is, we will have to remove the tips from column + 1 (because it first uses 1 column with water). If the incomplete column is 12, we will have to remove the tips from column 1 of slot 6. **Verify this**


2-Settings
= 

**Api level**  

To use a tip isolater version 2.9 is required.  
Higher api levels do not seem to work (at least version 2.11).  

**Variables**  

Number of columns to process = 12  
PCR Volume = 20  
Total volume = 50 (SN to remove after binding to the beads)  
Ethanol washes = 2x150 ul  
Elution volume = 30 ul  

> To change these values go to the "Protocol variables" section of the script.  

**Pipettes**  

Right\) p300_multi_gen2  

**Slots**  

1\) [Magnetic module](https://opentrons.com/modules/magnetic-module/) with samples loaded into a [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt?category=wellPlate&manufacturer=NEST))  
2\) [nest_12_reservoir_15ml](https://labware.opentrons.com/nest_12_reservoir_15ml?category=reservoir)  
	<!--
	A1\) Magnetic Beads (Omega Bio-Tek Mag-Bind TotalPure NGS (SKU: M1378-00))  
		> Bead volumen: PCR volume (20 ul) * beads ratio (1) * number of samples (number of columns * 8)  
		> Beads must be thoroughly shaken, vortexed and resuspended with the 10 ml pipettes to avoid clogs.  
		> Recover remaining beads at the end   
	-->
	<ul>
	A2\) Elution buffer or MQ water  
		> Elution volume: (20 ul) * number of samples  
	A4-A6\) 11 ml sterile Water (for tip isolator)  
	A9-A12\) 11 ml 70% Ethanol  
		> Ethanol volumen: (150 ul) * Number of washes (3) * number of samples, divided into several wells  
	</ul>
3\) Output plate ([nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt?category=wellPlate&manufacturer=NEST))  
4\) Tip isolator(Empty rack [opentrons_96_tiprack_300ul](https://labware.opentrons.com/opentrons_96_tiprack_300ul?category=tipRack&manufacturer=Opentrons))  
5, 6, 7 & 8\) [opentrons_96_tiprack_300ul](https://labware.opentrons.com/opentrons_96_tiprack_300ul?category=tipRack&manufacturer=Opentrons))  
10\) Input plate ([nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt?category=wellPlate&manufacturer=NEST) or [pcr_plate_semi_skirt](https://github.com/microenvgen/OT2/blob/426f8d04e7917903d9d31d308ecbcd8541383280/custom_labware/pcr_plate_semi_skirt.md)).  


3-Deck
= 

![Deck](./OmegaMagBindPCRpurificationMultichannel.svg)


4-CHANGELOG
=

#### Notes for future changes...  


### V5

- I add a variable to choose the input plate format: [nest_96_wellplate_100ul_pcr_full_skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt?category=wellPlate&manufacturer=NEST) \[Default\] o [pcr_plate_semi_skirt](https://github.com/microenvgen/OT2/blob/426f8d04e7917903d9d31d308ecbcd8541383280/custom_labware/pcr_plate_semi_skirt.md).  

> I can't put it as a parameter in the app because I need to use apiLevel=2.9 for tip_isolator to work.

### V4

Magnetic beads are no longer placed in the reservoir, but a PCR plate with the required number of beads per well must be prepared using the "prepare_MagneticBeadsPlate_highVol.py" or "prepare_MagneticBeadsPlate_lowVol.py" protocol. This plate will be placed on the magnetic module. The plate with the samples (PCRs) will be placed in slot 10. Then, the robot transfers the samples from the input plate to the magnetic plate where they will come into contact with the magnetic beads.

We modified step 2: instead of incubating for 5 minutes, we mix the samples with the beads 2 times (5 repetitions of 150 ul).

### V3

During the transfer of the eluate to the final plate we have observed that it drips. To avoid this we have added some changes:
- We put a 5 ul air_gap so that it does not drip from the magnet to the output plate
- We add a blow_out on the output plate
- We add a pipette agitation on the output plate so that the remaining drops fall

### V2 

I add a calculation of the number of tip boxes needed so that I do not have to put them all in.

### V1  

#### Protocol:  
1. Shake or vortex the Mag-Bind® Total Pure NGS to resuspend any particles (Mix in OT2)  
2. Add the desired volume of Mag-Bind® Total Pure NGS to each well based upon desired fragment size to recover  
3. Pipet up and down 5-10 times or vortex for 30 seconds.  
4. Let sit at room temperature for 5 minutes.  
5. Place the plate on a magnetic separation device to magnetize  
6. Aspirate and discard the cleared supernatant  
7. With the plate remaining on the magnet, add 200 μL 70% ethanol to each well  
8. Let sit at room temperature for 1 minute. It is not necessary to resuspend the Mag-Bind® Total Pure NGS.  
9. Aspirate and discard the cleared supernatant. Do not disturb the Mag-Bind® Total Pure NGS  
10. Repeat Steps 7-9 for a second 70% ethanol wash step  
11. Leave the plate on the magnetic separation device for 5-15 minutes to air dry the Mag-Bind® Total Pure NGS. Remove any residual liquid with a pipettor.  
12. Remove the plate from magnetic separation device  
13. Add 30-40 µL Elution Buffer (not provided) to each well.  
14. Pipet up and down 20 times or vortex for 30 seconds.  
15. Let sit at room temperature for 5 minutes.  
16. Place the plate on a magnetic separation device to magnetize  
17. Transfer the cleared supernatant containing purified DNA to a new 96-well microplate and seal with non-permeable sealing film  

