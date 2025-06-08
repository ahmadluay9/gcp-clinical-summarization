document.addEventListener('DOMContentLoaded', function() {
    console.log("Find page script initialized.");

    const findResourceForm = document.getElementById('find-resource-form');
    const findMrnForm = document.getElementById('find-mrn-form');
    const responseElement = document.getElementById('api-response');

    if (findResourceForm) {
        findResourceForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const resourceType = document.getElementById('resource-type').value;
            const resourceId = document.getElementById('resource-id').value;
            if (!resourceType || !resourceId) { return; }
            const apiUrl = `/api/find/${resourceType}/${resourceId}`;
            fetchData(apiUrl, 'Searching for resource by ID...');
        });
    }

    if (findMrnForm) {
        const findPatientBtn = document.getElementById('find-by-mrn-btn');
        const findEverythingBtn = document.getElementById('find-everything-by-mrn-btn');
        const mrnInput = document.getElementById('mrn-value');

        findPatientBtn.addEventListener('click', () => {
            if (!mrnInput.value) { return; }
            const apiUrl = `/api/search/patient/mrn/${mrnInput.value}`;
            fetchData(apiUrl, 'Searching for patient...');
        });

        findEverythingBtn.addEventListener('click', () => {
            if (!mrnInput.value) { return; }
            const apiUrl = `/api/patient/everything/mrn/${mrnInput.value}`;
            fetchData(apiUrl, 'Searching for all patient records...');
        });
    }

    const fetchData = (url, initialMessage) => {
        responseElement.textContent = '';
        responseElement.innerHTML = `<p>${initialMessage}</p>`;

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                let formattedHtml = '';
                if (data.resourceType === 'Bundle') {
                    if (data.total === 0) {
                        formattedHtml = '<p>No results found.</p>';
                    } else {
                        data.entry.forEach(entry => {
                            formattedHtml += formatResource(entry.resource);
                        });
                    }
                } else {
                    formattedHtml = formatResource(data);
                }
                responseElement.innerHTML = formattedHtml;
            })
            .catch(error => {
                responseElement.innerHTML = `
                    <div class="resource-card error-card">
                        <h3 class="resource-title">An Error Occurred</h3>
                        <p>${error.message}</p>
                    </div>`;
            });
    };

    function formatResource(resource) {
        if (!resource || !resource.resourceType) {
            return '';
        }
        switch (resource.resourceType) {
            case 'Patient': return formatPatient(resource);
            case 'Encounter': return formatEncounter(resource);
            case 'Condition': return formatCondition(resource);
            case 'Observation': return formatObservation(resource);
            case 'Procedure': return formatProcedure(resource);
            case 'MedicationRequest': return formatMedicationRequest(resource);
            case 'DiagnosticReport': return formatDiagnosticReport(resource);
            default:
                return `<div class="resource-card"><h3 class="resource-title default-title">${resource.resourceType} <span>ID: ${resource.id}</span></h3><p>No specific formatter for this resource type yet.</p></div>`;
        }
    }
    
    function formatPatient(patient) {
        const name = patient.name ? `${patient.name[0].given.join(' ')} ${patient.name[0].family}` : 'N/A';
        const mrnIdentifier = patient.identifier?.find(id => id.type?.coding?.[0]?.code === 'MR');
        const mrn = mrnIdentifier ? mrnIdentifier.value : 'N/A';
        return `<div class="resource-card"><h3 class="resource-title patient-title">Patient <span>ID: ${patient.id}</span></h3><div class="details-grid"><div><strong>Name:</strong> ${name}</div><div><strong>MRN:</strong> ${mrn}</div><div><strong>Gender:</strong> ${patient.gender || 'N/A'}</div><div><strong>Birth Date:</strong> ${patient.birthDate || 'N/A'}</div></div></div>`;
    }

    function formatEncounter(encounter) {
    // The 'period' variable and the 'Date' div have been completely removed.
    return `
        <div class="resource-card">
            <h3 class="resource-title encounter-title">Encounter <span>ID: ${encounter.id}</span></h3>
            <div class="details-grid">
                <div><strong>Status:</strong> ${encounter.status || 'N/A'}</div>
                <div class="full-width"><strong>Reason:</strong> ${encounter.reasonCode?.[0]?.text || 'N/A'}</div>
            </div>
        </div>`;
}
    
    function formatCondition(condition) {
        const onset = condition.onsetDateTime ? new Date(condition.onsetDateTime).toLocaleDateString() : 'N/A';
        // IMPROVED: Check both .text and .coding[0].display
        const displayName = condition.code?.text || condition.code?.coding?.[0]?.display || 'N/A';
        return `<div class="resource-card"><h3 class="resource-title condition-title">Condition <span>ID: ${condition.id}</span></h3><div class="details-grid"><div class="full-width"><strong>Condition:</strong> ${displayName}</div><div><strong>Clinical Status:</strong> ${condition.clinicalStatus?.coding?.[0]?.display || 'N/A'}</div><div><strong>Onset Date:</strong> ${onset}</div></div></div>`;
    }

    function formatObservation(obs) {
        const value = obs.valueQuantity ? `${obs.valueQuantity.value} ${obs.valueQuantity.unit}` : (obs.valueCodeableConcept?.text || 'N/A');
        const effectiveDate = obs.effectiveDateTime ? new Date(obs.effectiveDateTime).toLocaleString() : 'N/A';
        // FIXED: Check both .text and .coding[0].display for the name
        const displayName = obs.code?.text || obs.code?.coding?.[0]?.display || 'N/A';
        return `<div class="resource-card"><h3 class="resource-title observation-title">Observation <span>ID: ${obs.id}</span></h3><div class="details-grid"><div class="full-width"><strong>Observation:</strong> ${displayName}</div><div><strong>Value:</strong> ${value}</div><div><strong>Date:</strong> ${effectiveDate}</div></div></div>`;
    }
    
    function formatProcedure(proc) {
        const performed = proc.performedPeriod ? new Date(proc.performedPeriod.start).toLocaleDateString() : 'N/A';
        // IMPROVED: Check both .text and .coding[0].display
        const displayName = proc.code?.text || proc.code?.coding?.[0]?.display || 'N/A';
        return `<div class="resource-card"><h3 class="resource-title procedure-title">Procedure <span>ID: ${proc.id}</span></h3><div class="details-grid"><div class="full-width"><strong>Procedure:</strong> ${displayName}</div><div><strong>Status:</strong> ${proc.status || 'N/A'}</div><div><strong>Date:</strong> ${performed}</div><div class="full-width"><strong>Reason:</strong> ${proc.reasonCode?.[0]?.text || 'N/A'}</div></div></div>`;
    }

    function formatMedicationRequest(medReq) {
        const authoredOn = medReq.authoredOn ? new Date(medReq.authoredOn).toLocaleDateString() : 'N/A';
         // IMPROVED: Check both .text and .coding[0].display
        const displayName = medReq.medicationCodeableConcept?.text || medReq.medicationCodeableConcept?.coding?.[0]?.display || 'N/A';
        return `<div class="resource-card"><h3 class="resource-title medication-title">Medication Request <span>ID: ${medReq.id}</span></h3><div class="details-grid"><div class="full-width"><strong>Medication:</strong> ${displayName}</div><div><strong>Status:</strong> ${medReq.status || 'N/A'}</div><div><strong>Intent:</strong> ${medReq.intent || 'N/A'}</div><div><strong>Prescribed On:</strong> ${authoredOn}</div><div class="full-width"><strong>Dosage:</strong> ${medReq.dosageInstruction?.[0]?.text || 'N/A'}</div><div><strong>Prescriber:</strong> ${medReq.requester?.display || 'N/A'}</div></div></div>`;
    }

    function formatDiagnosticReport(report) {
        const issued = report.issued ? new Date(report.issued).toLocaleString() : 'N/A';
        // IMPROVED: Check both .text and .coding[0].display
        const displayName = report.code?.text || report.code?.coding?.[0]?.display || 'N/A';
        return `<div class="resource-card"><h3 class="resource-title diagnostic-title">Diagnostic Report <span>ID: ${report.id}</span></h3><div class="details-grid"><div class="full-width"><strong>Report:</strong> ${displayName}</div><div><strong>Status:</strong> ${report.status || 'N/A'}</div><div><strong>Issued:</strong> ${issued}</div><div class="full-width"><strong>Conclusion:</strong> ${report.conclusion || 'N/A'}</div></div></div>`;
    }
});