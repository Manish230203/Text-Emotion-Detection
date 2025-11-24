document.getElementById('emotion-form').addEventListener('submit', function(event) {
    event.preventDefault();
    var text = document.getElementById("text-input").value;
    predictEmotion(text);
});

function predictEmotion(text) {
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        displayResult(data);
        document.getElementById("show-graph-btn").style.display = "block";
        if (data.probability && data.probability.length > 0) {
            plotEmotionChart(data.probability[0]);
        } else {
            console.error('Error: Empty or undefined probabilities array');
        }
    })
    .catch(error => console.error('Error:', error));
}
function displayResult(data) {
    var resultContainer = document.getElementById("result-container");
    var prediction = data.prediction;
    var probability = data.probability
    var max_probability = data.max_probability

    
    resultContainer.innerHTML = `
        <h3>Input Text :</h3>
        <p class="inline">${data.text}</p>
        <h3>Predicted Emotion :</h3>
        <p class="inline">${prediction}</p>
        <p class="inline">Confidence: ${max_probability * 100}%</p>
    `;
    resultContainer.classList.add('show-result'); // Add class to show result
}


function plotEmotionChart(probabilities) {
    var ctx = document.getElementById('emotion-chart').getContext('2d');
    var emotions = ["anger",  "fear", "happy/joy", "love", "neutral", "sadness", "surprise", "worry"];

    if (window.emotionChart) {
        window.emotionChart.destroy();
        document.getElementById("graph-container").style.display = "none";

    }
    window.emotionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: emotions,
            datasets: [{
                label: 'Emotion Probability',
                data: probabilities,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}



document.getElementById("show-graph-btn").addEventListener("click", function() {
    document.getElementById("graph-container").style.display = "block";
    // Plot the chart if data is available
    if (window.emotionChart && window.emotionChart.data.labels.length > 0) {
        window.emotionChart.update(); // Update chart in case data has changed
    } else {
        // Fetch probabilities and plot the chart if not already available
        fetch('/predict')
            .then(response => response.json())
            .then(data => {
                plotEmotionChart(data.probability);
            })
            .catch(error => console.error('Error:', error));
    }
});

// Event listener for the button to close the graph
document.getElementById("close-graph-btn").addEventListener("click", function() {
    document.getElementById("graph-container").style.display = "none";
});