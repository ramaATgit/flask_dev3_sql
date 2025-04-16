/**
 * Bank Account Management System
 * Charts JavaScript file
 */

// Chart color palette
const chartColors = [
    'rgba(75, 192, 192, 0.7)',
    'rgba(54, 162, 235, 0.7)',
    'rgba(255, 206, 86, 0.7)',
    'rgba(255, 99, 132, 0.7)',
    'rgba(153, 102, 255, 0.7)',
    'rgba(255, 159, 64, 0.7)',
    'rgba(199, 199, 199, 0.7)',
    'rgba(83, 102, 255, 0.7)'
];

// Chart border colors
const chartBorderColors = [
    'rgba(75, 192, 192, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(255, 99, 132, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)',
    'rgba(199, 199, 199, 1)',
    'rgba(83, 102, 255, 1)'
];

// Chart objects
let accountTypeChart = null;
let ownerChart = null;
let frnChart = null;

/**
 * Load chart data from the API
 */
function loadChartData() {
    fetch('/api/chart-data')
        .then(response => response.json())
        .then(data => {
            // Initialize or update charts
            createAccountTypeChart(data.account_types);
            createOwnerChart(data.owners);
            createFrnChart(data.frns);
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
        });
}

/**
 * Create or update the Account Type chart
 * @param {Object} data - The chart data
 */
function createAccountTypeChart(data) {
    const ctx = document.getElementById('accountTypeChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (accountTypeChart) {
        accountTypeChart.destroy();
    }
    
    // Create new chart
    accountTypeChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: chartColors,
                borderColor: chartBorderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#fff'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: £${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create or update the Owner chart
 * @param {Object} data - The chart data
 */
function createOwnerChart(data) {
    const ctx = document.getElementById('ownerChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (ownerChart) {
        ownerChart.destroy();
    }
    
    // Map owner codes to descriptive names
    const ownerLabels = data.labels.map(owner => {
        switch (owner) {
            case 'a': return 'Owner A';
            case 'i': return 'Owner I';
            case 'j': return 'Owner J';
            default: return owner;
        }
    });
    
    // Create new chart
    ownerChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ownerLabels,
            datasets: [{
                data: data.values,
                backgroundColor: chartColors,
                borderColor: chartBorderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#fff'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: £${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create or update the FRN chart
 * @param {Object} data - The chart data
 */
function createFrnChart(data) {
    const ctx = document.getElementById('frnChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (frnChart) {
        frnChart.destroy();
    }
    
    // Create new chart
    frnChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Total Balance',
                data: data.values,
                backgroundColor: 'rgba(75, 192, 192, 0.7)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '£' + value.toFixed(2);
                        },
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw || 0;
                            return `Balance: £${value.toFixed(2)}`;
                        }
                    }
                }
            }
        }
    });
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a page with charts
    if (document.getElementById('accountTypeChart')) {
        // If we're on the dashboard, initialize charts right away
        if (window.location.pathname === '/' || window.location.pathname === '') {
            loadChartData();
        }
    }
});
