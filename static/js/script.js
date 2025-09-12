// Basic form validation for date/time inputs
document.addEventListener('DOMContentLoaded', function() {
    // For schedule form
    const scheduleForm = document.getElementById('session_date');
    if (scheduleForm) {
        scheduleForm.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (selectedDate < today) {
                alert('Cannot schedule sessions in the past');
                this.value = '';
            }
        });
    }
    
    // For payment form
    const paymentForm = document.getElementById('amount');
    if (paymentForm) {
        paymentForm.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    }
});