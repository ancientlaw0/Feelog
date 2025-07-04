
// Infinite scroll using IntersectionObserver.
// Observes a special element (#load-more-trigger) that sits at the end of the list.
// When it enters the viewport, fetches the next batch via AJAX and appends to the list.
// Reattaches itself to the new trigger if more content exists.
// Also updates timestamps using moment.js (if available).

document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const trigger = entry.target;
                const nextUrl = trigger.dataset.nextUrl;

                if (nextUrl) {
                    fetch(nextUrl, {
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.text())
                    .then(data => {
                       

                        trigger.remove();

                        
                        const parentList = document.querySelector('#post-list') || document.querySelector('#comment-list') || document.querySelector('#messages-list') || document.querySelector('#users-list');
                        if (parentList) {
                            parentList.insertAdjacentHTML('beforeend', data);
                        }

                        
                        if (window.moment) {  // Refresh readable timestamps after new content is loaded.
                            document.querySelectorAll('time.timestamp').forEach(el => {
                                el.textContent = moment(el.getAttribute('datetime')).fromNow();
                            });
                        }

                       
                        const newTrigger = document.querySelector('#load-more-trigger');
                        if (newTrigger) {
                            observer.observe(newTrigger);
                        }
                        
                    })
                    .catch(error => console.error('Error fetching content:', error));
                }
            }
        });
    });


    const trigger = document.querySelector('#load-more-trigger');
    if (trigger) {
        observer.observe(trigger);
    }
});
