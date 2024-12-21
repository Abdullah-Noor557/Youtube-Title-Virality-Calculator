const titleInput = document.getElementById('titleInput');
const calculateBtn = document.getElementById('calculateBtn');
const resultDiv = document.getElementById('result');
const scoreSpan = document.getElementById('score');
const errorDiv = document.getElementById('error');

calculateBtn.addEventListener('click', async () => {
    const title = titleInput.value.trim();

    if (!title) {
        alert('Please enter a title');
        return;
    }

    try {
        errorDiv.classList.remove('visible');
        calculateBtn.disabled = true;
        calculateBtn.textContent = 'Calculating...';

        // Now you can directly use axios
        const response = await axios.post('http://localhost:8000/virality-score', {
            title: title
        });

        resultDiv.classList.add('visible');
        scoreSpan.textContent = response.data.virality_score + "%";
    } catch (error) {
        console.error('Error:', error);
        errorDiv.classList.add('visible');
    } finally {
        calculateBtn.disabled = false;
        calculateBtn.textContent = 'Calculate';
    }
});
