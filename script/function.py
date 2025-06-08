# Import Library

from typing import Any, Dict
import json
from datetime import datetime, timezone, timedelta
import os
from google.oauth2 import service_account
from google.auth.transport import requests
import google.auth

def create_patient(
    family_name: str ,
    given_name: str ,
    gender: str ,
    birth_date: str ,
    mrn: str,
    healthcare_client: str,
    fhir_store_name: str,
) -> Dict[str, Any]:
    patient_body = {
        "name": [{"use": "official", "family": f"{family_name}", "given": [f"{given_name}"]}],
        "gender": f"{gender}",
        "birthDate": f"{birth_date}",
        "identifier": [
            {
                "use": "usual",
                # This 'type' coding explicitly identifies this as an MRN.
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR",
                            "display": "Medical Record Number",
                        }
                    ]
                },
                # The 'system' is a unique URI for the assigning authority (e.g., a hospital).
                # This should be changed to a real URI for your organization.
                "system": "urn:oid:1.2.36.146.595.217.0.1",
                "value": mrn,
            }
        ],
        "resourceType": "Patient",
    }

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .create(parent=fhir_store_name, type="Patient", body=patient_body)
    )
    # Sets required application/fhir+json header on the googleapiclient.http.HttpRequest.
    request.headers["content-type"] = "application/fhir+json;charset=utf-8"
    response = request.execute()

    print(f"Created Patient resource with ID {response['id']}")
    return response

# Imports the types Dict and Any for runtime type hints.
def create_encounter(
    patient_id: str,
    encounter_status: str,
    encounter_text: str,
    healthcare_client: str,
    fhir_store_name: str,
) -> Dict[str, Any]:
    encounter_body = {
        "status": encounter_status,
        "class": {
            "system": "http://hl7.org/fhir/v3/ActCode",
            "code": "IMP",
            "display": "inpatient encounter",
        },
        "reasonCode": [
            {
                "text": (
                    encounter_text
                )
            }
        ],
        "subject": {"reference": f"Patient/{patient_id}"},
        "resourceType": "Encounter",
    }

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .create(parent=fhir_store_name, type="Encounter", body=encounter_body)
    )
    # Sets required application/fhir+json header on the googleapiclient.http.HttpRequest.
    request.headers["content-type"] = "application/fhir+json;charset=utf-8"
    response = request.execute()
    print(f"Created Encounter resource with ID {response['id']}")

    return response

def create_condition(
    patient_id: str,
    clinical_status: str,
    verification_status: str,
    snomed_code: str,
    condition_display: str,
    onset_datetime: str,
    healthcare_client: str,
    fhir_store_name: str,
) -> Dict[str, Any]:
    # The body of the FHIR Condition resource to be created.
    condition_body = {
        "resourceType": "Condition",
        "subject": {"reference": f"Patient/{patient_id}"},
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                    "display": clinical_status,
                }
            ]
        },
        "verificationStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": "confirmed",
                    "display": verification_status,
                }
            ]
        },
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": snomed_code,
                    "display": condition_display,
                }
            ],
            "text": condition_display,
        },
        "onsetDateTime": onset_datetime,
    }

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .create(parent=fhir_store_name, type="Condition", body=condition_body)
    )
    # Sets required application/fhir+json header on the googleapiclient.http.HttpRequest.
    request.headers["content-type"] = "application/fhir+json;charset=utf-8"
    response = request.execute()
    print(f"Created Condition resource with ID {response['id']}")

    return response

