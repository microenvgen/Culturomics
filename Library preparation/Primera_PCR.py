from opentrons import protocol_api

metadata = {
	'protocolName': 'Primera PCR',
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
		display_name="PCR interna o externa",
		description="Interna: PCR opentrons (nest full-skirt) o Externa: PCR externa (semi-skirt).",
		default="externa",
		choices=[   {"display_name": "interna", "value": "interna"},
					{"display_name": "externa", "value": "externa"},]
	)

	parameters.add_int(
		variable_name="number_of_cycles",
		display_name="Nº de ciclos (interna)",
		description="Número de ciclos. Sólo si es interna. ",
		default=28,
		minimum=1,
		maximum=45
	)

	parameters.add_int(
		variable_name="melting_temp",
		display_name="TM (interna)",
		description="Temperatura de melting. Sólo si es interna",
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
		flash(f">>>>>Revisa los parámetros<<<<<< *PCR {pcr_location}* *{number_of_cycles} ciclos* *{melting_temp}ºC de TM* >>>No olvides anotar esta información en tu cuaderno de laboratorio<<<")
	else:
		flash(f">>>>>Revisa los parámetros<<<<<< *PCR {pcr_location}* >>>Coloca placa semifaldón con el adaptador en la posición 7<<< El nº de ciclos y la TM los tendrás que poner correctamente en el termociclador externo que vayas a usar.>>>No olvides anotar esta información en tu cuaderno de laboratorio<<<.")

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
	if pcr_location == "externa":
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
	cmt("#### 1. Distribuir 20 µL de las columnas 1-2 de reagent a cada pocillo de PCR")
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
	cmt("#### 2. Añadir 5 µl de ADN  template")
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

	if pcr_location == "externa":
		flash("#### 3. Guardar template, poner pegatina a placa PCR y poner en termociclador externo")

	else:
		flash("#### 3. Guardar template y poner pegatina a placa PCR")

		cmt("#### 4. Ejecutando programa de PCR...")
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
		flash("#### 5. FIN: repega la pegatina, anota el label y guarda la placa, limpia la silicona bien y deja el robot impoluto")

	# =============================================================================
	# END
	# =============================================================================
