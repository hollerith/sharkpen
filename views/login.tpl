% include('header.tpl', title='Sh4rkP3n - Login')

<body class="h-vh-100 bg-brandColor2">
    % include('appbar.tpl')
    <style>
        .login-form {
            width: 350px;
            height: auto;
            top: 50%;
            margin-top: -160px;
        }
    </style>
    <form class="login-form bg-white p-6 mx-auto border bd-default win-shadow" action='/login' method='post'>
        <span class="mif-vpn-lock mif-4x place-right" style="margin-top: -10px;"></span>
        <h2 class="text-light">Login</h2>
        <hr class="thin mt-4 mb-4 bg-white">
        <div class="form-group">
            <input name='username' type="text" data-role="input" data-prepend="<span class='mif-envelop'>" placeholder="Enter your email..." data-validate="required email">
        </div>
        <div class="form-group">
            <input name='password' type="password" data-role="input" data-prepend="<span class='mif-key'>" placeholder="Enter your password..." data-validate="required minlength=6">
        </div>
        <div class="form-group mt-10">
            <input type="checkbox" data-role="checkbox" data-caption="Remember me" class="place-right">
            <button class="button">Submit form</button>
        </div>
    </form>
    <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script src="https://cdn.metroui.org.ua/v4/js/metro.min.js"></script>
</body>

% include('footer.tpl')
