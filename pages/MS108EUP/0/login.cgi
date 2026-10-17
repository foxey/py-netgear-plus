<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="pragma" content="no-cache">
<title>NETGEAR MS108EUP</title>
<link rel="stylesheet" href="/loginPage.css">
<script src="/jquery.min.js"></script>
<script src="/jquery-migrate.min.js"></script>
<script src="/jquery.md5.js"></script>
<script src="/loginPage.js"></script>
</head>
<body>
<div class="login-container">
    <div class="logo">
        <a href="https://www.netgear.com" target="_blank">
            <img src="/images/netgear_logo.png" alt="NETGEAR">
        </a>
    </div>
    <div class="model-name">MS108EUP</div>
    <form method="post" action="/redirect.html" id="loginForm">
        <input type="hidden" id="rand" name="rand" value="514134199">
        <input type="hidden" name="LoginPassword" id="submitPwd" value="">
        <div class="password-field">
            <label for="Password">Password</label>
            <input type="password" id="Password" name="Password" maxlength="20" autocomplete="off">
            <span class="toggle-password"></span>
        </div>
        <div id="loginPageErrorMsg" class="error-msg"></div>
        <button type="button" onclick="submitLogin()">Login</button>
    </form>
    <div class="first-time-info">
        First time accessing the switch? Check the physical label on the device for the default password.
    </div>
</div>
<script>
function submitLogin() {
    var password = document.getElementById('Password').value;
    var rand = document.getElementById('rand').value;
    // Password is hashed with rand before submission
    var hashedPwd = $.md5(password + rand);
    document.getElementById('submitPwd').value = hashedPwd;
    document.getElementById('loginForm').submit();
}
function onEnterSub(e) {
    if (e.keyCode === 13) {
        submitLogin();
    }
}
document.getElementById('Password').addEventListener('keypress', onEnterSub);
</script>
</body>
</html>
