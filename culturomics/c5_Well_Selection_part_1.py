from opentrons import protocol_api
from collections import defaultdict
from opentrons.protocol_api import RuntimeParameterRequiredError
import os
import platform
import string
import sys


metadata = {
	'protocolName': 'Diluted Growth',
	'author': 'Silvia Talavera and Alberto Rastrojo',
	"apiLevel": "2.20",
	'version': '2'
}

def add_parameters(parameters):

	parameters.add_csv_file(
		variable_name="csv_file",
		display_name="csv_file",
		description="comma-separated values"
	)

def run(protocol: protocol_api.ProtocolContext):

	# =============================================================================
	# Input data and variables
	# =============================================================================
	protocol.set_rail_lights(True)
	tips_brand = "white_96_tiprack_200ul"

	# =============================================================================
	# Functions
	# =============================================================================
	def cmt(msg): 
		protocol.comment("="*100 + "\n" + msg + "\n" + "="*100)

	def flash(msg):

		light_status = 0
		if protocol.rail_lights_on: 
			light_status = 1

		for _ in range(5):
			protocol.set_rail_lights(False)
			protocol.delay(seconds=0.5)
			protocol.set_rail_lights(True)
			protocol.delay(seconds=0.5)

		protocol.pause(msg)

		if light_status: 
			protocol.set_rail_lights(True)
		else:
			protocol.set_rail_lights(False)

	# =============================================================================
	# Processing input files
	# =============================================================================
	# Input file format
	# wells_0015,O1,G2,M2,E3,I3,A4,I4,M5,N5,D6,K6,M6,E7,H8,J8,M8,J9,N10,O10,B12,I12,B16,D17,L18,O20,E21,P22
	# wells_015,E1,J1,M1,A2,F2,G2,M3,N3,O3,P3,A4,K4,D7,I7,K7,O7,I8,B9,P9,O10,A13,N13,A14,B14,D14,O14,E15,J15,K15,O15,A16,B19,D19,B20,F20,D21,O22
	# wells_015b,I14,B3,L21,D3,A13,B2,B7,B9,F16,O9,D19,O3,N13,M2,D14,C20,O10,P4,J9,F9,K19,A15,D1,L15,D7,D16,E3,G15,H20
	if protocol.is_simulating():
		selected_wells = {
			'wells_0015': ['O1', 'G2', 'M2', 'E3', 'I3', 'A4', 'I4', 'M5', 'N5', 'D6', 'K6', 'M6', 'E7', 'H8', 'J8', 'M8', 'J9', 'N10', 'O10', 'B12', 'I12', 'B16', 'D17', 'L18', 'O20', 'E21', 'P22'], 
			'wells_015': ['E1', 'J1', 'M1', 'A2', 'F2', 'G2', 'M3', 'N3', 'O3', 'P3', 'A4', 'K4', 'D7', 'I7', 'K7', 'O7', 'I8', 'B9', 'P9', 'O10', 'A13', 'N13', 'A14', 'B14', 'D14', 'O14', 'E15', 'J15', 'K15', 'O15', 'A16', 'B19', 'D19', 'B20', 'F20', 'D21', 'O22'], 
			'wells_015b': ['I14', 'B3', 'L21', 'D3', 'A13', 'B2', 'B7', 'B9', 'F16', 'O9', 'D19', 'O3', 'N13', 'M2', 'D14', 'C20', 'O10', 'P4', 'J9', 'F9', 'K19', 'A15', 'D1', 'L15', 'D7', 'D16', 'E3', 'G15', 'H20']
			}
	else:
		try:
			# raw_csv_data = [[row1,..], [row2,...]]
			raw_csv_data = protocol.params.csv_file.parse_as_csv(delimiter=",")
			selected_wells = {}
			for row in raw_csv_data:
				selected_wells[row[0]] = row[1:]

		except RuntimeParameterRequiredError as error:
			flash(f"#### ERROR READING INPUT FILE:{error}")

	total_wells =sum([len(selected_wells[plate]) for plate in selected_wells])
	required_input_plates = sorted(list(selected_wells.keys()))

	if total_wells > 93:
		flash("ERROR: The number of selected wells is higher than 93. Review input files.")
		quit() # The app is blocked when this happens

	if total_wells == 0:
		flash("ERROR: The number of selected wells is 0. Review input files.")
		quit() # The app is blocked when this happens

	# =============================================================================
	# Labware
	# =============================================================================
	#Pipettes
	tips = protocol.load_labware(tips_brand, 1)
	s300 = protocol.load_instrument('p300_single_gen2','left', tip_racks=[tips])

	# input plates ['wells_0015', 'wells_015', 'wells_015b']
	slots = [3,6,9]
	input_plates = [protocol.load_labware('corning_384_wellplate_112ul_flat', slot, plate_name) for slot, plate_name in zip(slots, required_input_plates)]

	for plate in input_plates:
		cmt(f"### Place plate {plate}")
	flash("### Check plate positions")

	# pcr_mod
	pcr_mod = protocol.load_module('thermocyclerModuleV2')
	pcr_mod.open_lid()
	pcr_plate = pcr_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')

	# Reagents
	reservoir = protocol.load_labware('nest_12_reservoir_15ml', 4)
	# A1 --> culture medium for negative controls

	# =============================================================================
	cmt("#### 1. Transferring 35 ul from 384 plates to PCR plate onto PCR module ")
	# =============================================================================
	dest = 0
	for plate in input_plates:
		plate_name = plate.name
		wells = selected_wells[plate_name]
		for well in wells:
			s300.transfer(35, 
				plate.wells_by_name()[well].bottom(z=1), 
				pcr_plate.wells()[dest].bottom(z=1), 
				new_tip="always")
			dest = dest + 1

	# =============================================================================
	cmt("#### 2. Adding a negative control to F12 position in PCR plate ")
	# =============================================================================
	s300.transfer(35, 
		reservoir.wells_by_name()["A1"].bottom(z=1), 
		pcr_plate.wells_by_name()["F12"].bottom(z=1), 
		new_tip="always")

	# ==========================================================================
	flash("#### END: run c5_Well_Selection_part_2.py")
	# =============================================================================

