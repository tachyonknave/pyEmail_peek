import poplib
import yaml


# Convert Byte array to a Python String
def convert_to_string(input_bytes):
	return input_bytes.decode('UTF-8')


def load_pymail_config():

	server_password = ""

	with open('email_peek.yml', 'r') as config_file:
		pymail_config = yaml.load(config_file)

	with open('email_password', 'r') as password_file:
		server_password = password_file.readline().rstrip()

	pymail_config['server_info']['password'] = server_password

	return pymail_config


def process_response(pop_response_bytes):

	pop_response = convert_to_string(pop_response_bytes)

	if pop_response[:3] == "+OK":
		print("INFO:  ", pop_response[3:])
		return True
	elif pop_response[:4] == "-ERR":
		print("ERROR: ", pop_response[4:])

	return False


def get_header_field(header_bytes):
	if len(header_bytes) == 0:
		return ""

	header_string = convert_to_string(header_bytes)

	if header_string[0] == '\t':
		return ""

	try:
		colon = header_string.index(":")
		field_name = header_string[:colon]
		return field_name
	except ValueError:
		return ""


def extract_address(field_value):

	try:
		open_bracket = field_value.index("<")
		close_bracket = field_value.index(">")
		return field_value[open_bracket+1:close_bracket]

	except ValueError:
		return field_value


def process_header(header_list):

	subject_filed = ""
	from_field = ""
	to_field = ""
	date_field = ""

	for hb in header_list:
		field = get_header_field(hb)
		if field == "Subject":
			subject_filed = convert_to_string(hb)
		elif field == "To":
			to_field = convert_to_string(hb)
		elif field == "From":
			from_field = convert_to_string(hb)
		elif field == "Date":
			date_field = convert_to_string(hb)

	print("\t", to_field, " - ", extract_address(to_field))
	print("\t", from_field, " - ", extract_address(from_field))
	print("\t", subject_filed)
	print("\t", date_field)


def peek_message(mserver, message_index):
	print("----")
	process_header(mserver.top(message_index, 0)[1])


###############################################################################


config = load_pymail_config()

server_config = config['server_info']

serverName = server_config['server']

if server_config['SSL_enabled']:
	M = poplib.POP3_SSL(serverName)
else:
	M = poplib.POP3(serverName)

M.user(server_config['username'])
M.pass_(server_config['password'])

process_response(M.getwelcome())

# ---

messageList = M.list()
process_response(messageList[0])

numMessages = len(messageList[1])
print("INFO:    Number of Messages: ", numMessages)

for msg_index in range(1, numMessages + 1):
	peek_message(M, msg_index)

M.quit()
