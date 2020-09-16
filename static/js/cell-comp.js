ಠᴥಠ = {
    $cell: true,
    id: "net",
    $type: "div",
    $components: [
    {
        $type: "div",
        $components: [
            { $type: "span", $text: "GET http://n-gate.com/hackernews/2018/06/ HTTP/1.1"},
            { $type: "span", $text: "80"}
        ]
    },
    ],
    $init: function(){
    }
}

Metro.notify.create('tableBody initialized', "Bounce", {});
$('#t1').data('table').setData(captureData);
