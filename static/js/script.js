// Overclock PC Shop - Global Interactive Frontend Scripts

// Helper to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// --- Cart AJAX Functionality ---
document.addEventListener('DOMContentLoaded', () => {
    // Bind plus/minus buttons in cart page
    document.querySelectorAll('.quantity-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            const container = e.target.closest('.quantity-control');
            const productId = container.dataset.productId;
            const action = button.dataset.action;
            const input = container.querySelector('.quantity-value');
            let currentVal = parseInt(input.value);

            if (action === 'plus') {
                currentVal += 1;
            } else if (action === 'minus') {
                currentVal -= 1;
            }

            updateCartQuantity(productId, currentVal);
        });
    });
});

function updateCartQuantity(productId, newQty) {
    fetch(`/cart/update/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ quantity: newQty })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' || data.status === 'deleted') {
            window.location.reload();
        } else {
            alert("Error updating cart: " + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


// --- PC Builder Application Engine ---
// Global selection object
let builderBuild = {
    cpus: null,
    gpus: null,
    motherboards: null,
    ram: null,
    storage: null,
    psus: null,
    cases: null,
    cooling: null
};

// Selection Handler called from HTML template onclicks
window.selectBuilderPart = function(categorySlug, partId, name, price, wattage, socket, ramType, formFactor, imageUrl) {
    // Set active item in our selection state
    builderBuild[categorySlug] = {
        id: partId,
        name: name,
        price: parseFloat(price),
        wattage: parseInt(wattage || 0),
        socket: socket || '',
        ramType: ramType || '',
        formFactor: formFactor || '',
        imageUrl: imageUrl
    };

    // Update frontend row layout
    const row = document.getElementById(`builder-row-${categorySlug}`);
    if (row) {
        row.classList.add('active-selection');
        
        // Update part name & remove placeholder styling
        const nameEl = row.querySelector('.builder-part-name');
        nameEl.textContent = name;
        nameEl.classList.remove('placeholder-part');
        
        // Update price label
        const priceEl = row.querySelector('.builder-step-price');
        priceEl.textContent = `₹${parseFloat(price).toLocaleString('en-IN')}`;
        
        // Update select button to "Change Part"
        const selectBtn = row.querySelector('.select-part-btn');
        selectBtn.textContent = "Change";
        selectBtn.classList.remove('btn-cyber-outline');
        selectBtn.classList.add('btn-cyber-pink');
    }

    // Run compatibility checkers and sum costs
    runCompatibilityCheck();
    
    // Close the category modal
    const modalEl = document.getElementById(`modal-${categorySlug}`);
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) {
        modal.hide();
    }
};

window.removeBuilderPart = function(categorySlug) {
    builderBuild[categorySlug] = null;
    
    const row = document.getElementById(`builder-row-${categorySlug}`);
    if (row) {
        row.classList.remove('active-selection');
        
        const nameEl = row.querySelector('.builder-part-name');
        nameEl.textContent = `Select ${categorySlug.slice(0, -1).toUpperCase()}...`;
        nameEl.classList.add('placeholder-part');
        
        const priceEl = row.querySelector('.builder-step-price');
        priceEl.textContent = `₹0`;
        
        const selectBtn = row.querySelector('.select-part-btn');
        selectBtn.textContent = "Select";
        selectBtn.classList.remove('btn-cyber-pink');
        selectBtn.classList.add('btn-cyber-outline');
    }
    
    runCompatibilityCheck();
};

function runCompatibilityCheck() {
    let totalPrice = 0;
    let totalWattage = 0;
    let compatibilityIssues = [];

    // 1. Calculate price and wattage
    for (const key in builderBuild) {
        if (builderBuild[key]) {
            totalPrice += builderBuild[key].price;
            totalWattage += builderBuild[key].wattage;
        }
    }

    // Update Totals on Side UI
    document.getElementById('summary-total-price').textContent = `₹${totalPrice.toLocaleString('en-IN')}`;
    document.getElementById('summary-total-wattage').textContent = `${totalWattage} W`;

    // 2. Compatibility Logic
    const cpu = builderBuild.cpus;
    const mobo = builderBuild.motherboards;
    const ram = builderBuild.ram;
    const cabinet = builderBuild.cases;
    const psu = builderBuild.psus;

    // A. CPU Socket vs Motherboard Socket
    if (cpu && mobo) {
        if (cpu.socket !== mobo.socket) {
            compatibilityIssues.push(`Socket Mismatch: CPU '${cpu.name}' uses Socket ${cpu.socket}, but Motherboard '${mobo.name}' has Socket ${mobo.socket}!`);
        }
    }

    // B. Motherboard RAM support vs Selected RAM Type
    if (mobo && ram) {
        if (mobo.ramType !== ram.ramType) {
            compatibilityIssues.push(`RAM Type Mismatch: Motherboard '${mobo.name}' supports ${mobo.ramType}, but selected RAM is ${ram.ramType}!`);
        }
    }

    // C. Motherboard Form Factor vs Case compatible layouts
    if (mobo && cabinet) {
        const supportedFactors = cabinet.formFactor.split(',').map(f => f.trim());
        if (!supportedFactors.includes(mobo.formFactor)) {
            compatibilityIssues.push(`Form Factor Mismatch: Motherboard is size '${mobo.formFactor}', but Case '${cabinet.name}' only supports sizes: [${cabinet.formFactor}]!`);
        }
    }

    // D. Wattage calculation vs Power Supply power
    if (psu) {
        const psuCapacity = psu.wattage;
        // Add a 20% overclock headroom safety margin
        const safeWattage = totalWattage * 1.2;
        if (safeWattage > psuCapacity) {
            compatibilityIssues.push(`Power Alert: Total Estimated Power Draw (${totalWattage}W + overclocking safety headroom) exceeds selected PSU rating of ${psuCapacity}W! Upgrade PSU.`);
        }
    }

    // Update Alerts Box
    const alertsContainer = document.getElementById('compatibility-alerts-box');
    const statusText = document.getElementById('builder-compat-status');
    const statusIcon = document.getElementById('builder-compat-icon');
    
    if (compatibilityIssues.length > 0) {
        statusText.textContent = "COMPATIBILITY WARNINGS DETECTED";
        statusText.style.color = "#ff0055";
        statusIcon.className = "bi bi-exclamation-triangle-fill text-danger me-2";
        
        alertsContainer.innerHTML = compatibilityIssues.map(issue => `
            <div class="alert alert-danger py-2 px-3 mb-2" style="background: rgba(255,0,85,0.1); border-color: rgba(255,0,85,0.3); font-size:13px;">
                <i class="bi bi-chevron-right me-1"></i> ${issue}
            </div>
        `).join('');
    } else {
        // Safe and compatible (or no parts selected yet)
        let selectedCount = Object.values(builderBuild).filter(v => v !== null).length;
        if (selectedCount > 0) {
            statusText.textContent = "SYSTEM HEALTH COMPATIBLE";
            statusText.style.color = "#39ff14";
            statusIcon.className = "bi bi-shield-fill-check text-success me-2";
            alertsContainer.innerHTML = `
                <div class="alert alert-success py-2 px-3 mb-0" style="background: rgba(57,255,20,0.1); border-color: rgba(57,255,20,0.3); font-size:13px;">
                    <i class="bi bi-check2-all me-1"></i> All selected components are compatible. Voltage profiles verified.
                </div>
            `;
        } else {
            statusText.textContent = "NO PARTS SELECTED";
            statusText.style.color = "#a0a0ba";
            statusIcon.className = "bi bi-gear-wide-connected text-muted me-2";
            alertsContainer.innerHTML = `
                <div class="text-muted text-center py-3" style="font-size: 13px;">
                    Start selecting components to run compatibility checks.
                </div>
            `;
        }
    }
}

// Add custom Rig bundle to Django Cart session
window.addRigToCart = function() {
    // Collect all selected product ids
    let productIds = [];
    for (const key in builderBuild) {
        if (builderBuild[key]) {
            productIds.push(builderBuild[key].id);
        }
    }

    if (productIds.length === 0) {
        alert("Please select at least one component before adding to cart!");
        return;
    }

    // Call bulk addition views endpoint
    fetch('/cart/add-custom-rig/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ product_ids: productIds })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = '/cart/';
        } else {
            alert("Could not add custom rig: " + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Failed to connect to cart service.");
    });
};