def create_procedure(
    patient_id: str,
    encounter_id: str,
    procedure_status: str,
    snomed_code: str,
    procedure_display: str,
    start_time: str,
    end_time: str,
    reason_text: str,
    healthcare_client: str,
    fhir_store_name: str,
) -> Dict[str, Any]:
    """Creates a new Procedure resource in a FHIR store.

    This new Procedure will be linked to an existing Patient and Encounter resource.

    Args:
        patient_id: The "logical id" of the referenced Patient resource.
        encounter_id: The "logical id" of the referenced Encounter resource during which the procedure was performed.
        procedure_status: The status of the procedure (e.g., 'completed').
        snomed_code: The SNOMED CT code for the procedure.
        procedure_display: The human-readable name of the procedure.
        start_time: The start time of the procedure (ISO 8601 format).
        end_time: The end time of the procedure (ISO 8601 format).
        reason_text: The text description for the reason for the procedure.

    Returns:
        A dict representing the created Procedure resource.
    """

    # The body of the FHIR Procedure resource to be created.
    procedure_body = {
        "resourceType": "Procedure",
        "status": procedure_status,
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": snomed_code,
                    "display": procedure_display,
                }
            ],
            "text": procedure_display,
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "encounter": {"reference": f"Encounter/{encounter_id}"},
        "performedPeriod": {
            "start": start_time,
            "end": end_time,
        },
        "reasonCode": [{"text": reason_text}],
    }

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .create(parent=fhir_store_name, type="Procedure", body=procedure_body)
    )
    # Sets required application/fhir+json header on the googleapiclient.http.HttpRequest.
    request.headers["content-type"] = "application/fhir+json;charset=utf-8"
    response = request.execute()
    print(f"Created Procedure resource with ID {response['id']}")

    return response

def create_practitioner(
    npi: str,
    family_name: str,
    given_name: str,
    healthcare_client: str,
    fhir_store_name: str,
) -> Dict[str, Any]:
    practitioner_body = {
        "resourceType": "Practitioner",
        "identifier": [
            {
                "system": "http://hl7.org/fhir/sid/us-npi",
                "value": npi,
            }
        ],
        "name": [{"family": family_name, "given": [given_name], "prefix": ["Dr."]}],
    }

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .create(parent=fhir_store_name, type="Practitioner", body=practitioner_body)
    )
    request.headers["content-type"] = "application/fhir+json;charset=utf-8"
    response = request.execute()
    print(f"Created Practitioner resource with ID {response['id']}")

    return response

def create_medication_request(
    patient_id: str,
    practitioner_id: str,
    medication_status: str,
    medication_intent: str,
    rxnorm_code: str,
    medication_display: str,
    practitioner_display: str,
    dosage_text: str,
    healthcare_client: str,
    fhir_store_name: str,
) -> Dict[str, Any]:
    current_time = datetime.now(timezone.utc).isoformat()

    # A more robust body for the FHIR MedicationRequest resource.
    medication_request_body = {
        "resourceType": "MedicationRequest",
        "status": medication_status,
        "intent": medication_intent,
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": rxnorm_code,
                    "display": medication_display,
                }
            ],
            "text": medication_display,
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "authoredOn": current_time,
        "requester": {
            "reference": f"Practitioner/{practitioner_id}",
            "display": practitioner_display,
        },
        "dosageInstruction": [
            {
                # Using just the "text" field is simpler and less error-prone.
                "text": dosage_text
            }
        ],
    }

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .create(
            parent=fhir_store_name,
            type="MedicationRequest",
            body=medication_request_body,
        )
    )
    request.headers["content-type"] = "application/fhir+json;charset=utf-8"


    response = request.execute()
    print(f"Created MedicationRequest resource with ID {response['id']}")
    return response

def create_diagnostic_report(
    report_status: str,
    loinc_code: str,
    report_display: str,
    conclusion: str,
    healthcare_client: str,
    fhir_store_name: str,
    patient_id: str,
    encounter_id: str,
    practitioner_id: str
) -> Dict[str, Any]:
    current_time = datetime.now(timezone.utc).isoformat()

    # The body for the FHIR DiagnosticReport resource.
    diagnostic_report_body = {
        "resourceType": "DiagnosticReport",
        "status": report_status,
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": loinc_code,
                    "display": report_display,
                }
            ],
            "text": report_display,
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "encounter": {"reference": f"Encounter/{encounter_id}"},
        # effectiveDateTime is when the sample was collected or the testing occurred.
        "effectiveDateTime": current_time,
        # issued is when the report was officially released.
        "issued": current_time,
        "performer": [{"reference": f"Practitioner/{practitioner_id}"}],
        "conclusion": conclusion,
    }

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .create(
            parent=fhir_store_name,
            type="DiagnosticReport",
            body=diagnostic_report_body,
        )
    )
    request.headers["content-type"] = "application/fhir+json;charset=utf-8"

    response = request.execute()
    print(f"Created DiagnosticReport resource with ID {response['id']}")
    return response

