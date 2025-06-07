// calculator.js
document.addEventListener('DOMContentLoaded', function() {
    // Set the widths of the progress bars

    // Water usage bar
    const waterValue = parseFloat(document.getElementById('waterValue').textContent);
    if (!isNaN(waterValue)) {
        const waterPercentage = Math.min(waterValue / 5 * 100, 100);
        document.querySelector('.water-fill').style.width = waterPercentage + '%';
    }

    // Carbon footprint bar
    const carbonValue = parseFloat(document.getElementById('carbonValue').textContent);
    if (!isNaN(carbonValue)) {
        const carbonPercentage = Math.min(carbonValue / 2 * 100, 100);
        document.querySelector('.carbon-fill').style.width = carbonPercentage + '%';
    }

    // Energy usage bar
    const energyValue = parseFloat(document.getElementById('energyValue').textContent);
    if (!isNaN(energyValue)) {
        const energyPercentage = Math.min(energyValue / 5 * 100, 100);
        document.querySelector('.energy-fill').style.width = energyPercentage + '%';
    }

    // Overall impact bar
    const impactScore = parseFloat(document.getElementById('impactScore').textContent);
    if (!isNaN(impactScore)) {
        document.getElementById('impactBar').style.width = (impactScore * 100) + '%';
    }
});
