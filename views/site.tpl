% include('header.tpl', title='Sh4rkP3n :: Campaign')

<body class="bg-brandColor2">
    % include('appbar.tpl')
    <style>
      .site-page {
        min-width: 100%;
        position: relative;
        left: 20px;
        color: aliceblue;
      }
      .site-title {
        position: relative;
        left: 80px;
        display: none;
      }
      .site-page {
          padding: 80px 80px 0 0;
      }

      @media all and (min-width: 768px) {
        .site-title {
          display: block;
        }
        .site-page {
          padding: 60px 80px 0 0;
        }
      }
    </style>

    <div class="container-fluid site-page">
        <div class="grid">
            <div class="row">
                <div class="cell-sm-full cell-md-half cell-lg-one-third">
                    <h1 class="site-title fg-white">{{ site.name }}</h1>
                    <form action='/site/{{ site.id }}/edit' method='POST'>
                        <div class="form-group">
                            <label>Name</label>
                            <input name='name' type="text"
                                    placeholder="Enter site name"
                                    value='{{ site.name }}'
                                    data-validate="required"/>
                        </div>
                        <div class="form-group">
                            <label>Color&nbsp;</label>
                            <input name='color' type="color"
                                    value='{{ site.color }}'/>
                        </div>
                        <div class="form-group">
                            <label>Notes</label>
                            <textarea name='notes'
                                        data-role="textarea"
                                        data-max-height="25"
                                        placeholder="..notes">{{ site.notes }}</textarea>
                        </div>
                        <div class="form-group">
                            <label data-role="hint"
                                    data-hint-position="right"
                                    data-hint-text="Enter hostname or ip address followed/separated by commas">Targets</label>
                            <input name='targets'
                                type='text'
                                data-role="taginput"
                                data-cls-tag-title="text-bold fg-white"
                                data-cls-tag="bg-olive"
                                data-cls-tag-remover="bg-darkOlive fg-white"
                                value = '{{ site.targets }}'>
                        </div>
                        <div class="form-group">
                            <button type='submit' class="button success">Submit</button>
                            <a href='/' class="button" >Cancel</a>
                        </div>
                    </form>
                </div>
                <div class="cell-md-half cell-lg-two-third">
                    <div data-role="cube" data-cells="16" data-margin="1"></div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script src="https://cdn.metroui.org.ua/v4/js/metro.min.js"></script>

    <div class="bottom-nav pos-absolute">
        <div id='delete1' class="dialog" data-role="dialog">
            <div class="dialog-title">Remove site?</div>
            <div class="dialog-content">
                Remove this project and all its associated data.
            </div>
            <div class="dialog-actions">
                <button class="button js-dialog-close">Cancel</button>
                <button class="button primary js-dialog-close"
                        onclick="location.href='/site/{{ site.id }}/delete';">Delete</button>
            </div>
        </div>
        <button class="button" onclick="Metro.dialog.open('#delete1')" >
            <span class="icon mif-bin"></span>
            <span class="label">Delete</span>
        </button>
    </div>

</footer>
</body>
</html>
