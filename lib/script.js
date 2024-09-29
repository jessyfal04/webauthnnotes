async function register() {
    let username = $("#username").val();

    $.ajax({
        url: "/api/webauthnnotes/webauthn/register/begin",
		type: 'POST',
		dataType : "json",
		contentType: 'application/json',
		data: JSON.stringify({ username: username })
    })
    .done(async function (response) {
        if (response.code === "success") {
            // Options for creating a new credential
            const publicKeyCredentialCreationOptions = JSON.parse(response.data);
            
            publicKeyCredentialCreationOptions.challenge = base64URLToBuffer(publicKeyCredentialCreationOptions.challenge);
            publicKeyCredentialCreationOptions.user.id = base64URLToBuffer(publicKeyCredentialCreationOptions.user.id);

            let credential;
            // Register the credential
            try {
                credential = publicKeyCredentialToBase64(await navigator.credentials.create({
                    publicKey: publicKeyCredentialCreationOptions
                }))
            } catch (error) {
                console.log(error);
                setMessages("danger", "Error creating credential");
                return;
            }
            

            // Send the credential to the server
            $.ajax({
                url: "/api/webauthnnotes/webauthn/register/complete",
                type: 'POST',
                dataType : "json",
                contentType: 'application/json',
                data: JSON.stringify({ credential: credential, username: username})
            })
            .done(async function (response) {
                if (response.code === "success") {
                    setMessages("success", response.message);
                    whoami();
                } else {
                    setMessages("danger", response.message);
                }
            })
            .fail(function (e) {
                console.log(e);
            })

        } else {
            setMessages("danger", response.message);
        }
    })
    .fail(function (e) {
		console.log(e);
	});
}

async function login() {
    let username = $("#username").val();

    $.ajax({
        url: "/api/webauthnnotes/webauthn/authenticate/begin",
        type: 'POST',
        dataType : "json",
        contentType: 'application/json',
        data: JSON.stringify({ username: username })
    })
    .done(async function (response) {
        if (response.code === "success") {
            // Options for creating a new credential
            const publicKeyCredentialRequestOptions = JSON.parse(response.data);
            
            publicKeyCredentialRequestOptions.challenge = base64URLToBuffer(publicKeyCredentialRequestOptions.challenge);
            publicKeyCredentialRequestOptions.allowCredentials.forEach(function (listItem) {
                listItem.id = base64URLToBuffer(listItem.id);
            });

            console.log(publicKeyCredentialRequestOptions);

            // Register the credential
            let credential;

            try {
                credential = publicKeyCredentialToBase64(await navigator.credentials.get({
                    publicKey: publicKeyCredentialRequestOptions
                }));
            } catch (error) {
                console.log(error);
                setMessages("danger", "Error creating credential");
                return
                
            }

            // Send the credential to the server
            $.ajax({
                url: "/api/webauthnnotes/webauthn/authenticate/complete",
                type: 'POST',
                dataType : "json",
                contentType: 'application/json',
                data: JSON.stringify({ credential: credential, username: username})
            })
            .done(async function (response) {
                if (response.code === "success") {
                    setMessages("success", response.message);
                    whoami();
                } else {
                    setMessages("danger", response.message);
                }
            })
            .fail(function (e) {
                console.log(e);
            })
        } else {
            setMessages("danger", response.message);
        }
    })
    .fail(function (e) {
        console.log(e);
    }).then(function() {
        $("#register-button").removeClass("is-loading");
    }); 
}

async function loginOrRegister() {
    // user exists
    let username = $("#username").val();

    $.ajax({
        url: "/api/webauthnnotes/user-exists",
        type: 'POST',
        dataType : "json",
        contentType: 'application/json',
        data: JSON.stringify({ username: username })
    }).done(async function (response) {
        if (response.code === "success") {
            $("#login-button").prop("disabled", !response.data.exists);
            $("#register-button").prop("disabled", response.data.exists);
        } else {
            setMessages("danger", response.message);
        }
    }).fail(function (e) {
        console.log(e);
    });
}

async function logout() {
    $.ajax({
        url: "/api/webauthnnotes/logout",
        type: 'POST',
        dataType : "json",
        contentType: 'application/json',
    })
    .done(async function (response) {
        if (response.code === "success") {
            whoami();
        } else {
            setMessages("danger", response.message);
        }
    })
    .fail(function (e) {
        console.log(e);
    })
}

