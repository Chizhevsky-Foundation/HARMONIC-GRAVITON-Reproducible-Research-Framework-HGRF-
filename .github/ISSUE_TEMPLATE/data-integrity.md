name: "Report: Research Integrity / Data Issue"
about: "Report integrity problems with datasets, manifest/hash mismatches, missing provenance, suspected manipulation, or data leak."
title: "[DATA ISSUE] <short summary>"
labels: ["data-integrity","triage"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        **Important**: If you need confidentiality, mark "Request confidentiality" below and do NOT include sensitive data (credentials, private patient info) in this public issue. For urgent security leaks, contact the project admins privately.
  - type: input
    id: summary
    attributes:
      label: "Short summary"
      description: "Short one-line summary of the issue (e.g. 'SHA mismatch for runA.root')."
      required: true
  - type: textarea
    id: description
    attributes:
      label: "Detailed description"
      description: |
        Provide a detailed explanation:
        - What is the dataset / file involved (filename, path, manifest entry)?
        - What did you observe (hash mismatch, missing .sha256, missing manifest metadata, suspicious data patterns)?
        - When and where (URL / repo path / server) did you observe it?
      required: true
  - type: input
    id: manifest
    attributes:
      label: "manifest.json path (optional)"
      description: "If applicable, give the path to manifest.json (e.g. data/raw/manifest.json)."
      required: false
  - type: textarea
    id: evidence
    attributes:
      label: "Evidence & relevant links/commit SHAs"
      description: "Attach or link to .sha256 files, commit SHAs, logs, screenshots or URLs. Do NOT paste large binary content."
      required: false
  - type: dropdown
    id: severity
    attributes:
      label: "Severity"
      options:
        - name: "Low (metadata/manifest missing)"
        - name: "Medium (hash mismatch / missing file)"
        - name: "High (suspected manipulation of dataset)"
        - name: "Critical (data leak / exposure of sensitive data)"
      required: true
  - type: checkboxes
    id: confidentiality
    attributes:
      label: "Confidential handling"
      options:
        - label: "Request confidentiality / private handling"
      required: false
  - type: input
    id: contact
    attributes:
      label: "Your contact (optional)"
      description: "Provide email for follow-up if you are comfortable."
      required: false
  - type: textarea
    id: suggested_action
    attributes:
      label: "Suggested action"
      description: "What action do you propose? (e.g., verify hash, withdraw dataset, notify infra/security)"
      required: false
