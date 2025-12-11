function showTab(tabIndex) {
    const tabs = document.querySelectorAll('.tab-content');
    const tabButtons = document.querySelectorAll('.tab');
    tabs.forEach((tab, index) => {
        tab.classList.remove('active');
        tabButtons[index].classList.remove('active');
        if (index === tabIndex) {
            tab.classList.add('active');
            tabButtons[index].classList.add('active');
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    showTab(0); // Show the first tab by default
});