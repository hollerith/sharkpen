<!DOCTYPE html>
<html>
<head>
	<!-- META -->
  <title>Sh4rkP3n Pr0xy</title>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
	<meta name="description" content="" />

	<!-- CSS -->
	<link rel="stylesheet" href="https://cdn.metroui.org.ua/v4/css/metro-all.min.css">
	<!-- FONT -->
  <style>
			@font-face {
				font-family: 'SharkPen';
				src: url('/public/fonts/sharkpen.ttf');
			}
			.sharkTitle {
				font-family: 'SharkPen', 'Georgia', serif;
				font-stretch: extra-expanded;
				font-size: 35px;
			}
  </style>
  <!-- JS -->
  <script type="text/javascript">
      var message;

      var ws = new WebSocket("ws://127.0.0.1:9090/msgq");
      ws.onopen = function() {
          ws.send("Connected with server");
      };

      ws.onmessage = function (evt) {
          var message = JSON.parse(evt.data);
          if (message.type == 'data') {
            tableData.data.push([ message.path, message.port ]);
            $('#t1').data('table').setData(tableData)
            Metro.notify.create(message.path, "Message", {});
          } else {
            Metro.notify.create(message.text, "Incoming", {});
          }
      };

      var tableData = {
        "header": [
          {
            "name": "path",
            "title": "Path",
            "sortable": true,
            "size": 200
          },
          {
            "name": "port",
            "title": "Port",
            "sortable": true,
            "format": "int",
            "size": 60
          }
        ],
        "data": [],
        "footer": []
      }

  </script>
</head>
<body class="bg-brandColor2">
    % include('appbar.tpl')
    <style>
      #cap {
          padding: 20px;
      }

      .proxy-screen {
        min-width: 100%;
        position: relative;
        padding: 5em 1em 1em 1em ;
      }
      .proxy-screen-title {
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
        .proxy-screen-title {
          display: block;
        }
        .proxy-screen {
          padding: 100px 80px;
        }
        .tiles-group {
          left: 100px;
        }
        .tiles-group {
          margin-left: 80px;
        }
      }
    </style>
    <div class="container-fluid proxy-screen">
        <h1 class='proxy-screen-title fg-white'>Network traffic</h1>
        <div id='cap' class='fg-black bg-white'>
          <table id='t1' class="table striped table-border mt-4"
              data-role="table"
              data-rows="5"
              data-rownum="true"
              data-check="true"
              data-check-style="2"
              >
              <thead>
                  <tr>
                    <th data-sortable="true" data-sort-dir="asc">Head</th>
                    <th data-sortable="true" data-format="number">Port</th>
                  </tr>
              </thead>
              <tbody id='tableBody'>

              </tbody>
          </table>
        </div>
        <div id='net'></div>
    </div>

    <div class="bottom-nav pos-absolute">
        <button class="button" onclick="ws.send('Hola todos');" >
            <span class="icon mif-plus"></span>
            <span class="label">Send</span>
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

    <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script src="https://cdn.metroui.org.ua/v4/js/metro.min.js"></script>
  </body>
</html>