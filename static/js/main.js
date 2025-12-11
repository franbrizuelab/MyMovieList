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

    // FEATURE: Cascade scrolling for movie items
    const movieItems = document.querySelectorAll('.movie-item.hidden');
    if (movieItems.length > 0 && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    entry.target.classList.remove('hidden'); // Remove hidden class once visible
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1 // Trigger when 10% of the item is visible
        });

        movieItems.forEach((item) => observer.observe(item));
    }
});