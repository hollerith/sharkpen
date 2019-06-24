% include('header.tpl', title='Sh4rkP3n :: Advanced Adversary Simulations')

<body class="bg-brandColor2">
    % include('appbar.tpl')
    <style>
      .start-screen {
        min-width: 100%;
        position: relative;
        padding-bottom: 20px;
      }
      .start-screen-title {
        position: relative;
        left: 80px;
        display: none;
      }
      [class*=tile-] {
        transform: scale(0.8);
      }
      .tiles-group {
        margin-left: 0;
        margin-top: 50px;
      }
      @media all and (min-width: 768px) {
        .start-screen-title {
          display: block;
        }
        .start-screen {
          padding: 100px 80px 0 0;
        }
        .tiles-group {
          left: 100px;
        }
        .tiles-group {
          margin-left: 80px;
        }
      }
    </style>

    <div class="container-fluid start-screen">
        <h1 class="start-screen-title fg-white">{{ username }}</h1>
        <div class="tiles-area clear">
            <div class="tiles-grid tiles-group size-fs-2 size-sm-3 size-md-5 size-lg-6 fg-white" data-group-title="Sites">
              % for site in sites:
                <a href="/site/{{ site.id }}/edit"
                   data-role="tile"
                   class="fg-white"
                   style='background-color: {{ site.color }} '>
                      <span class="mif-folder icon"></span>
                      <span class="branding-bar">{{ site.name }}</span>
                      <span class="badge-bottom">{{ len(site.targets.split(',')) }}</span>
                </a>
              % end
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script src="https://cdn.metroui.org.ua/v4/js/metro.min.js"></script>

    <style>
        footer {
            position:inherit;
        }
    </style>
    <footer>

        <div class="bottom-nav pos-absolute">
            <button class="button" onclick="location.href='/site/new';" >
                <span class="icon mif-plus"></span>
                <span class="label">Add</span>
            </button>
            <button class="button">
                <span class="icon mif-favorite"></span>
                <span class="label">Favorites</span>
            </button>
            <button class="button">
                <span class="icon mif-search"></span>
                <span class="label">Search</span>
            </button>
        </div>

    </footer>
    </body>
    </html>
