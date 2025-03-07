# Opentrons OT-2; Plate Evaluation (culturomics #4)
# this R script                                                       
# - checks controls; if they're wrong throws a warning and excludes those plates
# - discards those plates with growth in more than 30% of wells (there might
#   be more than one clone in a single well)
# - saves the location of a total "w" wells showing growth (from different 
#   plates if necessary)

# ===INPUT======================================================================
## Where are the files with the optical density readings?
setwd("C:/Users/AR.5020963/Desktop/OT2_plates")

## File names, from most diluted to most concentrated
od_readings_files = c("diluidaFinal.csv",
                      "intermediaFinal.csv",
                      "intermediaasteriscoFinal.csv",
                      "concentrado.csv")

## What's the minimum OD for it to have growth?
threshold = 0.25

## Assume no valid growth in corners
skip_corners = TRUE

## If the percentage of wells with growth is higher than this value, exclude the
## plate (from 0 to 1)
excl_perc = 1 # 1 == don't exclude

## Total (maximum number) wells we want to save
w = 93

## Should we exclude those plates with bad controls?
exclude_bad_pos_controls = FALSE
exclude_bad_neg_controls = FALSE

## Suffix for output files. For instance, if the suffix is "0015" the output for
## that plate will be saved as wells_0015
plate_names = c("0015", "015", "015b", "15")
filename = "wells_c4.csv"
# ==============================================================================
# #1: Read .CSV with OD measures
plates = lapply(
  od_readings_files, 
  FUN=function(f){
    csv=read.csv(f, sep=";", header=T, row.names = 1)[1:24]
    csv=as.data.frame(lapply(csv, FUN= function(col) {gsub(",", ".",col)}))
    rownames(csv) = c(LETTERS[1:16])
    colnames(csv) = as.character(c(1:24))
    return(csv)
  }
)

names(plates) <- plate_names

perc   = as.numeric(lapply(plates,
                           FUN=function(x){sum(x>threshold)/384}))

writeLines("Growth percentage in the plates:")
writeLines(paste0(names(plates),":\t",round(perc*100,2),"%"))

# ==============================================================================
# #2: Select those plates with growth in less than 30% of the wells and with
#     good controls

pos_controls = lapply(plates,
                  FUN=function(p){
                    # Positive controls must show growth
                    c("B24-"=(p["B",24] < threshold),
                      "D24-"=(p["D",24] < threshold),
                      "F24-"=(p["F",24] < threshold),
                      "H24-"=(p["H",24] < threshold))
                  })
                    
neg_controls = lapply(plates,
                      FUN=function(p){
                      # Negative controls must not
                      c("J24+"=(p["J",24] > threshold),
                        "L24+"=(p["L",24] > threshold),
                        "N24+"=(p["N",24] > threshold),
                        "P24+"=(p["P",24] > threshold))
                  })

good_pos_controls = mapply(pos_controls,FUN=function(c){sum(c)==4}) # 4 controls ok
good_neg_controls = mapply(neg_controls,FUN=function(c){sum(c)==4}) # 4 controls ok

# throw warning for (or exclude) files with bad controls
if (exclude_bad_pos_controls) {
  for (file in od_readings_files[good_pos_controls==FALSE] ) {
    warning(paste0("Positive(+) controls are WRONG for ", file, ". Excluded."))
  }
  selected_plates = plates[good_pos_controls & perc<excl_perc]
} else {
  for (file in od_readings_files[good_pos_controls==FALSE] ) {
    warning(paste0("Positive(+) controls are WRONG for ", file, "."))
  }
  selected_plates = plates[perc<excl_perc]
}


if (exclude_bad_neg_controls) {
  for (file in od_readings_files[good_neg_controls==FALSE] ) {
    warning(paste0("Negative(-) controls are WRONG for ", file, ". Excluded."))
  }
  selected_plates = selected_plates[good_neg_controls & perc<excl_perc]
} else {
  for (file in od_readings_files[good_neg_controls==FALSE] ) {
    warning(paste0("Negative(-) controls are WRONG for ", file, "."))
  }
}

# ==============================================================================
# #3: Compute and show total
total_per_selected_plates = as.numeric(lapply(selected_plates,
                                              FUN=function(x){sum(x>threshold)}))
total = sum(total_per_selected_plates)

writeLines(paste("Total wells with growth, without taking positive controls into account (but without excluding the other 3 corners)):",total-(length(selected_plates)*4)))
for (i in 1:length(selected_plates)){
  writeLines(paste0("Plate ",i,": ",total_per_selected_plates[i]-4))
}

# ==============================================================================
# #4: Generate .csv file (no actual .csv extension by default)
names = mapply(1:24,FUN=function(i){paste0(LETTERS[1:16],i)})
"%nin%" = Negate("%in%")

if (total>0) {
  # First, second, third and fourth plate                                       
  # ============
  saved_wells = 0
  saved_plates = 0
  for (i in 1:length(selected_plates)) {
    platename = paste0("wells_",names(selected_plates[i]))
    if (total_per_selected_plates[i] < (w-saved_wells)) {
      #~# save all wells with growth except controls
      g = names[which(selected_plates[[i]]>threshold)]     
      g = g[g %nin% c("J24", "L24", "N24", "P24")]
      if (skip_corners) {
        g = g[g %nin% c("A1", "P1", "A24")]
      }
      write(paste(c(platename, g), collapse=","), #> save a line per plate
                filename, append = (i!=1))        #> if not the first plate, create new file
      saved_plates = saved_plates + 1
      
      saved_wells=saved_wells+length(g)
      
      writeLines(paste0("Finished saving mapping for plate ",i,
                     " (total of ",length(g)," wells)."))
    
    } else if ((w - saved_wells) > 0) { 
      # If I have "0" left to save, I don't want an empty file!
      g = names[which(selected_plates[[i]]>threshold)]      
      g = g[g %nin% c("J24", "L24", "N24", "P24")]
      if (skip_corners) {
        g = g[g %nin% c("A1", "P1", "A24")]
      }
      g = sample(g,w-saved_wells,replace=FALSE)
      write(paste(c(platename, g), collapse=","), #> save a line per plate
            filename, append = (i!=1))        #> if not the first plate, create new file
      saved_plates = saved_plates + 1
      saved_wells=saved_wells+length(g)
      
      writeLines(paste0("Finished saving mapping for plate ",i,
                     " (total of ",length(g)," wells)."))
      writeLines(paste0("Finished saving up to ", w, " wells."))
      
    }
  }
  
  writeLines(paste("Total plates saved:",saved_plates))
  
}
