document.addEventListener('DOMContentLoaded', function() {

    const responseElement = document.getElementById('api-response');
    const idStoreElements = {
        patient: document.getElementById('last-patient-id'),
        encounter: document.getElementById('last-encounter-id'),
        practitioner: document.getElementById('last-practitioner-id'),
    };

    /**
     * Finds all input fields that need a specific resource ID and automatically fills them.
     * Also adds a temporary visual flash to indicate the field was updated.
     * @param {string} resourceType The type of resource (e.g., 'patient', 'encounter').
     * @param {string} id The actual ID to fill in.
     */
    function autofillInputs(resourceType, id) {
        if (!id) return;

        // Find all inputs with a name like 'patient_id', 'encounter_id', etc.
        const inputsToFill = document.querySelectorAll(`input[name="${resourceType}_id"]`);

        inputsToFill.forEach(input => {
            input.value = id;
            // Add a temporary flash effect for better UX
            input.classList.add('input-flash');
            setTimeout(() => {
                input.classList.remove('input-flash');
            }, 1500); // Flash lasts 1.5 seconds
        });
    }


    /**
     * Adds click listeners to the 'Quick Reference ID' spans.
     * When clicked, they will autofill the corresponding inputs.
     */
    function addClickToFillListeners() {
        for (const resourceType in idStoreElements) {
            const element = idStoreElements[resourceType];
            element.addEventListener('click', () => {
                const id = element.textContent;
                if (id && id !== 'N/A') {
                    autofillInputs(resourceType, id);
                }
            });
        }
    }


    /**
     * A generic function to handle all form submissions.
     * @param {string} formId The ID of the form element.
     * @param {string} apiEndpoint The API endpoint to send the request to.
     * @param {string} resourceType The type of FHIR resource being created.
     */
    function handleFormSubmit(formId, apiEndpoint, resourceType) {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', function(event) {
            event.preventDefault();
            responseElement.textContent = 'Loading...';

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch(apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || 'Unknown server error') });
                }
                return response.json();
            })
            .then(result => {
                responseElement.textContent = JSON.stringify(result, null, 2);

                // Check if a resource with a storable ID was created
                if (result.id && idStoreElements[resourceType]) {
                    // 1. Update the Quick Reference display
                    idStoreElements[resourceType].textContent = result.id;

                    // 2. Automatically fill inputs that need this new ID
                    autofillInputs(resourceType, result.id);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                responseElement.textContent = 'Error: ' + error.message;
            });
        });
    }

    // --- Main Initialization ---
    // Initialize form handlers for all resource types
    handleFormSubmit('form-patient', '/api/patient', 'patient');
    handleFormSubmit('form-practitioner', '/api/practitioner', 'practitioner');
    handleFormSubmit('form-encounter', '/api/encounter', 'encounter');
    handleFormSubmit('form-condition', '/api/condition', null); // No ID to store
    handleFormSubmit('form-procedure', '/api/procedure', null); // No ID to store
    handleFormSubmit('form-medication-request', '/api/medication_request', null); // No ID to store
    handleFormSubmit('form-diagnostic-report', '/api/diagnostic_report', null); // No ID to store
    handleFormSubmit('form-observation', '/api/observation', null); // No ID to store

    // Activate the 'Click to Fill' functionality
    addClickToFillListeners();
});