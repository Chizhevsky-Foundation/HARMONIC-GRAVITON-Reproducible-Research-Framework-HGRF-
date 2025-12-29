name: "Report: Ethical / Integrity Incident"
about: "Use this template to report ethical concerns, research integrity issues, data breaches or other incidents requiring review by the Ethics Committee. You can request confidentiality."
title: "[ETHICS REPORT] <breve resumen>"
labels: ["ethics","triage"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        **IMPORTANTE**: Si necesitas confidencialidad, marca la casilla "Confidential request" abajo y contactaremos por correo privado. No incluyas información sensible (credenciales, datos personales) en el Issue público si deseas confidencialidad.
  - type: input
    id: summary
    attributes:
      label: "Short summary"
      description: "Una frase que resuma el incidente (ej: 'Uso indebido de dataset X en análisis Y')"
      placeholder: "Breve resumen del incidente"
      required: true
  - type: textarea
    id: description
    attributes:
      label: "Detailed description of the incident"
      description: "Describe hechos, contexto, qué observaste y por qué es preocupante. Indica fechas y horas aproximadas."
      placeholder: |
        - ¿Qué pasó? 
        - ¿Cuándo y dónde (URL / repo / archivo / evento)? 
        - ¿Quiénes estuvieron involucrados (nombres/roles)? 
      required: true
  - type: textarea
    id: evidence
    attributes:
      label: "Evidence & links"
      description: "Proporciona links, captures, commit SHAs, archivos, o nombres de datasets. Si adjuntas ficheros, marca que son confidenciales si aplica."
      placeholder: "URLs, commit SHAs, capturas, nombres de archivos, etc."
      required: false
  - type: dropdown
    id: severity
    attributes:
      label: "Severity (your assessment)"
      description: "Evalúa la gravedad percibida del incidente."
      options:
        - name: "Low (minor concern)"
        - name: "Medium (possible policy breach)"
        - name: "High (serious breach, potential harm)"
        - name: "Critical (immediate risk to safety or legal)"
      required: true
  - type: checkboxes
    id: confidentiality
    attributes:
      label: "Confidential request"
      description: "¿Deseas que la comunicación sea privada (no publicar el contenido completo del issue)?"
      options:
        - label: "Request confidentiality / private handling"
      required: false
  - type: input
    id: contact
    attributes:
      label: "Your contact (optional)"
      description: "Email o teléfono si deseas seguimiento (si pides confidencialidad, proporcionar un contacto facilita la respuesta privada)."
      required: false
  - type: textarea
    id: action_request
    attributes:
      label: "What action are you requesting?"
      description: "Por ejemplo: 'Investigación interna', 'borrar contenido', 'notificar a institución X', 'revisión del análisis'."
      required: false
  - type: textarea
    id: additional
    attributes:
      label: "Additional notes"
      required: false
