function get_parsed_obj(data) {
    var json_to_html_tag = document.getElementById("json_to_html");   
    return JSON.parse(data);
}

function isObject(item) {
    return (typeof item === "object" && !Array.isArray(item) && item !== null);
    // return (typeof item === "object" && item !== null);
}

// Function to check if an item is an array of objects
function isArrayOfObjects(item) {
    return Array.isArray(item) && item.length > 0 && isObject(item[0]);
}


function isObject(item) {
    return (typeof item === "object" && !Array.isArray(item) && item !== null);
    // return (typeof item === "object" && item !== null);
}

// Function to check if an item is an array of objects
function isArrayOfObjects(item) {
    return Array.isArray(item) && item.length > 0 && isObject(item[0]);
}


function createTable(parsed_obj) {
    // Fields to exclude from the table
    const excludedFields = ["uniprot_data", "kegg",
        "second_structure_features", "helix", "strand", "turn",
        "domains", "regions", "plots", "plots_s", "plots_sub",
    ];
    console.log("entro en createTable_")
    // Get the table element
    const table = document.getElementById("responseTable"); // Make sure you have an element with id="responseTable" in your HTML

    // Check for an existing tbody
    let responseBody = table.querySelector("#responseBody");

    if (responseBody) {
        // Clear existing rows if tbody exists
        responseBody.innerHTML = "";
    } else {
        // Create a new tbody if it doesn't exist
        responseBody = document.createElement("tbody");
        responseBody.id = "responseBody";
        table.appendChild(responseBody);
    }

    // Loop through the object and create table rows
    for (const key in parsed_obj) {
        if (parsed_obj.hasOwnProperty(key) && !excludedFields.includes(key)) {
            const value = parsed_obj[key];
            const valueText = typeof value === 'object' ? JSON.stringify(value) : value;

            const row = responseBody.insertRow(); // Use responseBody here instead of table
            const keyCell = row.insertCell();
            const valueCell = row.insertCell();

            keyCell.textContent = key;
            valueCell.textContent = valueText;
        }
    }
}


function extractPlotKeys(parsed_obj) {
    const plotKeysArray = [];

    for (const key in parsed_obj.plots) {
        if (parsed_obj.plots.hasOwnProperty(key)) {
            try {
                const plotData = JSON.parse(parsed_obj.plots[key]);
                if (typeof plotData === 'object') {
                    plotKeysArray.push(key);
                }
            } catch (error) {
                // Handle JSON parsing error if needed
                console.error(`Error parsing JSON for key "${key}":`, error);
            }
        }
    }

    return plotKeysArray;
}


function plotWithLayout(plotKeys, parsed_obj) {

    console.log('Inside plotWithLayout');
    const myDiv = document.getElementById("myDiv");
    console.log('myDiv:', myDiv);


    // Clear any previous content in myDiv
    myDiv.innerHTML = "";

    for (const key of plotKeys) {
        const plot = get_parsed_obj(parsed_obj.plots[key]);

        // Check if plot and plot.layout are defined and if layout is not an empty object
        if (plot && plot.layout && Object.keys(plot.layout).length > 0) {
            const plotDiv = document.createElement("div");
            myDiv.appendChild(plotDiv);

            // Create a new Plotly plot in the current plotDiv
            Plotly.newPlot(plotDiv, plot.data, plot.layout);
        }
    }
}


function plotWithLayoutsec_struct(parsed_obj) {
    const myDiv2 = document.getElementById("myDiv2");

   
    // Clear any previous content in myDiv2
    myDiv2.innerHTML = "";

    // Check if parsed_obj.plots_s is defined
    if (parsed_obj.plots_s) {
        const plot_sec = get_parsed_obj(parsed_obj.plots_s.secondary_structure);

        

        // Check if plot_sec and plot_sec.layout are defined and if layout is not an empty object
        if (plot_sec && plot_sec.layout && Object.keys(plot_sec.layout).length > 0) {
            const plotDiv2 = document.createElement("div");
            myDiv2.appendChild(plotDiv2);

            // Debugging: Log the plot_sec data
            console.log("PlotSec Data for Key:", plot_sec);

            graphOptions = { editable: true, displaylogo: false, responsive: true }

            // Create a new Plotly plot in the current plotDiv2
            Plotly.newPlot(plotDiv2, plot_sec.data, plot_sec.layout, graphOptions)
                .then(() => console.log("Plot created successfully"))
                .catch(error => console.error("Plot creation error:", error));
        } else {
            console.warn("No valid data or layout for 'plots_s.secondary_structure'.");
            }
    } else {
            console.warn("No data available for 'plots_s.secondary_structure'.");
        }
}

function plotWithLayoutsub_struct(parsed_obj) {
    const myDiv3 = document.getElementById("myDiv3");

   
    // Clear any previous content in myDiv2
    myDiv3.innerHTML = "";

    // Check if parsed_obj.plots_s is defined
    if (parsed_obj.plots_sub) {
        const plot_sub = get_parsed_obj(parsed_obj.plots_sub.subcellular_features);

        

        // Check if plot_sec and plot_sec.layout are defined and if layout is not an empty object
        if (plot_sub && Object.keys(plot_sub.layout).length > 0) {
            //(plot_sub && plot_sub.layout && Object.keys(plot_sub.layout).length > 0)
            const plotDiv3 = document.createElement("div");
            myDiv3.appendChild(plotDiv3);

            // Debugging: Log the plot_sec data
            console.log("Subcellular features Data for Key:", plot_sub);

            graphOptions = { editable: true, displaylogo: false, responsive: true }

            // Create a new Plotly plot in the current plotDiv2
            Plotly.newPlot(plotDiv3, plot_sub.data, plot_sub.layout, graphOptions)
                .then(() => console.log("Plot created successfully"))
                .catch(error => console.error("Plot creation error:", error));
        } else {
            console.warn("No valid data or layout for 'plots_sub.subcellular_features'.");
            }
    } else {
            console.warn("No data available for 'plots_sub.subcellular_features'.");
        }
}



