# Import Library

from googleapiclient import discovery
from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from script.function import *
import logging
from logging.handlers import RotatingFileHandler

# Variables
project_id = 'eikon-dev-ai-team'
location = 'asia-southeast2'
dataset_id = 'patient-dataset-demo'
fhir_store_id = 'fhir-patient-datastore'
version = 'R4'

fhir_store_parent = (
    f"projects/{project_id}/locations/{location}/datasets/{dataset_id}"
)
fhir_store_name = f"{fhir_store_parent}/fhirStores/{fhir_store_id}"

api_version = "v1"
service_name = "healthcare"
healthcare_client = discovery.build(service_name, api_version)


gmt7_timezone = timezone(timedelta(hours=7))
current_time = datetime.now(gmt7_timezone).isoformat()

app = Flask(__name__)
CORS(app)

# --- Logging Configuration ---
# This block should be placed after `app = Flask(__name__)` and before your routes.
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Set up a file handler that rotates logs, keeping 5 backup files of 5MB each.
file_handler = RotatingFileHandler('app.log', maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Also log to the console (useful for development).
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Add handlers to the Flask app's logger
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO) # Set the base level for the app logger

# This removes the default Flask handler to avoid duplicate logs in the console.
app.logger.removeHandler(app.logger.handlers[0])

app.logger.info("Flask application starting up...")

@app.route('/')
def index():
    app.logger.info("Serving the 'Create Resource' page (index.html).")
    return render_template('index.html')

@app.route('/find')
def find_page():
    app.logger.info("Serving the 'Find Resource' page (find.html).")
    return render_template('find.html')

# --- API Endpoints ---

@app.route('/api/patient', methods=['POST'])
def api_create_patient():
    data = request.get_json()
    app.logger.info(f"Received request to create patient with MRN: {data.get('mrn')}")
    try:
        response = create_patient(
            family_name=data['family_name'],
            given_name=data['given_name'],
            gender=data['gender'],
            birth_date=data['birth_date'],
            mrn=data['mrn'],
            healthcare_client=healthcare_client,
            fhir_store_name=fhir_store_name
        )
        app.logger.info(f"Successfully created Patient. New resource ID: {response.get('id')}")
        return jsonify(response)
    except Exception as e:
        app.logger.exception("Error occurred while creating Patient.")
        return jsonify({"error": str(e)}), 500

@app.route('/api/encounter', methods=['POST'])
def api_create_encounter():
    data = request.get_json()
    app.logger.info(f"Received request to create encounter for Patient ID: {data.get('patient_id')}")
    try:
        response = create_encounter(
            patient_id=data['patient_id'],
            encounter_status=data['encounter_status'],
            encounter_text=data['encounter_text'],
            healthcare_client=healthcare_client,
            fhir_store_name=fhir_store_name
        )
        app.logger.info(f"Successfully created Encounter. New resource ID: {response.get('id')}")
        return jsonify(response)
    except Exception as e:
        app.logger.exception("Error occurred while creating Encounter.")
        return jsonify({"error": str(e)}), 500

