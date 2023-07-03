const content = document.getElementById('content')
const base_url = "http://localhost:8000"
var url = ""

//  CLICK EVENT
document.addEventListener('click', function(e) {

    const element = e.target
    // e.preventDefault()
    // console.log(element)

    // Profile Page Button
    if(element.classList.contains("profile_page")) {
        e.preventDefault()
        url = base_url + element.getAttribute('href')
        fetch(url)
        .then(response => response.text())
        .then(text => {
            content.innerHTML = text
        })
    }

    // Home Page
    if(element.classList.contains("home_page")) {
        e.preventDefault()
        url = base_url + element.getAttribute('href')
        fetch(url)
        .then(response => response.text())
        .then(text => {
            content.innerHTML = text
        })
    }

    // Post Detail Page
    if(element.classList.contains("post_detail")) {
        e.preventDefault()
        url = base_url + element.getAttribute('href')
        console.log(url)
        fetch(url)
        .then(response => response.text())
        .then(text => {
            content.innerHTML = text
        })
    }

    // Post Create Page
    if(element.classList.contains("post_create_page")) {
        e.preventDefault()
        const parent_element = element.closest("li")
        const popup = parent_element.querySelector("dialog")
        url = base_url + element.getAttribute('href')
        fetch(url)
        .then(response => response.text())
        .then(text => {
            popup.innerHTML = text
            popup.showModal()
        })
    }

    // Public Chat Page
    if(element.classList.contains("public_chat_page")) {
        e.preventDefault()
        url = base_url + element.getAttribute('href')
        fetch(url)
        .then(response => response.text())
        .then(text => {
            content.innerHTML = text
            document.querySelector('#room-name-input').focus();
            document.querySelector('#room-name-input').onkeyup = function(e) {
                if (e.keyCode === 13) {  // enter, return
                    document.querySelector('#room-name-submit').click();
                }
            };

            document.querySelector('#room-name-submit').onclick = function(e) {
                var roomName = document.querySelector('#room-name-input').value;
                url =  base_url + '/chat/' + roomName + '/'
                fetch(url)
                .then(response => response.text())
                .then(text => {
                    content.innerHTML = text

                    const roomName = JSON.parse(document.getElementById('room-name').textContent);
                    
                    const chatSocket = new WebSocket(
                        'ws://'
                        + window.location.host
                        + '/ws/chat/'
                        + roomName
                        + '/'
                    );

                    chatSocket.onmessage = function(e) {
                        const data = JSON.parse(e.data);
                        document.querySelector('#chat-log').value += (data.message + '\n');
                    };

                    chatSocket.onclose = function(e) {
                        console.error('Chat socket closed unexpectedly');
                    };

                    document.querySelector('#chat-message-input').focus();
                    document.querySelector('#chat-message-input').onkeyup = function(e) {
                        if (e.keyCode === 13) {  // enter, return
                            document.querySelector('#chat-message-submit').click();
                        }
                    };

                    document.querySelector('#chat-message-submit').onclick = function(e) {
                        const messageInputDom = document.querySelector('#chat-message-input');
                        const message = messageInputDom.value;
                        chatSocket.send(JSON.stringify({
                            'message': message
                        }));
                        messageInputDom.value = '';
                    };
                })
            };
        })
    }

    // Post Like Button
    if(element.classList.contains("post_like_button")) {
        e.preventDefault()
        url = base_url + element.getAttribute('href')
        fetch(url)
        .then(response => response.json())
        .then(text => {
            element.closest(".like-comment").lastElementChild.innerHTML = text['likes'] + " Likes , " + text['comments'] + " Comments"
            if(text['liked']) {
                element.closest(".like-comment").firstElementChild.style.color = "red"
            } else {
                element.closest(".like-comment").firstElementChild.style.color = "black"
            }
        })
    }

    // Post delete Button
    if(element.classList.contains("post-delete-button")) {
        e.preventDefault()
        url = base_url + element.getAttribute('href')
        fetch(url)
        .then(response => response.json())
        .then(text => {
            console.log(text['message'])
            const parent_element = element.closest(".post-class")
            parent_element.remove()
        })
    }

    // Post update Button
    if(element.classList.contains("post-update-button")) {
        e.preventDefault()
        url = base_url + element.getAttribute('href')
        fetch(url)
        .then(response => response.text())
        .then(text => {
            const parent_element = element.closest('.post-class')
            const popup = parent_element.querySelector('.post-update-popup')
            popup.innerHTML = text
            popup.showModal()
        })
    }
})

// SUBMIT EVENT
document.addEventListener('submit', function(e) {

    const element = e.target
    // e.preventDefault()
    // console.log(element)

    if(element.classList.contains("post_create_form")) {
        e.preventDefault();
        const first_post = content.querySelector(".post-class")[0]
        url = base_url + element.getAttribute('action')
        const formData = new FormData(element);
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(text => {
            const span = document.createElement("span")
            span.innerHTML = text
            content.insertBefore(span, content.firstChild)
            document.querySelector(".post-add-popup").close()
        })
        .catch(error => {
            console.error('Error:', error);
        })
    }

    if(element.classList.contains("post-update-form")) {
        e.preventDefault();
        const dialog = element.closest('dialog')
        const element_parent = element.closest('.post-class')
        url = base_url + element.getAttribute('action')
        const formData = new FormData(element);
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(text => {
            dialog.close()
            element_parent.querySelector('.post-content-span').innerHTML = text
        })
        .catch(error => {
            console.error('Error:', error);
        })
    }

    if(element.classList.contains("comment_post_form")) {
        e.preventDefault()
        url = base_url + element.getAttribute('action')
        const formData = new FormData(element);
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(text => {
            const node = document.createElement("span")
            const parent_element = element.closest("div")
            node.innerHTML = text
            parent_element.insertBefore(node, element)
            element.querySelector("textarea").value = ""
            element.querySelector(".comment-post-button").style.display = "none"
            const likes_count = parent_element.querySelector(".likes-count")
            url = base_url + likes_count.getAttribute("href")
            fetch(url)
            .then(response => response.json())
            .then(text => {
                likes_count.innerHTML = text['likes'] + " Likes , " + text['comments'] + " Comments"
            })
        })
    }
})

function auto_grow(element) {
    element.style.height = "5px";
    element.style.height = (element.scrollHeight) + "px";
    if(element.value != "") {
        element.nextElementSibling.style.display = "block"
    } else {
        element.nextElementSibling.style.display = "none"
    }
}