function createTd(text) {
    var td = document.createElement('td');
    td.textContent = text;
    return td;
  }
  
    
  function generateTable_prot(parsed_obj, excludedFields = []) {
    const table = document.createElement('table');

    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    if (parsed_obj.length > 0) {
        Object.keys(parsed_obj[0]).forEach(key => {
            if (!excludedFields.includes(key)) {
                const th = document.createElement('th');
                th.textContent = key;
                headerRow.appendChild(th);
            }
        });
    }
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create table body
    const tbody = document.createElement('tbody');
    if (!Array.isArray(parsed_obj)) {
        console.log('parsed_obj is not an array');
        parsed_obj = JSON.parse(parsed_obj);
    }

    parsed_obj.forEach(item => {
        const tr = document.createElement('tr');
        Object.keys(item).forEach(key => {
            if (!excludedFields.includes(key)) {
                const td = document.createElement('td');
                td.textContent = item[key] !== null ? item[key] : '';
                tr.appendChild(td);
            }
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    return table;
}
   
    function generateTable(parsed_obj, excludedFields ) {
        

        const jsonKeys = Object.keys(parsed_obj);
        tabtab = generateTable_prot(parsed_obj, excludedFields );
        return tabtab;
    }        

function sequence_chunk(sequence, chunkSize) {
    if (typeof sequence !== 'string' || sequence !== sequence.toUpperCase()) {
      throw new Error('Input must be a sequence of capital letters');
    }
  
    if (chunkSize <= 0 || chunkSize > sequence.length) {
      throw new Error('Chunk size must be a positive integer less than or equal to the sequence length');
    }
  
    const chunks = [];
    for (let i = 0; i < sequence.length; i += chunkSize) {
      chunks.push(sequence.slice(i, i + chunkSize));
    }
  
    return chunks;
  }


// Function to trigger download of the FASTA file
function downloadFasta(content,  uniprotId) {
    const blob = new Blob([content], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${uniprotId}.fasta`; // Set the filename as uniprotId.fasta;
    link.click();
}

// Function to generate FASTA content
function toFasta(uniprotId, fetchedSequence) {
    const fastaContent = `>${uniprotId}\n${fetchedSequence}`;
    return fastaContent;
}


// Define the blastp function
function blastp() {
    console.log("Blastp function executed"); // Check if this log appears in the console

    // Assuming you have a variable named 'aminoacid_consensus'
    const aminoacidSequence = aminoacid_consensus;

    // Construct BLASTp link
    const blastpLink = `https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE=Proteins&PROGRAM=blastp&BLAST_PROGRAMS=blastp&PAGE_TYPE=BlastSearch&BLAST_SPEC=blast2seq&DATABASE=n/a&QUERY=${aminoacidSequence}`;

    // Open the link in a new tab
    window.open(blastpLink, '_blank');
}

// Define the blastp function
function blastn() {
    console.log("Blastn function executed"); // Check if this log appears in the console

    // Assuming you have a variable named 'aminoacid_consensus'
    const nucleotiddSequence = nucleotide_consensus;

    // Construct BLASTp link
    const blastnLink = `https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE=MegaBlast&PROGRAM=blastn&BLAST_PROGRAMS=megaBlast&PAGE_TYPE=BlastSearch&BLAST_SPEC=blast2seq&DATABASE=n/a&QUERY=${nucleotiddSequence}`;

    // Open the link in a new tab
    window.open(blastnLink, '_blank');
}


async function fetchExistingEndpoint(my_filename) {
    try {
        let url;
        // Check if the provided UNIPROT ID value contains digits in certain positions
        //if (/[0-9]/.test(uniprotIdValue[1]) || /[0-9]/.test(uniprotIdValue[2])) {
        //    url = `https://bc92sqjf99.execute-api.us-east-1.amazonaws.com/v2/search?UNIPROT_id=${uniprotIdValue}`;
        //} else {
        //    url = `https://bc92sqjf99.execute-api.us-east-1.amazonaws.com/v2/search?UNIPROT_id=${uniprotIdValue.toLowerCase()}`;
        //}
        
		    //url = `https://173qaj7qxk.execute-api.us-east-1.amazonaws.com/v2/search`;
            url = `https://173qaj7qxk.execute-api.us-east-1.amazonaws.com/v2/inova-ProcessStudies-sam?fileid=${my_filename}`;
		
        // Fetch data from the specified URL
        await new Promise(resolve => setTimeout(resolve, 1000)); //sleep 1 second
        const response = await fetch(url);  
        
        // Check if the response is successful
        if (!response.ok) {
            throw new Error('Failed to fetch data from the existing endpoint');
        } 
		console.log('1'); // Do something with the data
        console.log(response); // Do something with the data
        // Parse the JSON response
		const data = await response.json();
		
        //const data = await response.json();
		console.log('2'); // Do something with the data
        console.log(data); // Do something with the data		
		//const data = JSON.parse(responseData.body);
		
		//console.log('3');		
        //console.log(data); // Do something with the data
        // Return the parsed data
        return data;
    } catch (error) {
        // Handle any errors that occur during the fetch operation
        console.error('Error occurred while fetching data from the existing endpoint:', error);
        throw error; // Rethrow the error to handle it where the function is called
    }
}
