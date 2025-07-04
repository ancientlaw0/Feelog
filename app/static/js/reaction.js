// Handle reaction button clicks cheer/boo (likes/dislikes) via event delegation.

document.addEventListener('click', function(e) {
   
    let reactionBtn = e.target.closest('.reaction-btn');
    
    if (reactionBtn) {
        const postId = reactionBtn.dataset.postId;
        const action = reactionBtn.dataset.action;

        fetch('/react', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ post_id: postId, action: action })
        })
        .then(res => res.json())
        .then(data => {
           
            document.getElementById('cheers-' + postId).textContent = data.cheers;
            document.getElementById('boos-' + postId).textContent = data.boos;
            
            
            const likeBtn = document.querySelector(`[data-post-id="${postId}"][data-action="cheer"]`);
            const dislikeBtn = document.querySelector(`[data-post-id="${postId}"][data-action="boo"]`);
            
            
            likeBtn.classList.remove('active');
            dislikeBtn.classList.remove('active');
            
           
            if (data.user_reaction === 'cheer') {
                likeBtn.classList.add('active');
            } else if (data.user_reaction === 'boo') {
                dislikeBtn.classList.add('active');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});