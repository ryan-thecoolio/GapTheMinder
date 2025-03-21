document.addEventListener('DOMContentLoaded', function() {
    const stockButtons = document.querySelectorAll('.stock-btn');
    const answerButtonsContainer = document.getElementById('answerButtons');
    const questionText = document.getElementById('questionText');
    const selectedStockInput = document.getElementById('selectedStock');
    const selectedAnswerInput = document.getElementById('selectedAnswer');
    const questionIndexInput = document.getElementById('questionIndex');

    function selectStock(stock, button) {
        selectedStockInput.value = stock;

        // Reset stock button styles
        stockButtons.forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.remove('btn-gold');
            btn.classList.add('btn-secondary');
        });

        // Highlight selected stock button
        button.classList.remove('btn-secondary');
        button.classList.add('btn-gold'); // Turn selected button gold

        updateQuestion(stock);
    }

    function updateQuestion(stock) {
        if (stock in questions) {
            // Pick a random question index
            const questionIndex = Math.floor(Math.random() * questions[stock].length);
            const questionObj = questions[stock][questionIndex];

            // Store the question index to send with the form
            questionIndexInput.value = questionIndex;

            questionText.innerText = questionObj.question;
            answerButtonsContainer.innerHTML = "";

            questionObj.choices.forEach(choice => {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.className = "btn btn-secondary answer-btn"; // Default color for answer buttons
                btn.innerText = choice;
                btn.onclick = function() { selectAnswer(choice, btn); };
                answerButtonsContainer.appendChild(btn);
            });

            // Clear previous answer selection when switching stocks
            selectedAnswerInput.value = "";
        }
    }

    function selectAnswer(answer, button) {
        selectedAnswerInput.value = answer;

        // Reset answer button styles
        const answerButtons = document.querySelectorAll('.answer-btn');
        answerButtons.forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.remove('btn-gold');
            btn.classList.add('btn-secondary');
        });

        // Highlight selected answer button
        button.classList.remove('btn-secondary');
        button.classList.add('btn-gold'); // Turn selected answer button gold
    }

    // Make functions globally accessible
    window.selectStock = selectStock;
    window.selectAnswer = selectAnswer;
});