def create_observation(
    patient_id: str,
    encounter_id: str,
    observation_status: str,
    loinc_code: str,
    observation_display: str,
    observation_value: float,
    observation_unit: str,
    healthcare_client: str,
    fhir_store_name: str,
    current_time: str
) -> Dict[str, Any]:
    observation_body = {
        "resourceType": "Observation",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": loinc_code,
                    "display": observation_display,
                }
            ]
        },
        "status": observation_status,
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": current_time,
        "valueQuantity": {"value": observation_value, "unit": observation_unit},
        "encounter": {"reference": f"Encounter/{encounter_id}"},
    }

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .create(
            parent=fhir_store_name,
            type="Observation",
            body=observation_body,
        )
    )
    # Sets required application/fhir+json header on the googleapiclient.http.HttpRequest.
    request.headers["content-type"] = "application/fhir+json;charset=utf-8"
    response = request.execute()
    print(f"Created Observation resource with ID {response['id']}")

    return response

## Updating a FHIR resource

def update_resource(
    project_id: str,
    location: str,
    dataset_id: str,
    fhir_store_id: str,
    resource_type: str,
    resource_id: str,
    fhir_store_parent: str,
    healthcare_client: str,
) -> Dict[str, Any]:
    fhir_resource_path = f"{fhir_store_parent}/fhirStores/{fhir_store_id}/fhir/{resource_type}/{resource_id}"

    patient_body = {
        "resourceType": resource_type,
        "active": True,
        "id": resource_id,
    }

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .update(name=fhir_resource_path, body=patient_body)
    )
    # Sets required application/fhir+json header on the googleapiclient.http.HttpRequest.
    request.headers["content-type"] = "application/fhir+json;charset=utf-8"
    response = request.execute()

    print(
        f"Updated {resource_type} resource with ID {resource_id}:\n"
        f" {json.dumps(response, indent=2)}"
    )

    return response

## Patching a resource

def patch_resource(
    fhir_store_id: str,
    resource_type: str,
    resource_id: str,
    fhir_store_parent: str,
    healthcare_client: str
) -> Dict[str, Any]:
    fhir_resource_path = f"{fhir_store_parent}/fhirStores/{fhir_store_id}/fhir/{resource_type}/{resource_id}"

    patient_body = [{"op": "replace", "path": "/active", "value": False}]

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .patch(name=fhir_resource_path, body=patient_body)
    )

    # Sets required application/json-patch+json header.
    # See https://tools.ietf.org/html/rfc6902 for more information.
    request.headers["content-type"] = "application/json-patch+json"

    response = request.execute()

    print(
        f"Patched {resource_type} resource with ID {resource_id}:\n"
        f" {json.dumps(response, indent=2)}"
    )

    return response

## Getting a FHIR resource

def get_resource(
    fhir_store_id: str,
    resource_type: str,
    resource_id: str,
    fhir_store_parent: str,
    healthcare_client: str
) -> Dict[str, Any]:
    fhir_resource_path = f"{fhir_store_parent}/fhirStores/{fhir_store_id}/fhir/{resource_type}/{resource_id}"

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .read(name=fhir_resource_path)
    )
    response = request.execute()
    print(
        f"Got contents of {resource_type} resource with ID {resource_id}:\n",
        json.dumps(response, indent=2),
    )

    return response

def search_patient_by_mrn(
    project_id: str,
    location: str,
    dataset_id: str,
    fhir_store_id: str,
    mrn: str,
) -> Dict[str, Any]:
    """
    Searches for a Patient resource using their Medical Record Number (MRN).

    Args:
        project_id: The ID of the Google Cloud project.
        location: The Cloud location of the dataset.
        dataset_id: The ID of the dataset.
        fhir_store_id: The ID of the FHIR store.
        mrn: The Medical Record Number to search for.

    Returns:
        A dict representing the FHIR search bundle.
    """
    import google.auth
    
    # Gets credentials from the environment.
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    # Creates a requests Session object with the credentials.
    authed_session = requests.AuthorizedSession(credentials)

    base_url = "https://healthcare.googleapis.com/v1"
    fhir_store_path = (
        f"{base_url}/projects/{project_id}/locations/{location}"
        f"/datasets/{dataset_id}/fhirStores/{fhir_store_id}"
    )

    # The identifier system for MRN must match the one used when creating the patient.
    # From create_patient, we know the system is "urn:oid:1.2.36.146.595.217.0.1"
    identifier_system = "urn:oid:1.2.36.146.595.217.0.1"
    
    # Construct the search query URL
    # The format is ?identifier=SYSTEM|VALUE
    search_url = f"{fhir_store_path}/fhir/Patient?identifier={identifier_system}|{mrn}"

    headers = {"Content-Type": "application/fhir+json;charset=utf-8"}
    
    print(f"Searching for Patient with MRN at URL: {search_url}")
    response = authed_session.get(search_url, headers=headers)
    response.raise_for_status()

    return response.json()

