from opentrons import protocol_api

metadata = {
	'protocolName': 'First PCR',
	'author': 'Alberto Rastrojo',
	'apiLevel': '2.20',
	'version': '1'
}

# =============================================================================
# Runtime parameters
# =============================================================================
def add_parameters(parameters):

	parameters.add_str(
		variable_name="pcr_location",
		display_name="PCR internal or external",
		description="Internal: opentrons thermocycler (nest full-skirt) or External: external thermocycler (semi-skirt).",
		default="external",
		choices=[   {"display_name": "internal", "value": "internal"},
					{"display_name": "external", "value": "external"},]
	)

	parameters.add_int(
		variable_name="number_of_cycles",
		display_name="Nº of cycles (internal)",
		description="Number of cycles. Only if internal. ",
		default=28,
		minimum=1,
		maximum=45
	)

	parameters.add_int(
		variable_name="melting_temp",
		display_name="TM (internal)",
		description="Melting temperature. Only if it is internal",
		default=55,
		minimum=20,
		maximum=80
	)

def run(protocol: protocol_api.ProtocolContext):

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
	# Input data and variables & parameters
	# =============================================================================
	protocol.set_rail_lights(True)
	number_of_cycles = protocol.params.number_of_cycles
	pcr_location = protocol.params.pcr_location
	melting_temp = protocol.params.melting_temp

	if pcr_location == "interna":
		flash(f">>>>>Review the parameters<<<<<< *PCR {pcr_location}* *{number_of_cycles} cycles* *{melting_temp}ºC of TM* >>>Don't forget to write down this information in your lab notebook<<<")
	else:
		flash(f">>>>>Check the parameters<<<<<< *PCR {pcr_location}* >>>Place the semi-skirted plate with the adapter in position 7<<< The number of cycles and the TM must be entered correctly in the external thermal cycler you are going to use.>>>Don't forget to write this information down in your laboratory notebook<<<.")

	# =============================================================================
	# Labware
	# =============================================================================
	# Pipettes
	m20_tipracks = [protocol.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in [1, 2]]
	m20 = protocol.load_instrument('p20_multi_gen2', 'right', tip_racks=m20_tipracks)

	# input DNA (template)
	template = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', 4)

	# Reagent
	reagents = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', 3)

	# Loading Termocycler/output plate
	if pcr_location == "external":
		PCR = protocol.load_labware('pcr_plate_semi_skirt', 7)

	else: # internal
		# PCR (slots 7-11)
		tc_mod = protocol.load_module('thermocyclerModuleV2')
		# if not tc_mod.lid_position=="open":
		tc_mod.open_lid()
		PCR = tc_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')

	# =============================================================================
	# Protocol
	# =============================================================================

	# =============================================================================
	cmt("#### 1. Distribute 20 µL of reagent columns 1-2 to each PCR well")
	# =============================================================================
	m20.pick_up_tip()
	m20.distribute(20,
				source = reagents.columns()[0],
				dest = PCR.columns()[0:6],
				new_tip = "never",
				disposal_volume = 0,
				trash = False)
	m20.distribute(20,
				source = reagents.columns()[1],
				dest = PCR.columns()[6:12],
				new_tip = "never",
				disposal_volume = 0,
				trash = False)
	m20.drop_tip()

	# =============================================================================
	cmt("#### 2. Add 5 µl of template DNA")
	# =============================================================================
	m20.transfer(5,
				source = template.wells(),
				dest = PCR.wells(),
				new_tip = "always",
				trash = True,
				mix_after = (1, 20))

	# =============================================================================
	# Correr PCR o avisar del final
	# =============================================================================

	if pcr_location == "external":
		flash("#### 3. Save template, put sticker on PCR plate and put in external thermal cycler")

	else:
		flash("#### 3. Save template and put sticker on PCR plate")

		cmt("#### 4. Running PCR program...")
		protocol.set_rail_lights(False)

		tc_mod.close_lid()
		tc_mod.set_lid_temperature(105)
		tc_mod.set_block_temperature(95,hold_time_seconds = 30, block_max_volume = 25)
		profile = [	{'temperature': 95, 'hold_time_seconds': 10},
					{'temperature': melting_temp, 'hold_time_seconds': 30},
					{'temperature': 72, 'hold_time_seconds': 30}]
		tc_mod.execute_profile(	steps = profile, repetitions = number_of_cycles, block_max_volume = 25)
		tc_mod.set_block_temperature(72, hold_time_minutes = 2)
		tc_mod.set_block_temperature(20, hold_time_seconds = 10)
		tc_mod.deactivate_block()
		tc_mod.deactivate_lid()
		tc_mod.open_lid()

		protocol.set_rail_lights(True)
		flash("#### 5. END: Re-stick the sticker, write down the label and save the plate, clean the silicone well and leave the robot spotless")

	# =============================================================================
	# END
	# =============================================================================
