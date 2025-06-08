document.addEventListener('DOMContentLoaded', function() {

    const findForm = document.getElementById('find-resource-form');
    const responseElement = document.getElementById('api-response');

    if (findForm) {
        findForm.addEventListener('submit', function(event) {
            event.preventDefault();
            responseElement.textContent = 'Searching...';

            const resourceType = document.getElementById('resource-type').value;
            const resourceId = document.getElementById('resource-id').value;

            if (!resourceType || !resourceId) {
                responseElement.textContent = 'Error: Both Resource Type and Resource ID are required.';
                return;
            }

            // Construct the API URL from the form values
            const apiUrl = `/api/find/${resourceType}/${resourceId}`;

            fetch(apiUrl)
                .then(response => {
                    // Check if the response is ok (status in the range 200-299)
                    if (!response.ok) {
                        // If not ok, parse the error JSON and throw an error to be caught by the .catch block
                        return response.json().then(errorData => {
                            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    // Display the successful response, pretty-printed
                    responseElement.textContent = JSON.stringify(data, null, 2);
                })
                .catch(error => {
                    console.error('Fetch error:', error);
                    // Display the error message from the thrown error
                    responseElement.textContent = `Error: ${error.message}`;
                });
        });
    }
const findMrnForm = document.getElementById('find-mrn-form');
    if (findMrnForm) {
        const findPatientBtn = document.getElementById('find-by-mrn-btn');
        const findEverythingBtn = document.getElementById('find-everything-by-mrn-btn');
        const mrnInput = document.getElementById('mrn-value');

        // Function to perform the fetch and display results
        const fetchData = (url, initialMessage) => {
            responseElement.textContent = initialMessage;
            
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
                    if (data.total === 0) {
                        responseElement.textContent = `No results found for MRN: ${mrnInput.value}`;
                    } else {
                        responseElement.textContent = JSON.stringify(data, null, 2);
                    }
                })
                .catch(error => {
                    console.error('Fetch error:', error);
                    responseElement.textContent = `Error: ${error.message}`;
                });
        };

        // Event listener for the "Find Patient Only" button
        findPatientBtn.addEventListener('click', () => {
            if (!mrnInput.value) {
                responseElement.textContent = 'Error: MRN is required.';
                return;
            }
            const apiUrl = `/api/search/patient/mrn/${mrnInput.value}`;
            fetchData(apiUrl, 'Searching for patient...');
        });

        // Event listener for the "Find All Records" button
        findEverythingBtn.addEventListener('click', () => {
            if (!mrnInput.value) {
                responseElement.textContent = 'Error: MRN is required.';
                return;
            }
            const apiUrl = `/api/patient/everything/mrn/${mrnInput.value}`;
            fetchData(apiUrl, 'Searching for all patient records...');
        });
    }
});
