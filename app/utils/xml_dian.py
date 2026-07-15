from __future__ import annotations

from datetime import datetime

from lxml import etree

UBL_NS = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
CAC_NS = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CBC_NS = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
EXT_NS = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"


def buildUBLInvoice(
    numero_documento: str,
    fecha_emision: datetime,
    total: float,
    subtotal: float,
    impuestos: float,
    nit_empresa: str,
    items: list[dict],
) -> str:
    NSMAP = {
        None: UBL_NS,
        "cac": CAC_NS,
        "cbc": CBC_NS,
        "ext": EXT_NS,
    }

    root = etree.Element("Invoice", nsmap=NSMAP)

    ext = etree.SubElement(root, f"{{{EXT_NS}}}UBLExtensions")
    ext_sub = etree.SubElement(ext, f"{{{EXT_NS}}}UBLExtension")

    etree.SubElement(root, f"{{{CBC_NS}}}ID").text = numero_documento
    etree.SubElement(root, f"{{{CBC_NS}}}IssueDate").text = fecha_emision.strftime("%Y-%m-%d")
    etree.SubElement(root, f"{{{CBC_NS}}}IssueTime").text = fecha_emision.strftime("%H:%M:%S")
    etree.SubElement(root, f"{{{CBC_NS}}}InvoiceTypeCode").text = "01"

    supplier = etree.SubElement(root, f"{{{CAC_NS}}}AccountingSupplierParty")
    supplier_id = etree.SubElement(supplier, f"{{{CAC_NS}}}PartyIdentification")
    supplier_id_id = etree.SubElement(supplier_id, f"{{{CBC_NS}}}ID")
    supplier_id_id.set("schemeID", "96")
    supplier_id_id.text = nit_empresa

    customer = etree.SubElement(root, f"{{{CAC_NS}}}AccountingCustomerParty")
    customer_id = etree.SubElement(customer, f"{{{CAC_NS}}}PartyIdentification")
    customer_id_id = etree.SubElement(customer_id, f"{{{CBC_NS}}}ID")
    customer_id_id.set("schemeID", "13")
    customer_id_id.text = "222222222222"

    tax_total = etree.SubElement(root, f"{{{CAC_NS}}}TaxTotal")
    tax_amount = etree.SubElement(tax_total, f"{{{CBC_NS}}}TaxAmount")
    tax_amount.set("currencyID", "COP")
    tax_amount.text = f"{impuestos:.2f}"

    legal_total = etree.SubElement(root, f"{{{CAC_NS}}}LegalMonetaryTotal")
    line_total = etree.SubElement(legal_total, f"{{{CBC_NS}}}LineExtensionAmount")
    line_total.set("currencyID", "COP")
    line_total.text = f"{subtotal:.2f}"
    tax_inclusive = etree.SubElement(legal_total, f"{{{CBC_NS}}}TaxInclusiveAmount")
    tax_inclusive.set("currencyID", "COP")
    tax_inclusive.text = f"{total:.2f}"
    payable = etree.SubElement(legal_total, f"{{{CBC_NS}}}PayableAmount")
    payable.set("currencyID", "COP")
    payable.text = f"{total:.2f}"

    for i, item in enumerate(items, 1):
        invoice_line = etree.SubElement(root, f"{{{CAC_NS}}}InvoiceLine")
        etree.SubElement(invoice_line, f"{{{CBC_NS}}}ID").text = str(i)
        quantity = etree.SubElement(invoice_line, f"{{{CBC_NS}}}InvoicedQuantity")
        quantity.set("unitOfMeasure", "EA")
        quantity.text = str(item.get("cantidad", 1))
        line_ext = etree.SubElement(invoice_line, f"{{{CBC_NS}}}LineExtensionAmount")
        line_ext.set("currencyID", "COP")
        line_ext.text = f"{item.get('subtotal', 0):.2f}"

        item_elem = etree.SubElement(invoice_line, f"{{{CAC_NS}}}Item")
        desc = etree.SubElement(item_elem, f"{{{CBC_NS}}}Description")
        desc.text = item.get("descripcion", "")
        name = etree.SubElement(item_elem, f"{{{CBC_NS}}}Name")
        name.text = item.get("nombre", "")

        price = etree.SubElement(invoice_line, f"{{{CAC_NS}}}Price")
        price_amount = etree.SubElement(price, f"{{{CBC_NS}}}PriceAmount")
        price_amount.set("currencyID", "COP")
        price_amount.text = f"{item.get('precio', 0):.2f}"

    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()