## Getting all patient compartment resources

def get_patient_everything_by_mrn(
    project_id: str,
    location: str,
    dataset_id: str,
    fhir_store_id: str,
    mrn: str,
) -> Dict[str, Any]:
    """
    Finds a patient by MRN and then retrieves all resources in their compartment
    using the $everything operation.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The Cloud location of the dataset.
        dataset_id: The ID of the dataset.
        fhir_store_id: The ID of the FHIR store.
        mrn: The Medical Record Number to search for.

    Returns:
        A dict representing the FHIR $everything bundle.

    Raises:
        Exception: If no patient is found for the given MRN.
    """
    # STEP 1: Find the patient by MRN to get their internal FHIR ID.
    print(f"Searching for patient with MRN: {mrn}")
    patient_search_bundle = search_patient_by_mrn(
        project_id, location, dataset_id, fhir_store_id, mrn
    )

    if (
        "entry" not in patient_search_bundle
        or not patient_search_bundle["entry"]
        or "resource" not in patient_search_bundle["entry"][0]
    ):
        raise Exception(f"No patient found with MRN: {mrn}")

    # Extract the internal FHIR ID from the search result
    patient_resource = patient_search_bundle["entry"][0]["resource"]
    patient_id = patient_resource.get("id")
    if not patient_id:
        raise Exception("Could not find patient ID in the search result.")
    
    print(f"Found patient with internal FHIR ID: {patient_id}")

    # STEP 2: Use the internal ID to get everything for that patient.
    print(f"Fetching all records for patient ID: {patient_id}")
    # Note: We are now calling the existing get_patient_everything function
    everything_bundle = get_patient_everything(
        project_id, location, dataset_id, fhir_store_id, patient_id
    )

    return everything_bundle

def get_patient_everything(
    project_id,
    location,
    dataset_id,
    fhir_store_id,
    resource_id,
):  
    # Gets credentials from the environment.
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    # Creates a requests Session object with the credentials.
    authed_session = requests.AuthorizedSession(credentials)

    # URL to the Cloud Healthcare API endpoint and version
    base_url = "https://healthcare.googleapis.com/v1"

    url = f"{base_url}/projects/{project_id}/locations/{location}"

    resource_path = "{}/datasets/{}/fhirStores/{}/fhir/{}/{}".format(
        url, dataset_id, fhir_store_id, "Patient", resource_id
    )
    resource_path += "/$everything"

    # Sets required application/fhir+json header on the request
    headers = {"Content-Type": "application/fhir+json;charset=utf-8"}

    response = authed_session.get(resource_path, headers=headers)
    response.raise_for_status()

    resource = response.json()

    print(json.dumps(resource, indent=2))

    return resource

## Deleting a FHIR resource

def delete_resource(
    fhir_store_id: str,
    resource_type: str,
    resource_id: str,
    fhir_store_parent: str,
    healthcare_client: str,   
) -> dict:
    fhir_resource_path = f"{fhir_store_parent}/fhirStores/{fhir_store_id}/fhir/{resource_type}/{resource_id}"

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .delete(name=fhir_resource_path)
    )
    response = request.execute()
    print(f"Deleted {resource_type} resource with ID {resource_id}.")

    return response

def delete_resource_purge(
    fhir_store_id: str,
    resource_type: str,
    resource_id: str,
    fhir_store_parent: str,
    healthcare_client: str
) -> dict:
    fhir_resource_path = f"{fhir_store_parent}/fhirStores/{fhir_store_id}/fhir/{resource_type}/{resource_id}"

    request = (
        healthcare_client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .fhir()
        .Resource_purge(name=fhir_resource_path)
    )
    response = request.execute()
    print(
        f"Deleted all versions of {resource_type} resource with ID"
        f" {resource_id} (excluding current version)."
    )
    return response