/**
 * Bank Account Management System
 * Main JavaScript file
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Format currency displays
    formatCurrencyDisplays();
    
    // Add the current year to the footer
    updateFooterYear();
});

/**
 * Format all currency displays to show commas for thousands
 */
function formatCurrencyDisplays() {
    document.querySelectorAll('.currency-display').forEach(function(element) {
        const value = parseFloat(element.textContent);
        if (!isNaN(value)) {
            element.textContent = formatCurrency(value);
        }
    });
}

/**
 * Format a number as currency
 * @param {number} value - The number to format
 * @returns {string} - The formatted currency string
 */
function formatCurrency(value) {
    return '£' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

/**
 * Update the footer with the current year
 */
function updateFooterYear() {
    const footerYear = document.querySelector('.footer .text-muted');
    if (footerYear) {
        const year = new Date().getFullYear();
        footerYear.textContent = footerYear.textContent.replace(/\d{4}/, year);
    }
}

/**
 * Toggle the visibility of a collapsible element
 * @param {string} elementId - The ID of the element to toggle
 */
function toggleCollapsible(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.toggle('d-none');
    }
}

/**
 * Show a confirmation dialog before performing a dangerous action
 * @param {string} message - The confirmation message
 * @returns {boolean} - Whether the user confirmed the action
 */
function confirmAction(message) {
    return window.confirm(message);
}