async function whoami() {
    $.ajax({
        url: "/api/webauthnnotes/whoami",
        type: 'GET',
        dataType : "json",
        contentType: 'application/json',
    })
    .done(async function (response) {
        if (response.code === "success") {
            let username = response.data.username;

            $("#username").val(username == null ? "" : username);
            $("#username").prop("disabled", username != null);

            $("#logout-button").css("display", username == null ? "none" : "initial");
            $("#login-button").css("display", username == null ? "initial" : "none");
            $("#register-button").css("display", username == null ? "initial" : "none");

            username == null ? null : disableLoginRegister();
            username == null ? disableNote() : getNote();
            
            
        } else {
            setMessages("danger", response.message);
        }
    })
    .fail(function (e) {
        console.log(e);
    })
}

function disableLoginRegister() {
    $("#login-button").prop("disabled", true);
    $("#register-button").prop("disabled", true);
}

whoami();

// Notes
async function getNote() {
    $.ajax({
        url: "/api/webauthnnotes/note",
        type: 'GET',
        dataType : "json",
        contentType: 'application/json',
    })
    .done(async function (response) {
        if (response.code === "success") {
            let note = response.data.note;
            $("#noteTextArea").val(note);
            $("#noteTextArea").prop("disabled", false);
            $("#noteTextArea").removeClass("is-danger");
            $("#noteTextArea").addClass("is-success");
        } else {
            setMessages("danger", response.message);
        }
    })
    .fail(function (e) {
        console.log(e);
    })
}

async function noteChange() {
    let note = $("#noteTextArea").val();

    $.ajax({
        url: "/api/webauthnnotes/note",
        type: 'POST',
        dataType : "json",
        contentType: 'application/json',
        data: JSON.stringify({ note: note })
    })
    .done(async function (response) {
        if (response.code === "success") {
            $("#noteTextArea").removeClass("is-danger");
            $("#noteTextArea").addClass("is-success");
        } else {
            setMessages("danger", response.message);
            noteInput();
        }
    })
    .fail(function (e) {
        console.log(e);
        noteInput();
    })
}

function disableNote() {
    $("#noteTextArea").prop("disabled", true);
    $("#noteTextArea").val("");
    $("#noteTextArea").removeClass("is-success");
    $("#noteTextArea").removeClass("is-danger");
}

function noteInput() {
    $("#noteTextArea").removeClass("is-success");
    $("#noteTextArea").addClass("is-danger");
}

// Functions
function base64URLToBuffer(base64URL) {
    const base64 = base64URL.replace(/-/g, '+').replace(/_/g, '/');
    const padLen = (4 - (base64.length % 4)) % 4;
    return Uint8Array.from(atob(base64.padEnd(base64.length + padLen, '=')), c => c.charCodeAt(0));
}

function bufferToBase64URL(buffer) {
    const bytes = new Uint8Array(buffer);
    let string = '';
    bytes.forEach(b => string += String.fromCharCode(b));

    const base64 = btoa(string);
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

function publicKeyCredentialToBase64(credential) {
    return {
        id: credential.id,
        rawId: credential.rawId ? bufferToBase64URL(credential.rawId) : "",
        type: credential.type,
        response: {
            clientDataJSON: credential.response.clientDataJSON ? bufferToBase64URL(credential.response.clientDataJSON) : "",
            authenticatorData: credential.response.authenticatorData ? bufferToBase64URL(credential.response.authenticatorData) : "",
            attestationObject: credential.response.attestationObject ? bufferToBase64URL(credential.response.attestationObject) : null,
            signature: credential.response.signature ? bufferToBase64URL(credential.response.signature) : "",
            userHandle: credential.response.userHandle ? bufferToBase64URL(credential.response.userHandle) : ""
        }
    };
}

function setMessages(type, text) {
	$("#messages").html("");
	// in click one 
	if (text != null) {
        var notification = $(`
            <div class="notification is-${type} mx-6" style="display: none;">
				<button class="delete" onclick="$(this).parent().remove();"></button>
				${text}
            </div>
        `);
        
        // Append notification to messages container
        $("#messages").append(notification);

        // Fade in the notification
        notification.fadeIn();

        // Set timeout to fade out and remove the notification after 5 seconds
        setTimeout(function() {
            notification.fadeOut(function() {
                $(this).remove();
            });
        }, 5000);
    }
}