@app.route('/api/condition', methods=['POST'])
def api_create_condition():
    data = request.get_json()
    try:
        # The onset_datetime should be in ISO 8601 format
        onset_datetime = datetime.now(gmt7_timezone).isoformat()
        response = create_condition(
            patient_id=data['patient_id'],
            clinical_status=data['clinical_status'],
            verification_status=data['verification_status'],
            snomed_code=data['snomed_code'],
            condition_display=data['condition_display'],
            onset_datetime=onset_datetime,
            healthcare_client=healthcare_client,
            fhir_store_name=fhir_store_name,
        )
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/procedure', methods=['POST'])
def api_create_procedure():
    data = request.get_json()
    try:
        current_time_iso = datetime.now(gmt7_timezone).isoformat()
        response = create_procedure(
            patient_id=data['patient_id'],
            encounter_id=data['encounter_id'],
            procedure_status=data['procedure_status'],
            snomed_code=data['snomed_code'],
            procedure_display=data['procedure_display'],
            start_time=current_time_iso,
            end_time=current_time_iso, # Or handle separate end time
            reason_text=data['reason_text'],
            healthcare_client=healthcare_client,
            fhir_store_name=fhir_store_name
        )
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/practitioner', methods=['POST'])
def api_create_practitioner():
    data = request.get_json()
    try:
        response = create_practitioner(
            npi=data['npi'],
            family_name=data['family_name'],
            given_name=data['given_name'],
            healthcare_client=healthcare_client,
            fhir_store_name=fhir_store_name
        )
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medication_request', methods=['POST'])
def api_create_medication_request():
    data = request.get_json()
    try:
        response = create_medication_request(
            patient_id=data['patient_id'],
            practitioner_id=data['practitioner_id'],
            medication_status=data['medication_status'],
            medication_intent=data['medication_intent'],
            rxnorm_code=data['rxnorm_code'],
            medication_display=data['medication_display'],
            practitioner_display=data['practitioner_display'],
            dosage_text=data['dosage_text'],
            healthcare_client=healthcare_client,
            fhir_store_name=fhir_store_name
        )
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/diagnostic_report', methods=['POST'])
def api_create_diagnostic_report():
    data = request.get_json()
    try:
        response = create_diagnostic_report(
            patient_id=data['patient_id'],
            encounter_id=data['encounter_id'],
            practitioner_id=data['practitioner_id'],
            report_status=data['report_status'],
            loinc_code=data['loinc_code'],
            report_display=data['report_display'],
            conclusion=data['conclusion'],
            healthcare_client=healthcare_client,
            fhir_store_name=fhir_store_name
        )
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/observation', methods=['POST'])
def api_create_observation():
    data = request.get_json()
    try:
        current_time_iso = datetime.now(gmt7_timezone).isoformat()
        response = create_observation(
            patient_id=data['patient_id'],
            encounter_id=data['encounter_id'],
            observation_status=data['observation_status'],
            loinc_code=data['loinc_code'],
            observation_display=data['observation_display'],
            observation_value=float(data['observation_value']),
            observation_unit=data['observation_unit'],
            healthcare_client=healthcare_client,
            fhir_store_name=fhir_store_name,
            current_time=current_time_iso
        )
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# # Add this new API endpoint with the other API endpoints
# @app.route('/api/find/<resource_type>/<resource_id>', methods=['GET'])
# def api_get_resource(resource_type, resource_id):
#     """
#     Generic API endpoint to get any FHIR resource by its type and ID.
#     """
#     app.logger.info(f"Received request to find resource by ID. Type: {resource_type}, ID: {resource_id}")
#     try:
#         # We re-use the get_resource function from function.py
#         response = get_resource(
#             fhir_store_id=fhir_store_id,
#             resource_type=resource_type,
#             resource_id=resource_id,
#             fhir_store_parent=fhir_store_parent,
#             healthcare_client=healthcare_client
#         )
#         app.logger.info(f"Successfully found resource {resource_type}/{resource_id}.")
#         return jsonify(response)
#     except Exception as e:
#         # The Google API client often returns specific error structures
#         # We can parse them for a cleaner error message
#         error_details = getattr(e, 'content', str(e))
#         try:
#             # Try to parse the json error content from the client library
#             import json
#             error_json = json.loads(error_details)
#             message = error_json.get("error", {}).get("message", "An unknown error occurred.")
#             if "NOT_FOUND" in message:
#                  app.logger.warning(f"Resource not found: {resource_type}/{resource_id}")
#                  return jsonify({"error": f"Resource of type '{resource_type}' with ID '{resource_id}' was not found."}), 404
#             else:
#                 app.logger.error(f"API error finding resource: {message}")
#                 return jsonify({"error": message}), 500
#         except:
#             app.logger.exception(f"Generic error finding resource {resource_type}/{resource_id}.")
#             return jsonify({"error": str(e)}), 500

@app.route('/api/search/patient/mrn/<mrn>', methods=['GET'])
def api_search_patient_by_mrn(mrn):
    """API endpoint to search for a patient by their MRN."""
    app.logger.info(f"Received request to search for patient by MRN: {mrn}")
    try:
        bundle = search_patient_by_mrn(
            project_id=project_id,
            location=location,
            dataset_id=dataset_id,
            fhir_store_id=fhir_store_id,
            mrn=mrn
        )
        app.logger.info(f"Search for MRN {mrn} returned {bundle.get('total', 0)} results.")
        return jsonify(bundle)
    except Exception as e:
        app.logger.exception(f"Error occurred during patient search for MRN: {mrn}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/patient/everything/mrn/<mrn>', methods=['GET'])
def api_get_patient_everything_by_mrn(mrn):
    """
    API endpoint to find a patient by MRN and get all their related data.
    """
    app.logger.info(f"Received request to get all records for patient with MRN: {mrn}")
    try:
        bundle = get_patient_everything_by_mrn(
            project_id=project_id,
            location=location,
            dataset_id=dataset_id,
            fhir_store_id=fhir_store_id,
            mrn=mrn
        )
        app.logger.info(f"Successfully retrieved $everything bundle for MRN: {mrn}. Total resources: {bundle.get('total', 0)}")
        return jsonify(bundle)
    except Exception as e:
        # Custom error handling for "not found"
        if "No patient found" in str(e):
             app.logger.warning(f"Could not find patient for $everything operation with MRN: {mrn}")
             return jsonify({"error": str(e)}), 404
        app.logger.exception(f"Error occurred during $everything operation for MRN: {mrn}")
        return jsonify({"error": str(e)}), 500
                    
# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
