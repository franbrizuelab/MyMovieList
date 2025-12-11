function showTab(tabIndex) {
    const tabs = document.querySelectorAll('.tab-content');
    const tabButtons = document.querySelectorAll('.tab');
    let currentActiveTab = document.querySelector('.tab-content.active');

    if (currentActiveTab) {
        // do nothing if the same tab is clicked
        if (currentActiveTab === tabs[tabIndex]) {
            return;
        }
        currentActiveTab.classList.remove('active');
    }

    // Deactivate all tab buttons
    tabButtons.forEach(button => button.classList.remove('active'));

    function showNewTab() {
        if (currentActiveTab) {
            currentActiveTab.style.display = 'none';
        }
        const newTab = tabs[tabIndex];
        newTab.style.display = 'block';
        // Delay to allow display property to take effect before adding class for transition
        setTimeout(() => {
            newTab.classList.add('active');
            tabButtons[tabIndex].classList.add('active');
        }, 20);
    }
    
    if (currentActiveTab) {
        // Wait for fade out transition to finish
        setTimeout(showNewTab, 300);
    } else {
        showNewTab();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    showTab(0); // Show the first tab by default
});