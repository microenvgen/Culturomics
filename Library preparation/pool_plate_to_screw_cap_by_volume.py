from opentrons import protocol_api
from opentrons.protocol_api import RuntimeParameterRequiredError

"""
- Usar plantilla en excel para poner los volumenes (pool_plate_to_screw_cap_by_volume.xlsx)
- Exportar como CSV
- Cambiar "," por "." en sublime text o donde 
- Cargar el CSV como parámetro

> En el epp screw cap de 1.5 ml poner 20 ul de NFW para que no pipetee en vació la primera vez
"""



metadata = {
	'protocolName': 'Pool Plate to Screw Cap by volume',
	'author': 'Alberto Rastrojo',
	'description': "balabablabla",
	'apiLevel': '2.20',
	'version': '1'
}

# =============================================================================
# Runtime parameters
# =============================================================================
def add_parameters(parameters):

	parameters.add_csv_file(
		variable_name="csv_file",
		display_name="csv_file",
		description="csv separado por comas"
	)

	parameters.add_str(
		variable_name="input_plate_format",
		display_name="Tipo de placa de entrada",
		description="Tipo de placa de entrada",
		default="nest",
		choices = [	{"display_name": "NEST full-skirt", "value":"nest"},
					{"display_name": "Shapire semi-skirt", "value":"semi"}]
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

	def epp_height(epp_vol):

		height = (0.022669 * epp_vol + 5.226) - 5
		if height < 1:
			height = 1

		return height

	# =============================================================================
	# Input data, variables & parameters
	# =============================================================================
	protocol.set_rail_lights(True)
	input_plate_format = protocol.params.input_plate_format

	# =============================================================================
	# Labware
	# =============================================================================
	# Pipettes
	tips = protocol.load_labware('opentrons_96_filtertiprack_20ul', 9)
	s20 = protocol.load_instrument('p20_single_gen2','left', tip_racks=[tips])

	# Input plate
	if input_plate_format == "nest":
		input_plate = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', 8)
	else:
		input_plate = protocol.load_labware('pcr_plate_semi_skirt', 8)

	# Output tube
	eppendorf_rack = protocol.load_labware('opentrons_24_aluminumblock_nest_1.5ml_screwcap', 11)
	epp = eppendorf_rack["A1"]

	# =============================================================================
	# Protocol
	# =============================================================================
	# =============================================================================
	cmt("#### 1. Reading CSV file")
	# =============================================================================
	if not protocol.is_simulating():
		try:
			# raw_csv_data = [[row1,..], [row2,...]]
			raw_csv_data = protocol.params.csv_file.parse_as_csv(delimiter=";")
		except RuntimeParameterRequiredError as error:
			flash(f"#### NO SE ESTÁ LEYENDO EL FICHERO. ERROR:{error}")

	else: # simulating & test data
		raw_csv_data = [
			['', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'], 
			['A', '-1', '10', '10', '4', '4', '4', '-1', '10', '5', '-1', '-1', '-1'], 
			['B', '-1', '5', '3', '3', '2', '2', '-1', '-1', '-1', '5', '5', '-1'], 
			['C', '-1', '4', '10', '4', '4', '4', '-1', '10', '5', '-1', '-1', '-1'], 
			['D', '-1', '4', '10', '4', '4', '4', '-1', '10', '5', '-1', '-1', '-1'], 
			['E', '-1', '4', '10', '4', '4', '4', '-1', '10', '5', '-1', '-1', '-1'], 
			['F', '-1', '4', '10', '4', '4', '4', '-1', '10', '5', '-1', '-1', '-1'], 
			['G', '-1', '4', '10', '4', '4', '4', '-1', '10', '5', '-1', '-1', '-1'], 
			['H', '-1', '4', '10', '4', '4', '4', '-1', '10', '5', '-1', '-1', '-1'], 
		]

	#--Define wells by row and a dictionary to store volumes
	rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
	columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
	wells = [r+c for r in rows for c in columns]
	volumes = {r+c:0 for r in rows for c in columns}

	#--Parsing CSV data
	total_vol = 0
	for row_data in raw_csv_data[1:9]: #--skip header
		row = row_data[0]
		for col, vol in enumerate(row_data[1:13]): #-- skip first column (row_name)
			if float(vol) != -1 and float(vol) < 2:
				flash("<<<ERROR: hay un volúmen menor de 2 ul>>>")
			elif float(vol) != -1 and float(vol) > 10:
				flash("<<<ERROR: hay un volúmen mayor de 10 ul>>>")
			else:
				well = row + str(col+1)
				volumes[well] = float(vol)
				if float(vol) != -1:
					total_vol += float(vol)

	if total_vol > 1480:
		flash("<<<ERROR: volume excesivo>>>")
	else:
		flash(f"<<<VOLUMEN TOTAL: {total_vol}, ¿Es correcto?>>>")

	# =============================================================================
	cmt("#### 2. Transferring samples to pool.")
	# =============================================================================
	s20.flow_rate.aspirate = 2
	s20.flow_rate.dispense = 2

	epp_vol = 0
	z = epp_height(epp_vol)
	for well in wells:
		vol = volumes[well]

		if vol == -1: continue

		s20.transfer(vol, input_plate.well(well).bottom(z=1), epp.bottom(z=z), new_tip="always")
		epp_vol += vol
		z = epp_height(epp_vol)

	# =============================================================================
	flash("#### END: close tube and vortex. Close input plate properly.")
	# =============================================================================

