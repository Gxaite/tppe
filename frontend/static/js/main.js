// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Confirm delete actions
function confirmDelete(message) {
    return confirm(message || 'Tem certeza que deseja excluir este item?');
}

// Format currency inputs
function formatCurrency(input) {
    let value = input.value.replace(/\D/g, '');
    value = (parseInt(value) / 100).toFixed(2);
    input.value = value;
}

// Validate form before submit
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return false;
    }
    return true;
}

// Dynamic form helpers
function updateServiceTotal() {
    const valorMaoObra = parseFloat(document.getElementById('valor_mao_obra')?.value || 0);
    const valorPecas = parseFloat(document.getElementById('valor_pecas')?.value || 0);
    const totalElement = document.getElementById('valor_total');

    if (totalElement) {
        const total = valorMaoObra + valorPecas;
        totalElement.value = total.toFixed(2);
    }
}

// Status color mapping
const statusColors = {
    'aguardando_orcamento': 'secondary',
    'orcamento_aprovado': 'info',
    'em_andamento': 'warning',
    'concluido': 'success',
    'cancelado': 'danger'
};

function getStatusBadgeClass(status) {
    return `badge bg-${statusColors[status] || 'secondary'}`;
}
