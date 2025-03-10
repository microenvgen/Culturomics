from opentrons import protocol_api

metadata = {
	'protocolName': 'Segunda PCR',
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
		default="interna",
		choices=[	{"display_name": "interna", "value": "interna"},
					{"display_name": "externa", "value": "externa"},]
	)

	parameters.add_str(
		variable_name="dilution",
		display_name="Dilución",
		description="Aplicar dilución 1/10",
		default="no",
		choices = [	{"display_name": "No", "value": "no"},
					{"display_name": "Sí", "value": "yes"}]
	)

	parameters.add_str(
		variable_name="input_plate_format",
		display_name="Tipo de placa de entrada",
		description="Tipo de placa de entrada",
		default="nest",
		choices = [	{"display_name": "NEST full-skirt", "value":"nest"},
					{"display_name": "Shapire semi-skirt", "value":"semi"}]
	)

	parameters.add_int(
		variable_name="number_of_cycles",
		display_name="Nº de ciclos (interna)",
		description="Número de ciclos. Sólo si es interna. ",
		default=10,
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
	dilution = protocol.params.dilution
	input_plate_format = protocol.params.input_plate_format


	if pcr_location == "interna":
		flash(f">>>>>Revisa los parámetros<<<<<< *PCR {pcr_location}* *Dilución 1/10: {dilution}* *{number_of_cycles} ciclos* *{melting_temp}ºC de TM* >>>No olvides anotar esta información en tu cuaderno de laboratorio<<<")
	else:
		flash(f">>>>>Revisa los parámetros<<<<<< *PCR {pcr_location}* *Dilución 1/10: {dilution}* >>>Coloca placa semifaldón con el adaptador en la posición 7<<< El nº de ciclos y la TM los tendrás que poner correctamente en el termociclador externo que vayas a usar.>>>No olvides anotar esta información en tu cuaderno de laboratorio<<<.")

	if dilution == "yes":
		flash(f"No olvides añadir 150 µl de H20 buena (NFW) en las columnas 5 y 6 de la placa de reactivos. ")

	# =============================================================================
	# Labware
	# =============================================================================
	# Pipettes
	m20_tipracks = [protocol.load_labware('opentrons_96_filtertiprack_20ul', slot) for slot in [1, 2, 9]]
	m20 = protocol.load_instrument('p20_multi_gen2', 'right', tip_racks=m20_tipracks)

	# input DNA (template)
	if input_plate_format == "nest":
		template = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', 4)
	else:
		template = protocol.load_labware('pcr_plate_semi_skirt', 4)

	# dilution?
	if dilution == "yes":
		template_dil = protocol.load_labware('pcr_plate_semi_skirt', 5)

	# Reagent
	reagents = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', 3)

	# Barcodes
	barcodes = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', 6)

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
	if dilution == "yes":

		# =============================================================================
		cmt("#### Dilución 1: Añadir 18 ul de agua de columnas 5-6 de reagents a cada pocillo de templete_dil sin cambiar puntas")
		# =============================================================================
		m20.pick_up_tip()
		m20.distribute(18,
					source = reagents.columns()[4],
					dest = template_dil.columns()[0:6],
					new_tip = "never",
					disposal_volume = 0,
					trash = False)
		m20.distribute(18,
					source = reagents.columns()[5],
					dest = template_dil.columns()[6:12],
					new_tip = "never",
					disposal_volume = 0,
					trash = False)

	# =============================================================================
	cmt("#### 1. Distribuir 20 µL de las columnas 1-2 de reagent a cada pocillo de PCR")
	# =============================================================================
	if dilution == "no":
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
	cmt("#### 2. Añadir 3 µl de template o template_dil")
	# =============================================================================
	if dilution == "yes":
		# =============================================================================
		cmt("#### Dilución 2: Añadir 2 ul de la placa template a la placa template_dil y mezclar 3 veces 10 µl.")
		# =============================================================================
		for i in range(12):
			m20.pick_up_tip()
			m20.transfer(2, template.columns()[i], template_dil.columns()[i], mix_after=(3, 10), new_tip="never")
			m20.transfer(3, template_dil.columns()[i], PCR.columns()[i], mix_after=(3, 10), new_tip="never")
			m20.drop_tip()

	else:
		m20.transfer(3,
					source = template.wells(),
					dest = PCR.wells(),
					new_tip = "always",
					trash = True,
					mix_after = (3, 20))

	# =============================================================================
	cmt("#### 3. Añadir 2 µl de barcodes y mezclamos 3 veces 10 µl")
	# =============================================================================
	m20.transfer(2,
				source = barcodes.wells(),
				dest = PCR.wells(),
				new_tip = "always",
				trash = True,
				mix_after = (3, 10))

	# =============================================================================
	# Correr PCR o avisar del final
	# =============================================================================

	if pcr_location == "externa":
		flash("#### 3. Guardar template/s, poner pegatina a placa PCR, tiras placa de barcodes cerrada y poner en termociclador externo")

	else:
		flash("#### 3. Guardar template/s, poner pegatina a placa PCR y tiras placa de barcodes cerrada.")

		cmt("#### 4. Ejecutando programa de PCR...")
		protocol.set_rail_lights(False)

		tc_mod.close_lid()
		tc_mod.set_lid_temperature(105)
		tc_mod.set_block_temperature(95, hold_time_seconds = 30, block_max_volume = 25)
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
