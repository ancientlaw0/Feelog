document.addEventListener('click', function (e) {
  const deleteBtn = e.target.closest('.delete-btn'); // Uses `closest()` to handle clicks on nested elements (icons, spans inside button)
  if (!deleteBtn) return;

  const postId = deleteBtn.dataset.id;
  if (!postId) return;

  if (!confirm('Are you sure you want to delete this post?')) return;

  fetch(`/delete_post/${postId}`, {
    method: 'POST'
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert("Post deleted successfully.");
      const postElement = deleteBtn.closest('.post');
      if (postElement) postElement.remove();
    } else {
      alert("Delete failed: " + (data.error || "Unknown error."));
      console.error('Deletion failed:', data);
    }
  })
  .catch(err => {
    alert("Server error.");
    console.error('Fetch error:', err);
  });
});
