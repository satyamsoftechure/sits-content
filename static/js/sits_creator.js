function downloadImage(url, filename) {
    fetch(url)
        .then((response) => {
            if (!response.ok) {
                throw new Error('No image available');
            }
            return response.blob();
        })
        .then((blob) => {
            const objectUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = objectUrl;
            a.download = filename + '.jpg';
            a.click();
            URL.revokeObjectURL(objectUrl); // Clean up the object URL after downloading
        })
        .catch((error) => {
            console.log("No image available");
        });
}


$(document).ready(function () {
    $('#save_draft_form').submit(function (event) {
        event.preventDefault()
        event.stopImmediatePropagation()
        var formData = $(this).serialize()
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formData,
            dataType: 'json',
            success: function (data) {
                var tooltip = $('#tooltip_success')
                var message = $('#message')
                message.html(data.message)
                tooltip.addClass('show')
                setTimeout(function () {
                    tooltip.removeClass('show')
                }, 2000)
            }
        })
        return false
    })
})

$(document).ready(function () {
    // Function to get CSRF token
    function getCSRFToken() {
        return $('[name=csrfmiddlewaretoken]').val();
    }

    // Set up AJAX to always send CSRF token
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
            }
        }
    });

    function closeModalProperly() {
        $('#loginModal').modal('hide');
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();
    }

    $(document).ready(function () {
        // Handle login form submission
        $('#inside_login_form').submit(function (event) {
            event.preventDefault()
            var formData = $(this).serialize()
            $.ajax({
                type: 'POST',
                url: $(this).attr('action'),
                data: formData,
                dataType: 'json',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                success: function (data) {
                    if (data.success) {
                        closeModalProperly();

                        $('.anchor-button').html(`
                  <a href="{% url 'generate_blog' %}" class="btn mt-3"><span class="remove_span_text">New Blog</span><i class="fa-solid fa-blog"></i></a>
                  <button type="submit" form="save_draft_form" class="form_button mt-3" id="save_draft_btn"><span class="remove_span_text">Save Draft</span><i class="fa-regular fa-bookmark"></i></button>
                  <button type="submit" form="regenerate-form" class="form_button mt-3" id="Regenerate-btn"><span class="remove_span_text">Regenerate</span><i class="fa-solid fa-arrows-rotate"></i></button>
                `)
                        $('.change_dropdown').html(`
                  <li>
                    <span>Profile : (${data.username})</span>
                  </li>
                  <li>
                    <a href="/my_drafts">Saved Drafts</a>
                  </li>
                  <li>
                    <a href="/logout">Logout</a>
                  </li>
                `)

                        // Show a success message
                        $('#message').text('Logged in successfully. You can now save your draft.')
                        $('#tooltip_success').show().delay(3000).fadeOut()
                    } else {
                        // Show an error message
                        $('#message-error').text('Login failed. Please try again.')
                        $('#tooltip_error').show().delay(3000).fadeOut()
                    }
                },
                error: function () {
                    $('#message-error').text('The username or password you entered is incorrect.')
                    $('#tooltip_error').show().delay(3000).fadeOut()
                }
            })
        })
    })


    $(document).ready(function () {

        $('#showRegisterForm').click(function () {
            $('#loginForm').hide();
            $('#registerForm').show();
        });

        // Show the login form when "Already have an account? Login" button is clicked
        $('#showLoginForm').click(function () {
            $('#loginForm').show();
            $('#registerForm').hide();
        });

        $('#inside_register_form').submit(function (event) {
            event.preventDefault()
            var formData = $(this).serialize()
            $.ajax({
                type: 'POST',
                url: $(this).attr('action'),
                data: formData,
                dataType: 'json',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                success: function (data) {
                    if (data.message === 'Register successfully !') {

                        $('#message').text('Register successfully. Now you can Login.')
                        $('#tooltip_success').show().delay(3000).fadeOut()

                        $('#registerForm').hide()
                        $('#loginForm').show()
                    } else {
                        // Show an error message
                        $('#message-error').text(data.message)
                        $('#tooltip_error').show().delay(3000).fadeOut()
                    }
                },
                error: function () {
                    $('#message-error').text('An error occurred')
                    $('#tooltip_error').show().delay(3000).fadeOut()
                }
            })
        })
    })

    // Handle save draft button click
    $(document).on('click', 'button[form="save_draft_form"]', function (event) {
        event.preventDefault()
        var formData = $('#save_draft_form').serialize();
        formData.csrfmiddlewaretoken = getCSRFToken();
        $.ajax({
            type: 'POST',
            url: $('#save_draft_form').attr('action'),
            data: formData,
            dataType: 'json',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function (data) {
                $('#message').text(data.message)
                $('#tooltip_success').show().delay(3000).fadeOut()
                $('#save_draft_btn').html('<span class="remove_span_text">saved</span> <i class="fa-solid fa-bookmark"></i>');
            },
            error: function () {
                $('#message').text('An error occurred while saving the draft.')
                $('#tooltip_error').show().delay(3000).fadeOut()
            }
        })
    })
})


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function confirmDelete(draftId) {
    Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/delete_draft/${draftId}/`,
                type: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                success: function (response) {
                    if (response.status === 'success') {
                        Swal.fire({
                            title: 'Deleted!',
                            text: 'Your draft has been deleted.',
                            icon: 'success',
                            confirmButtonText: 'OK'
                        }).then((result) => {
                            if (result.isConfirmed) {
                                location.reload(); // Reload the page
                            }
                        });
                    } else {
                        Swal.fire(
                            'Error!',
                            'There was a problem deleting the draft.',
                            'error'
                        )
                    }
                },
                error: function () {
                    Swal.fire(
                        'Error!',
                        'There was a problem deleting the draft.',
                        'error'
                    )
                }
            });
        }
    })
}