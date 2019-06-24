<div data-role="appbar" data-expand-point="md">
    <a href="/" class="brand no-hover">
        <span style="width: 55px;" class="p-2 border bd-dark border-radius">
            % include('logo', width='35px', height='15px')
        </span>
    </a>
    <a href="/" class='brand no-hover sharkTitle'>sharkpen</a>
    <ul class="app-bar-menu">
        % if defined('site'):
        <li>
            <a href="#" class="dropdown-toggle">Scans</a>
            <ul class="d-menu" data-role="dropdown">
                <li><a href="#">SQL inject</a></li>
                <li><a href="#">Find files</a></li>
                <li class="divider bg-lightGray"></li>
                <li><a href="/home">Scan endpoints</a></li>
            </ul>
        </li>
        <li><a href="#">Notes</a></li>
        <li><a href="#">Results</a></li>
        % end
        <li><a href="/home">Proxy</a></li>
        <li><a href="/test">Fuzzing</a></li>
        % if defined('username'):
        <li><a href="/logout">Logout</a></li>
        % end
    </ul>
</div>