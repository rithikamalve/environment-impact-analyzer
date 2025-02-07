class EcoImpactCalculator {
    constructor() {
        this.form = document.getElementById('impactForm');
        this.scoreElement = document.getElementById('score');
        this.waterMetric = document.getElementById('waterMetric');
        this.carbonMetric = document.getElementById('carbonMetric');
        this.energyMetric = document.getElementById('energyMetric');
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    calculateScore(waterUsage, carbonFootprint, energyConsumption) {
        const waterScore = (waterUsage / 1000) * 33.33;
        const carbonScore = (carbonFootprint / 100) * 33.33;
        const energyScore = (energyConsumption / 100) * 33.33;
        return Math.min(Math.round(waterScore + carbonScore + energyScore), 100);
    }

    updateMetrics(waterUsage, carbonFootprint, energyConsumption, totalScore) {
        this.scoreElement.textContent = totalScore;
        this.waterMetric.textContent = `${waterUsage} L`;
        this.carbonMetric.textContent = `${carbonFootprint} kg`;
        this.energyMetric.textContent = `${energyConsumption} kWh`;
    }

    handleSubmit(e) {
        e.preventDefault();
        
        const waterUsage = parseFloat(document.getElementById('waterUsage').value);
        const carbonFootprint = parseFloat(document.getElementById('carbonFootprint').value);
        const energyConsumption = parseFloat(document.getElementById('energyConsumption').value);

        const totalScore = this.calculateScore(waterUsage, carbonFootprint, energyConsumption);
        this.updateMetrics(waterUsage, carbonFootprint, energyConsumption, totalScore);
    }
}

// Initialize the calculator when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EcoImpactCalculator();
});