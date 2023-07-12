const content = document.getElementById('content')
const base_url = "http://localhost:8000"
var url = ""
var pagination = 2


const paginator_request = (page) => {
    const icon_div = document.querySelector("#paginator_loading_icon")
    url = base_url + "/blog/poetrypaginationdone/" + page +"/"
    fetch(url)
    .then(response => response.json())
    .then(json => {
        if(json['not_done']) {
            // console.log(json['not_done'])
        } else {
            // console.log(json['not_done'])
            icon_div.innerHTML = "<i class='fa-solid fa-check fa-beat-fade' style='font-size: small;'></i>"
        }
    })
}

const post_likes_handler = (span) => {
    const post_like_buttons = span.getElementsByClassName("post_like_button")
    for(let i=0; i<post_like_buttons.length; i++) {
        url = base_url + post_like_buttons[i].getAttribute("link")
        fetch(url)
        .then(response => response.json())
        .then(json => {
            if(json['liked']) {
                post_like_buttons[i].style.color = "red"
            }
        })
    }
}

window.onscroll = function(ev) {
    if ((window.innerHeight + Math.round(window.scrollY)) >= document.body.offsetHeight) {
        const icon_div = document.querySelector("#paginator_loading_icon")
        if(icon_div) {
            console.log(pagination)
            url = base_url + "/blog/poetrypaginationdone/1/"
            fetch(url)
            .then(response => response.json())
            .then(json => {
                if(json['page_count']>=pagination) {
                    const parent = icon_div.parentElement
                    url = base_url + icon_div.getAttribute('href') + "?page=" + (pagination)
                    fetch(url)
                    .then(response => response.text())
                    .then(text => {
                        const node = document.createElement("span")
                        node.innerHTML = text
                        parent.insertBefore(node, icon_div)
                        post_likes_handler(node)
                        paginator_request(pagination)  
                        pagination = pagination + 1
                    })
                }
            })
        }
    }
};

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
        url = base_url + element.getAttribute('href') + "?page=1"
        fetch(url)
        .then(response => response.text())
        .then(text => {
            content.innerHTML = text
            post_likes_handler(content)
            paginator_request(1)
        })
        pagination = 2
    }

    // Post Detail Page
    if(element.classList.contains("post_detail")) {
        e.preventDefault()
        url = base_url + element.getAttribute('href')
        fetch(url)
        .then(response => response.text())
        .then(text => {
            content.innerHTML = text
            post_likes_handler(content)
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
            console.log(span)
            content.insertBefore(span, content.firstElementChild)
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

    if(element.classList.contains("comment_post_detail_form")) {
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
            const likes_count = parent_element.querySelector(".likes-count")
            const pointer = parent_element.querySelector(".pointer_comment_post")
            node.innerHTML = text
            parent_element.insertBefore(node, pointer.nextElementSibling)
            element.querySelector("textarea").value = ""
            element.querySelector(".comment-post-button").style.display = "none"
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