{% autoescape true %}

var root;
root = this;
$(function() {
    var f, c, b, e, a, d;
    $("#password_box").on('click', '#login_password_button', function (j) {
        var h, i, g;
        i = $("#login_new_password").val();
        g = $("#login_new_password2").val();
        if (i === g) {
            $.ajax({
                method: "post",
                url: "{{url_for('json.change_password')}}",
                data: $("#password_form").serialize(),
                async: true,
                success: function () {
                    indicateSuccess("{{_('Settings saved')}}");
                }
            })
            .fail(function() {
                indicateFail("{{_('Error occurred')}}");
            });
            $('#password_box').modal('hide');
        } else {
            alert("{{_('Passwords did not match.')}}")
        }
        j.stopPropagation();
        j.preventDefault();
    });
    $(".is_admin").each(function () {
        let userName = $(this).attr("name").split("|")[0];
        $(this).bind("change", {userName: userName}, function (event) {
            let checked = $(this).is(":checked");
            let permsList = $("#" + userName + "\\|perms");
            permsList.attr('disabled', checked);
            if (checked) {
                permsList.val([]);
            }
        });
    });
    $(".change_password").each(function () {
        var userName = $(this).attr("id").split("|")[1];
        $(this).bind("click",{userName:userName}, function(g) {
            $("#password_form").trigger("reset");
            $("#password_box #user_login").val(userName);
        });
    });
    $('#password_box').on('shown.bs.modal', function () {
        $('#login_current_password').focus();
    });
    $("#user_add").click(function (event) {
        $("#user_add_form").trigger("reset");
    });
    $("#new_role").change(function (event) {
        var checked = $(this).is(":checked");
        var permsList = $("#new_perms");
        permsList.attr('disabled', checked);
        if (checked) {
            permsList.val([]);
        }
    });
    $("#new_user_button").click(function (event) {
        $(this).attr('disabled', true);
        var $userForm = $("#user_add_form");
        var $userName = $("#new_user");
        if ($userName.val().trim() === "") {
            alert("{{_('Username must be filled out')}}");
        } else {
            $userName.val($userName.val().trim());
            var passwd = $("#new_password").val();
            var passwdConfirm = $("#new_password2").val();
            if (passwd === passwdConfirm) {
                $.ajax({
                    method: "post",
                    url: "{{url_for('json.add_user')}}",
                    async: true,
                    data: $userForm.serialize(),
                    success: function () {
                        window.location.assign(window.location.href);
                    }
                })
                .fail(function () {
                    indicateFail("{{_('Error occurred')}}");
                });
                $('#user_box').modal('hide');
            } else {
                alert("{{_('Passwords did not match.')}}")
            }
        }
        $(this).attr('disabled', false);
        event.stopPropagation();
        event.preventDefault();
    });
    $("#quit_box").on('click', '#quit_button', function () {
        $.get("{{url_for('api.rpc', func='kill')}}", function() {
            $('#quit_box').modal('hide');
            $('#content').addClass("hidden");
            $('#shutdown_msg').removeClass("hidden");
        })
        .fail(function () {
            indicateFail("{{_('Error occurred')}}");
        });
    });

    $("#restart_box").on('click', '#restart_button', function () {
        $.get("{{url_for('api.rpc', func='restart')}}", function() {
            $('#restart_box').modal('hide');
            $('#content').addClass("hidden");
            $('#restart_msg').removeClass("hidden");
            setTimeout(function() {
                window.location = "{{url_for('app.dashboard')}}";
            }, 10000);
        })
        .fail(function () {
            indicateFail("{{_('Error occurred')}}");
        });
    });

});

{% endautoescape %}
