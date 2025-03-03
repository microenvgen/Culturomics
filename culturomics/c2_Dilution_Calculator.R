# Opentrons OT-2; Calculate the dilution factor needed to obtain the desired 
# concentrations in all wells (culturomics #2)

metadata = c(
	'protocolName'= 'Dilution Calculator',
	'author'= 'Silvia Talavera',
	'version'= '3'
	)

# ==============================================================================
# INPUT
# - [REQUIRED] Vector specifying the last well with growth in each row
# - [OPTIONAL] Experiment and output parameters

# DESCRIPTION
# Calculate the dilution factor needed (by default, to obtain concentrations of 
# 0.015, 0.15 and 1.5 cells/100 μL). Note down the last dilution where there is
# detectable growth. Warn the user if this last dilution is very different from
# one plate to another. Assume there was originally a single bacterial clone in
# each well of the last column showing growth.
# Once the dilution factors have been obtained, the dilutions have to be done
# manually in preparation for the next step

# OUTPUT
# - Print instructions for the user

# ==============================================================================
# PLATE SPECIFICATIONS [REQUIRED]
# Last well showing growth in each row A-H
indeces = c("A" = 6,
            "B" = 6, 
            "C" = 6,
            "D" = 6,
            "E" = 6,
            "F" = 6,
            "G" = 6,
            "H" = 6)

dil_ini = 1 # if 10, initial dilution factor is 1:10
# It refers to how diluted the sample was before filling the plate. In other
# words, if there was no dilution of the original sample before filling the plate,
# write "1". If we are going to work with a flask with a sample that is 10 times
# more concentrated than the one used to fill the plate we're analysing, then
# write "10"

# ==============================================================================
# EXPERIMENTAL PARAMETERS [OPTIONAL]

dil_factor = 10 # dil_factor=10 if transfers at c1 took 20 uL into 200 uL total
well_vol = 100  # volume inside each well, in uL
# Es importante definir el volumen total del pocillo, porque afecta a los cálculos.
# Si el volumen del pocillo es 200, la concentración de células será el doble para
# que, tras añadir medio, quede a 1.5 c/100 ul. Actualmente, usamos placas de 384
# en las que no añadimos medio, es decir, el volumen del pocillo es 100 ul y lo que 
# añadimos son 100 ul del cultivo. 

wanted_final_vol = 100 # we want concentrations of 1.5, 0.15 & 0.015 cells
                       # in this volume (uL)


# ==============================================================================
# OUTPUT PARAMETERS [OPTIONAL] -- Decide here if we want to do 1 or 2 dilutions
# and the maximum volume we want to work with. It's a good idea to only adjust
# it after checking the output of this script once

# With the default parameters:
# - dilute a variable quantity in a total of 5 mL, which will be the "first tube" 
# - dilute 100 uL (vol_from_1st_to_2nd) from "first tube" into a "second tube",
#   which is actually a 50 mL flask (vol_2nd_tube).
# - dilute 100 uL (vol_from_2nd_to_f) from "second tube" to a "final tube" with
#   a total of 55 mL (vol_final_tube)

vol_1st_tube   = 10 #mL

vol_from_1st_to_2nd = 100 #uL

vol_2nd_tube    = 10 #mL

vol_from_2nd_to_f = 50 #uL

vol_final_tube = 48 #mL # <-- how much volume do we need in the end?


# # ==============================================================================
# #1: Parsing the input data

if ((max(indeces)-min(indeces)) > 1) {
  warning(paste("The most diluted well showing growth varies between",
                min(indeces),"(",dil_factor**min(indeces),")","y la",
                max(indeces),"(",dil_factor**max(indeces),")"))
}


# ==============================================================================
# #2: Obtain the mean for all replicates/rows

## Dilution factor to get "1" cell in a well with "well_vol" 
f1 = dil_ini * mean(dil_factor**indeces)   
##   10      * media(10**7, 10**8, 10**7...)


# ==============================================================================
# #3: Obtain the necessary dilution factors to get 1.5, 0.15 & 0.015 cells per 
#     100 ul   

## Dilution factor to obtain 1.5 cells in wanted_final_vol
f1_5 = (f1/1.5) * (wanted_final_vol / well_vol)

## Dilution factor to obtain 0.15 cells in wanted_final_vol
f0_15 = (f1/0.15) * (wanted_final_vol / well_vol)

## Dilution factor to obtain 0.015 cells in wanted_final_vol
f0_015 = (f1/0.015) * (wanted_final_vol / well_vol)

# ==============================================================================
# #4: Print instructions

f_extra = ((1000*vol_2nd_tube)/vol_from_1st_to_2nd) * 
  +   ((1000*vol_final_tube)/vol_from_2nd_to_f)

for (i in c(1,2,3)){
  text = c("1.5", "0.15", "0.015")[i]
  f = (c(f1_5, f0_15, f0_015)/f_extra)[i] # f_extra is the most important bit here
  
  writeLines(paste0("To get ",text,"cells en ",wanted_final_vol," uL:\n------------------------------------"))
  writeLines(paste0("First, dilute ",vol_1st_tube / (f/1000)," uL into ",vol_1st_tube," mL")) # /1000 converts to uL
  
  writeLines(paste0("Then, do a 1:",f_extra," dilution, following these steps:"))
  writeLines(paste0("1. Dilute ",vol_from_1st_to_2nd," uL from the mix in ",vol_1st_tube," into a new ",vol_2nd_tube," mL tube (1:",(1000*vol_2nd_tube)/vol_from_1st_to_2nd,")"))
  writeLines(paste0("2. Dilute ",vol_from_2nd_to_f," uL from the mix in ",vol_2nd_tube," into a new ",vol_final_tube," mL tube (1:",(1000*vol_final_tube)/vol_from_2nd_to_f,")\n"))
}
