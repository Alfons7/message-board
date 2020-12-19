function fav_change(action, post_id) {
    const url = `${window.location.origin}/${action}`;
    const formData = new FormData();
    formData.append('post_id', post_id);
    const request = new Request(url);
    fetch(request, {
        method: 'POST', 
        mode: 'same-origin',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let fav_heart = document.querySelector('#fav_' + data.post_id);
            let unfav_heart = document.querySelector('#unfav_' + data.post_id);
            let likes = document.querySelector('#likes_' + data.post_id);
            if (data.action === 'fav') {
                fav_heart.style.display = "flex";
                unfav_heart.style.display = "none";
            } else {
                fav_heart.style.display = "none";
                unfav_heart.style.display = "flex";
            }
            likes.textContent = data.likes;
        }
    });
}