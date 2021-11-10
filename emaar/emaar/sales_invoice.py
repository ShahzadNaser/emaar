import frappe
from pyqrcode import create as qr_create
import io
import os


def create_qr_code(doc, method):
	"""Create QR Code after inserting Sales Inv
	"""

	# if QR Code field not present, do nothing
	if not hasattr(doc, 'qr_code'):
		return

	# Don't create QR Code if it already exists
	qr_code = doc.get("qr_code")
	if qr_code and frappe.db.exists({"doctype": "File", "file_url": qr_code}):
		return

	fields = frappe.get_meta('Sales Invoice').fields

	for field in fields:
		if field.fieldname == 'qr_code' and field.fieldtype == 'Attach Image':
			# creating qr code for the Sales Invoice
			xml = """{{url}}""".format(url=frappe.utils.get_url_to_form("Sales Invoice", doc.name))
			qr_image = io.BytesIO()
			xml = qr_create(xml, error='L')
			xml.png(qr_image, scale=4, quiet_zone=1)

			# making file
			filename = f"QR-CODE-{doc.name}.png".replace(os.path.sep, "__")
			_file = frappe.get_doc({
				"doctype": "File",
				"file_name": filename,
				"content": qr_image.getvalue(),
				"is_private": 1
			})

			_file.save()

			# assigning to document
			doc.db_set('qr_code', _file.file_url)
			doc.notify_update()

			break

def delete_qr_code_file(doc, method):
	"""Delete QR Code on deleted sales invoice"""

	if hasattr(doc, 'qr_code'):
		if doc.get('qr_code'):
			file_doc = frappe.get_list('File', {
				'file_url': doc.qr_code,
				'attached_to_doctype': doc.doctype,
				'attached_to_name': doc.name
			})
			if len(file_doc):
				frappe.delete_doc('File', file_doc[0].name)
    
    