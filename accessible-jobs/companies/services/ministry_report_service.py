# companies/services/ministry_report_service.py
"""
Servicio para generar y enviar informes de contratación al Ministerio de Trabajo
"""
import os
import hashlib
from datetime import datetime
from io import BytesIO
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_and_send_report(report):
    """
    Genera PDF/XML, firma digitalmente y envía al Ministerio
    
    Args:
        report: Instancia de HiringReport
        
    Returns:
        dict: {'success': bool, 'receipt_number': str, 'error': str}
    """
    try:
        # 1. Generar PDF
        pdf_content = generate_pdf_report(report)
        
        # 2. Generar XML
        xml_content = generate_xml_report(report)
        
        # 3. Guardar archivos
        pdf_filename = f"informe_{report.contract_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        xml_filename = f"informe_{report.contract_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        
        report.pdf_file.save(pdf_filename, ContentFile(pdf_content), save=False)
        report.xml_file.save(xml_filename, ContentFile(xml_content.encode('utf-8')), save=False)
        
        # 4. Generar firma digital
        report.generate_signature()
        
        # 5. Simular envío al Ministerio
        result = send_to_ministry_api(report)
        
        if result['success']:
            report.mark_as_confirmed(
                receipt_number=result['receipt_number'],
                response_data=result.get('response_data', {})
            )
            return {
                'success': True,
                'receipt_number': result['receipt_number'],
                'message': 'Informe enviado y confirmado exitosamente'
            }
        else:
            # Manejar fallos
            if report.can_retry():
                report.increment_retry()
                return {
                    'success': False,
                    'error': f"Fallo en el envío. Intento {report.retry_count} de 3. Se reintentará automáticamente.",
                    'retry': True
                }
            else:
                report.mark_as_failed(result.get('error', 'Error desconocido'))
                return {
                    'success': False,
                    'error': 'Se agotaron los intentos de envío. Contacte al administrador.',
                    'retry': False
                }
    
    except Exception as e:
        report.mark_as_failed(str(e))
        return {
            'success': False,
            'error': f'Error al procesar el informe: {str(e)}'
        }


def generate_pdf_report(report):
    """
    Genera el PDF profesional del informe usando ReportLab
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Encabezado
    elements.append(Paragraph("REPÚBLICA DE COLOMBIA", title_style))
    elements.append(Paragraph("MINISTERIO DE TRABAJO", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    elements.append(Paragraph("INFORME DE CONTRATACIÓN", heading_style))
    elements.append(Paragraph("Ley 2466 de 2025 - Inclusión Laboral de Personas con Discapacidad", normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del informe
    info_data = [
        ['Número de Radicado:', report.ministry_receipt_number or 'Pendiente de asignación'],
        ['Fecha de Generación:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
        ['Estado:', report.get_status_display()],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Sección 1: Información de la Empresa
    elements.append(Paragraph("1. INFORMACIÓN DE LA EMPRESA", heading_style))
    
    company_data = [
        ['Razón Social:', report.company_name],
        ['NIT:', report.company_nit],
        ['Representante Legal:', report.company.get_full_name()],
        ['Correo Electrónico:', report.company.email],
    ]
    
    company_table = Table(company_data, colWidths=[2*inch, 4*inch])
    company_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Sección 2: Información del Contrato
    elements.append(Paragraph("2. INFORMACIÓN DEL CONTRATO", heading_style))
    
    contract_data = [
        ['Número de Contrato:', report.contract_number],
        ['Fecha de Contrato:', report.contract_date.strftime('%d/%m/%Y')],
        ['Cargo:', report.position_title],
        ['Oferta Relacionada:', report.job.title if report.job else 'No especificada'],
    ]
    
    contract_table = Table(contract_data, colWidths=[2*inch, 4*inch])
    contract_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(contract_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Sección 3: Información de Discapacidad (Codificada)
    elements.append(Paragraph("3. INFORMACIÓN DE DISCAPACIDAD (CODIFICADA)", heading_style))
    
    elements.append(Paragraph(
        "<i>Nota: La información de discapacidad ha sido codificada para proteger "
        "la privacidad del empleado según la Ley 1581 de 2012 (Protección de Datos Personales).</i>",
        ParagraphStyle('Italic', parent=normal_style, fontSize=8, textColor=colors.grey)
    ))
    elements.append(Spacer(1, 0.1*inch))
    
    disability_data = [
        ['Tipo de Discapacidad (Codificado):', report.get_disability_type_display()],
        ['Código de Tipo:', report.disability_type],
        ['Porcentaje de Discapacidad:', f"{report.disability_percentage}%" if report.disability_percentage else 'No especificado'],
    ]
    
    disability_table = Table(disability_data, colWidths=[2.5*inch, 3.5*inch])
    disability_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff9e6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(disability_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Notas adicionales
    if report.notes:
        elements.append(Paragraph("4. NOTAS ADICIONALES", heading_style))
        elements.append(Paragraph(report.notes, normal_style))
        elements.append(Spacer(1, 0.2*inch))
    
    # Firma Digital
    elements.append(Paragraph("CERTIFICACIÓN DIGITAL", heading_style))
    
    signature_data = [
        ['Algoritmo:', 'SHA-256'],
        ['Firma Digital:', report.digital_signature[:64] + '...'],
        ['Fecha de Firma:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
    ]
    
    signature_table = Table(signature_data, colWidths=[1.5*inch, 4.5*inch])
    signature_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f8e8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(signature_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Pie de página
    footer_style = ParagraphStyle(
        'Footer',
        parent=normal_style,
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        "Este documento ha sido generado electrónicamente y cuenta con firma digital.",
        footer_style
    ))
    elements.append(Paragraph(
        f"Ministerio de Trabajo - República de Colombia | Carrera 14 No. 99-33 Bogotá D.C. | www.mintrabajo.gov.co",
        footer_style
    ))
    
    # Construir PDF
    doc.build(elements)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def generate_xml_report(report):
    """
    Genera el XML estandarizado del informe
    """
    xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<InformeContratacion xmlns="http://www.mintrabajo.gov.co/schemas/contratacion" version="1.0">
    <Metadatos>
        <FechaGeneracion>{datetime.now().isoformat()}</FechaGeneracion>
        <Version>1.0</Version>
        <TipoDocumento>INFORME_CONTRATACION_DISCAPACIDAD</TipoDocumento>
    </Metadatos>
    
    <Empresa>
        <RazonSocial><![CDATA[{report.company_name}]]></RazonSocial>
        <NIT>{report.company_nit}</NIT>
        <RepresentanteLegal><![CDATA[{report.company.get_full_name()}]]></RepresentanteLegal>
        <CorreoElectronico>{report.company.email}</CorreoElectronico>
    </Empresa>
    
    <Contrato>
        <NumeroContrato>{report.contract_number}</NumeroContrato>
        <FechaContrato>{report.contract_date}</FechaContrato>
        <CargoEmpleado><![CDATA[{report.position_title}]]></CargoEmpleado>
        <OfertaRelacionada>{report.job.id if report.job else 'N/A'}</OfertaRelacionada>
    </Contrato>
    
    <Discapacidad>
        <TipoCodificado>{report.disability_type}</TipoCodificado>
        <DescripcionTipo><![CDATA[{report.get_disability_type_display()}]]></DescripcionTipo>
        <Porcentaje>{report.disability_percentage or 'N/A'}</Porcentaje>
    </Discapacidad>
    
    <Seguridad>
        <FirmaDigital>{report.digital_signature}</FirmaDigital>
        <Algoritmo>SHA-256</Algoritmo>
        <FechaFirma>{datetime.now().isoformat()}</FechaFirma>
    </Seguridad>
    
    <NotasAdicionales>
        <![CDATA[{report.notes or 'Sin notas adicionales'}]]>
    </NotasAdicionales>
</InformeContratacion>
"""
    
    return xml_template


def send_to_ministry_api(report):
    """
    Simula el envío al API del Ministerio
    En producción, esto haría una petición HTTPS real
    
    Returns:
        dict: {'success': bool, 'receipt_number': str, 'response_data': dict}
    """
    import random
    import time
    
    # Simular latencia de red
    time.sleep(1)
    
    # Simular probabilidad de éxito (95% exitoso, 5% falla)
    success = random.random() > 0.05
    
    if success:
        # Generar número de recibo único
        receipt_number = f"MIN-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
        
        return {
            'success': True,
            'receipt_number': receipt_number,
            'response_data': {
                'status': 'received',
                'timestamp': datetime.now().isoformat(),
                'ministry_id': receipt_number,
                'validation_code': hashlib.sha256(receipt_number.encode()).hexdigest()[:16],
                'message': 'Informe recibido correctamente por el Ministerio de Trabajo'
            }
        }
    else:
        return {
            'success': False,
            'error': 'Error de conexión con el servidor del Ministerio. Intente nuevamente.'
        }


def retry_failed_reports():
    """
    Función para reintentar informes fallidos (puede ejecutarse como tarea programada)
    """
    from companies.models import HiringReport, HiringReportStatus
    
    failed_reports = HiringReport.objects.filter(
        status__in=[HiringReportStatus.FAILED, HiringReportStatus.RETRY]
    ).filter(retry_count__lt=3)
    
    results = []
    for report in failed_reports:
        if report.can_retry():
            result = generate_and_send_report(report)
            results.append({
                'report_id': report.id,
                'contract_number': report.contract_number,
                'result': result
            })
    
    return results